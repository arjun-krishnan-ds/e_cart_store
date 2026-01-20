from django.urls import path
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("add-cart/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart_view, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update-cart/<int:product_id>/", views.update_cart, name="update_cart"),
    path("remove-cart/<int:product_id>/", views.remove_from_cart, name="remove_cart"),
    # ✅ ADD THIS
    path("place-order/", views.place_order, name="place_order"),
    path(
        "order-confirmation/<int:order_id>/",
        views.order_confirmation,
        name="order_confirmation",
    ),
]
