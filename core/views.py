from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from e_cart.models import Product

# Create your views here.


def home(request):
    # Select featured products (latest 6 for "deal of the day")
    featured_products = Product.objects.filter(is_available=True).order_by("-id")[:8]

    return render(request, "core/home.html", {"products": featured_products})


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "core/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "core/signin.html", {"form": form})


@login_required
def dashboard_view(request):
    return render(request, "core/dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")
