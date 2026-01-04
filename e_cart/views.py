from django.shortcuts import render
from django.http import JsonResponse
from .models import Category, Product

# Create your views here.

def product_list(request):
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    products = Product.objects.filter(id__isnull=False).select_related('category')
 
    return render(request, 'e_cart/products.html', {
            'categories': categories,
            'products': products
        })
def product_detail(request, id):
    return render(request, 'e_cart/product_detail.html', {'product': product_list})

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1
    request.session['cart'] = cart
    return JsonResponse({'status': 'success', 'cart_count': sum(cart.values())})

def checkout(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0
    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        product.qty = qty
        product.subtotal = qty * product.price
        total += product.subtotal
        products.append(product)
    return render(request, 'e_cart/checkout.html', {'products': products, 'total': total})