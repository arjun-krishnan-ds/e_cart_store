from django.urls import path
from .api_views import (
    CartViewAPI, AddToCartAPI, UpdateCartAPI, RemoveFromCartAPI,
    PlaceOrderAPI, OrderDetailAPI, CancelOrderAPI, ReturnOrderAPI,
    WalletViewAPI, WalletTopupAPI, WalletPayAPI
)

urlpatterns = []

urlpatterns += [
    # Cart
    path('cart/', CartViewAPI.as_view(), name='api_cart'),
    path('cart/add/', AddToCartAPI.as_view(), name='api_cart_add'),
    path('cart/update/<int:product_id>/', UpdateCartAPI.as_view(), name='api_cart_update'),
    path('cart/remove/<int:product_id>/', RemoveFromCartAPI.as_view(), name='api_cart_remove'),

    # Orders
    path('orders/', PlaceOrderAPI.as_view(), name='api_order_place'),
    path('orders/<int:id>/', OrderDetailAPI.as_view(), name='api_order_detail'),
    path('orders/<int:id>/cancel/', CancelOrderAPI.as_view(), name='api_order_cancel'),
    path('orders/<int:id>/return/', ReturnOrderAPI.as_view(), name='api_order_return'),

    # Wallet
    path('wallet/', WalletViewAPI.as_view(), name='api_wallet'),
    path('wallet/topup/', WalletTopupAPI.as_view(), name='api_wallet_topup'),
    path('wallet/pay/<int:order_id>/', WalletPayAPI.as_view(), name='api_wallet_pay'),
]
