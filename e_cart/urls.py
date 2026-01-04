from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", views.product_list, name="products"),
    path("store/product/<int:id>/", views.product_detail, name="p-details"),
    path("add-to-cart/<int:product_id>/", views.add_to_cart, name="add-cart"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="e_cart/password_reset.html"
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="e_cart/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="e_cart/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="e_cart/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
