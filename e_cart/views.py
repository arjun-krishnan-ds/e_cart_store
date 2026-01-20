from django.shortcuts import redirect,render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from .models import Product, Category, Order, OrderItem
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.urls import reverse_lazy


# ===========================
# PRODUCT LISTING / CATEGORY PAGE
# ===========================
def product_list(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related(
        "children"
    )
    category_id = request.GET.get("category")

    products = Product.objects.filter(is_available=True)
    if category_id:
        products = products.filter(category_id=category_id)

    return render(
        request,
        "e_cart/product_list.html",
        {"categories": categories, "products": products},
    )


# ===========================
# PRODUCT DETAIL PAGE
# ===========================
def product_detail(request, id):
    product = get_object_or_404(Product, id=id, is_available=True)
    related_products = Product.objects.filter(category=product.category).exclude(
        id=product.id
    )[:4]

    return render(
        request,
        "e_cart/product_detail.html",
        {"product": product, "related_products": related_products},
    )


# ===========================
# ADD TO CART (AJAX)
# ===========================
@require_POST
def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})

    # Get quantity from POST, default to 1
    try:
        qty = int(request.POST.get("qty", 1))
        if qty < 1:
            qty = 1
    except ValueError:
        qty = 1

    pid = str(product_id)
    # Add the quantity properly
    cart[pid] = cart.get(pid, 0) + qty

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({"status": "success", "cart_count": sum(cart.values())})


def checkout(request):
    cart = request.session.get("cart", {})
    products = []
    total = 0

    for pid, qty in cart.items():
        product = get_object_or_404(Product, id=pid)
        product.qty = qty
        product.subtotal = qty * product.price
        total += product.subtotal
        products.append(product)

    return render(
        request, "e_cart/checkout.html", {"products": products, "total": total}
    )


# ===========================
# VIEW CART
# ===========================
def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0
    cart_count = 0

    for product_id, qty in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            subtotal = product.price * qty

            cart_items.append(
                {"product": product, "quantity": qty, "subtotal": subtotal}
            )

            total += subtotal
            cart_count += qty

        except Product.DoesNotExist:
            pass

    return render(
        request,
        "e_cart/cart.html",
        {
            "cart_items": cart_items,
            "cart_total": total,
            "cart_count": cart_count,
        },
    )


# ===========================
# UPDATE CART QUANTITY (AJAX)
# ===========================
def update_cart(request, product_id):
    if request.method == "POST":
        try:
            qty = int(request.POST.get("qty", 1))
            if qty < 1:
                qty = 1
        except ValueError:
            qty = 1

        cart = request.session.get("cart", {})
        if str(product_id) in cart:
            cart[str(product_id)] = qty
            request.session["cart"] = cart
            request.session.modified = True

            subtotal = get_object_or_404(Product, id=product_id).price * qty
            total = sum(
                get_object_or_404(Product, id=int(pid)).price * q
                for pid, q in cart.items()
            )
            return JsonResponse(
                {"status": "success", "subtotal": subtotal, "total": total}
            )

    return JsonResponse({"status": "error"})


# ===========================
# REMOVE FROM CART (AJAX)
# ===========================
@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    mode = request.POST.get("mode", "all")  # Default removes all

    if product_id in cart:
        if mode == "single":
            # Decrement quantity by 1
            cart[product_id] -= 1
            remaining_qty = cart[product_id]

            # Remove key if quantity is 0
            if remaining_qty <= 0:
                del cart[product_id]
                remaining_qty = 0

        else:
            # Remove entire item
            remaining_qty = 0
            del cart[product_id]

        request.session["cart"] = cart
        request.session.modified = True

        # Recalculate total
        total = 0
        for pid, qty in cart.items():
            try:
                product = Product.objects.get(id=int(pid))
                total += product.price * qty
            except Product.DoesNotExist:
                continue

        return JsonResponse(
            {
                "success": True,
                "remaining_qty": remaining_qty,
                "cart_count": sum(cart.values()),
                "cart_total": round(total, 2),
            }
        )

    return JsonResponse({"success": False, "message": "Item not found in cart"})


# ------------------------
# PLACE ORDER
# ------------------------
@login_required(login_url=reverse_lazy('login'))
def place_order(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    cart = request.session.get("cart", {})
    if not cart:
        return JsonResponse({"success": False, "message": "Your cart is empty."})

    try:
        total_amount = Decimal("0.00")
        order = Order.objects.create(user=request.user, total_amount=0)  # Temporary amount

        for product_id, qty in cart.items():
            product = Product.objects.get(id=product_id)
            quantity = int(qty)
            subtotal = product.price * quantity
            total_amount += subtotal

            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        # Update order total
        order.total_amount = total_amount
        order.status = "COD"  # or "Pending" depending on your flow
        order.save()

        # Clear the cart from session
        request.session["cart"] = {}
        request.session.modified = True

        # Return JSON with redirect URL to confirmation page
        return JsonResponse({
            "success": True,
            "redirect_url": reverse("order_confirmation", args=[order.id])
        })

    except Product.DoesNotExist:
        return JsonResponse({"success": False, "message": "Some products are no longer available."})
    except Exception as e:
        print("Place order error:", e)
        return JsonResponse({"success": False, "message": "Server error. Try again."}, status=500)
# ------------------------
# ORDER CONFIRMATION
# ------------------------
@login_required
def order_confirmation(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, "e_cart/order_confirmation.html", {
            "order": order,
            "order_items": order_items
        })
    except Order.DoesNotExist:
        return redirect("product_list")  # fallback