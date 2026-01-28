from django.shortcuts import redirect, render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Product, Category, Order, OrderItem, Wallet, WalletTransaction
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.db.models import Q


# ===========================
# PRODUCT LISTING / CATEGORY PAGE
# ===========================
def product_list(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related(
        "children"
    )

    category_id = request.GET.get("category")
    search_query = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_available=True)

    # ---------------------------
    # CATEGORY FILTER
    # ---------------------------
    if category_id:
        selected_category = Category.objects.filter(id=category_id).first()
        if selected_category:
            child_ids = selected_category.children.values_list("id", flat=True)
            products = products.filter(
                Q(category=selected_category) | Q(category_id__in=child_ids)
            )

    # ---------------------------
    # SEARCH FILTER
    # ---------------------------
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    return render(
        request,
        "e_cart/product_list.html",
        {
            "categories": categories,
            "products": products,
            "search_query": search_query,  # optional, if you want to populate search box
            "selected_category_id": int(category_id) if category_id else None,
        },
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
    cart[pid] = cart.get(pid, 0) + qty

    request.session["cart"] = cart
    request.session.modified = True

    # Calculate totals for live update
    total = 0
    for pid, q in cart.items():
        try:
            product = Product.objects.get(id=int(pid))
            total += product.price * q
        except Product.DoesNotExist:
            continue

    return JsonResponse(
        {
            "status": "success",
            "cart_count": sum(cart.values()),
            "cart_total": round(total, 2),
        }
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
@require_POST
def update_cart(request, product_id):
    cart = request.session.get("cart", {})
    pid = str(product_id)

    if pid not in cart:
        return JsonResponse({"status": "error"})

    current_qty = cart.get(pid, 1)

    qty_action = request.POST.get("qty")

    if qty_action == "inc":
        new_qty = current_qty + 1
    else:
        try:
            new_qty = int(qty_action)
            if new_qty < 1:
                new_qty = 1
        except:
            new_qty = current_qty

    cart[pid] = new_qty
    request.session["cart"] = cart
    request.session.modified = True

    product = get_object_or_404(Product, id=product_id)

    subtotal = product.price * new_qty

    total = 0
    for p, q in cart.items():
        try:
            prod = Product.objects.get(id=int(p))
            total += prod.price * q
        except:
            pass

    return JsonResponse(
        {
            "status": "success",
            "qty": new_qty,
            "subtotal": float(subtotal),
            "total": float(total),
            "cart_count": sum(cart.values()),
        }
    )


@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    mode = request.POST.get("mode", "single")  # default to decrement by 1

    if product_id in cart:
        if mode == "single":
            cart[product_id] -= 1
            remaining_qty = cart[product_id]
            if remaining_qty <= 0:
                del cart[product_id]
                remaining_qty = 0
        else:
            remaining_qty = 0
            del cart[product_id]

        request.session["cart"] = cart
        request.session.modified = True

        # Calculate totals
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


@login_required(login_url="/login/")
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    cart_items = []
    total = Decimal("0")

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * qty
        total += subtotal
        cart_items.append({"product": product, "qty": qty, "subtotal": subtotal})

    return render(
        request, "e_cart/checkout.html", {"cart_items": cart_items, "total": total}
    )


@login_required(login_url="/login/")
@transaction.atomic
def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    address = request.POST.get("address")
    cart = request.session.get("cart", {})

    if not cart or not address:
        messages.error(request, "Invalid checkout.")
        return redirect("checkout")

    order = Order.objects.create(user=request.user, address=address, status="PLACED")

    total = Decimal("0")

    for product_id, qty in cart.items():
        product = get_object_or_404(Product, id=product_id)
        OrderItem.objects.create(
            order=order, product=product, quantity=qty, price=product.price
        )
        total += product.price * qty

    order.total_amount = total
    order.save()

    return render(request, "e_cart/order_confirmation.html", {"order": order})


@login_required(login_url="/login/")
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    payment_method = request.POST.get("payment_method")
    order.payment_method = payment_method
    order.save()

    if payment_method == "COD":
        request.session["cart"] = {}
        return redirect("order_success", order_id=order.id)

    if payment_method == "UPI":
        return redirect("upi_payment", order_id=order.id)

    if payment_method == "WALLET":
        return redirect("wallet_payment", order_id=order.id)

    return redirect("order_tracking", order_id=order.id)


@login_required(login_url="/login/")
@transaction.atomic
def wallet_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    if request.method == "POST":
        if wallet.balance < order.total_amount:
            messages.error(request, "Insufficient wallet balance.")
            return redirect("wallet_page")

        wallet.balance -= order.total_amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=order.total_amount,
            transaction_type="DEBIT",
            source="ORDER",
            order=order,
        )

        request.session["cart"] = {}
        return redirect("order_success", order_id=order.id)

    return render(
        request, "e_cart/wallet_payment.html", {"order": order, "wallet": wallet}
    )


@login_required(login_url="/login/")
def wallet_page(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    return render(request, "e_cart/wallet_main.html", {"wallet": wallet})


@login_required(login_url="/login/")
def wallet_add_money(request):
    return render(request, "e_cart/wallet_add_money.html")


@login_required(login_url="/login/")
def wallet_processing(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        bank = request.POST.get("bank")
        account = request.POST.get("account")
        ifsc = request.POST.get("ifsc")

        if not all([amount, bank, account, ifsc]):
            messages.error(request, "All bank fields are required.")
            return redirect("wallet_add_money")

        request.session["wallet_topup_amount"] = amount
        return redirect("wallet_processing")

    return render(request, "e_cart/wallet_processing.html")


@login_required(login_url="/login/")
@transaction.atomic
def wallet_topup(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    amount = request.session.get("wallet_topup_amount")
    if not amount:
        messages.error(request, "Invalid wallet transaction.")
        return redirect("wallet_page")

    amount = Decimal(amount)

    wallet.balance += amount
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet, amount=amount, transaction_type="CREDIT", source="BANK"
    )

    del request.session["wallet_topup_amount"]

    messages.success(request, f"₹{amount} added successfully to your wallet.")
    return redirect("wallet_page")


@login_required(login_url="/login/")
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "e_cart/order_success.html", {"order": order})


@login_required(login_url="/login/")
def order_tracking(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "e_cart/order_tracking.html", {"order": order})


@login_required(login_url="/login/")
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "DELIVERED":
        messages.error(request, "Delivered orders cannot be cancelled.")
        return redirect("order_tracking", order_id=order.id)

    if request.method == "POST":
        order.cancel_reason = request.POST.get("reason")
        order.status = "CANCELLED"
        order.save()
        messages.success(request, "Order cancelled successfully.")
        return redirect("order_tracking", order_id=order.id)

    return render(request, "e_cart/order_cancel.html", {"order": order})


@login_required(login_url="/login/")
def return_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "DELIVERED":
        messages.error(request, "Only delivered orders can be returned.")
        return redirect("order_tracking", order_id=order.id)

    if request.method == "POST":
        order.return_reason = request.POST.get("reason")
        order.status = "RETURNED"
        order.save()
        messages.success(request, "Return initiated successfully.")
        return redirect("order_tracking", order_id=order.id)

    return render(request, "e_cart/order_return.html", {"order": order})


@login_required(login_url="/login/")
def upi_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "e_cart/upi_scanner.html", {"order": order})
