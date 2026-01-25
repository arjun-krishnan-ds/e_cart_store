from django.urls import path
from . import views

urlpatterns = [

    # ------------------------
    # Product & Cart
    # ------------------------
    path("", views.product_list, name="product_list"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("add-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("update-cart/<int:product_id>/", views.update_cart, name="update_cart"),
    path("remove-cart/<int:product_id>/", views.remove_from_cart, name="remove_cart"),

    # ------------------------
    # Checkout Flow
    # ------------------------
    path("checkout/", views.checkout, name="checkout"),
    path("place-order/", views.place_order, name="place_order"),
    path("process-payment/<int:order_id>/", views.process_payment, name="process_payment"),

    # ------------------------
    # Payments
    # ------------------------
    path("payment/upi/<int:order_id>/", views.upi_payment, name="upi_payment"),
    path("wallet/", views.wallet_page, name="wallet_page"),
    path("wallet/topup/", views.wallet_topup, name="wallet_topup"),
    path("wallet/pay/<int:order_id>/", views.wallet_payment, name="wallet_payment"),
    path("wallet/add-money/", views.wallet_add_money, name="wallet_add_money"),
    path("wallet/processing/", views.wallet_processing, name="wallet_processing"),

    # ------------------------
    # Order Management
    # ------------------------
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("order-tracking/<int:order_id>/", views.order_tracking, name="order_tracking"),
    path("order/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
    path("order/<int:order_id>/return/", views.return_order, name="return_order"),
]
