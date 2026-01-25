from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Product, Order, OrderItem, Wallet, WalletTransaction
from .serializers import (
    ProductSerializer,
    OrderSerializer,
    OrderItemSerializer,
    WalletSerializer,
    WalletTransactionSerializer,
)

# -------------------- CART APIs --------------------
class CartViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = request.session.get('cart', {})
        cart_items = []
        for product_id, qty in cart.items():
            product = get_object_or_404(Product, id=product_id)
            cart_items.append({
                'product': ProductSerializer(product).data,
                'quantity': qty,
                'total_price': qty * float(product.price)
            })
        return Response(cart_items)

class AddToCartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = str(request.data.get('product_id'))
        quantity = int(request.data.get('quantity', 1))
        cart = request.session.get('cart', {})
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
        request.session['cart'] = cart
        return Response({'message': 'Product added to cart', 'cart': cart}, status=status.HTTP_200_OK)

class UpdateCartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, product_id):
        quantity = int(request.data.get('quantity', 1))
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)] = quantity
            request.session['cart'] = cart
            return Response({'message': 'Cart updated', 'cart': cart})
        return Response({'error': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)

class RemoveFromCartAPI(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart
            return Response({'message': 'Product removed from cart', 'cart': cart})
        return Response({'error': 'Product not in cart'}, status=status.HTTP_404_NOT_FOUND)

# -------------------- ORDER APIs --------------------
class PlaceOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        address = request.data.get('address')
        payment_method = request.data.get('payment_method')
        cart = request.session.get('cart', {})

        if not cart:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=user, address=address, payment_method=payment_method, total_amount=0)
        total = 0
        for pid, qty in cart.items():
            product = get_object_or_404(Product, id=pid)
            price = product.price * qty
            total += price
            OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)
        order.total_amount = total
        order.save()

        request.session['cart'] = {}  # clear cart
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderDetailAPI(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

class CancelOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        order = get_object_or_404(Order, id=id, user=request.user)
        if order.status in ['DELIVERED', 'CANCELLED']:
            return Response({'error': 'Cannot cancel this order'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'CANCELLED'
        order.cancel_reason = request.data.get('reason', 'No reason provided')
        order.save()
        return Response({'message': 'Order cancelled', 'order': OrderSerializer(order).data})

class ReturnOrderAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        order = get_object_or_404(Order, id=id, user=request.user)
        if order.status != 'DELIVERED':
            return Response({'error': 'Cannot return before delivery'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'RETURNED'
        order.return_reason = request.data.get('reason', 'No reason provided')
        order.save()
        return Response({'message': 'Order returned', 'order': OrderSerializer(order).data})

# -------------------- WALLET APIs --------------------
class WalletViewAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        transactions = wallet.transactions.all()
        return Response({
            'balance': wallet.balance,
            'transactions': WalletTransactionSerializer(transactions, many=True).data
        })

class WalletTopupAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        amount = Decimal(request.data.get('amount', 0))
        wallet.balance += amount
        wallet.save()
        WalletTransaction.objects.create(wallet=wallet, amount=amount, transaction_type='CREDIT', source='BANK')
        return Response({'balance': wallet.balance, 'message': 'Wallet topped up successfully'})

class WalletPayAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if wallet.balance < order.total_amount:
            return Response({'error': 'Insufficient wallet balance'}, status=status.HTTP_400_BAD_REQUEST)
        wallet.balance -= order.total_amount
        wallet.save()
        WalletTransaction.objects.create(wallet=wallet, amount=order.total_amount, transaction_type='DEBIT', source='ORDER', order=order)
        order.status = 'PLACED'
        order.save()
        return Response({'message': 'Order paid with wallet', 'order': OrderSerializer(order).data})
