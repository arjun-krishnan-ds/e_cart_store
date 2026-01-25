from decimal import Decimal

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from e_cart.models import Product, Category, Order, OrderItem, Wallet


class ECartAPITest(TestCase):

    def setUp(self):
        self.client = Client()

        # -----------------------
        # Create User & Login
        # -----------------------
        self.user = User.objects.create_user(
            username="testuser",
            password="password123"
        )
        self.client.login(username="testuser", password="password123")

        # -----------------------
        # Create Category
        # -----------------------
        self.category = Category.objects.create(
            name="Electronics"
        )

        # -----------------------
        # Create Product
        # -----------------------
        self.product = Product.objects.create(
            name="Laptop",
            category=self.category,
            price=Decimal("200.00"),
            stock=10
        )

        # -----------------------
        # Create Wallet safely
        # -----------------------
        self.wallet, _ = Wallet.objects.get_or_create(
            user=self.user,
            defaults={"balance": Decimal("0.00")}
        )

    # --------------------------------------------------
    # CART TESTS
    # --------------------------------------------------

    def test_add_to_cart(self):
        response = self.client.post(
            "/store/api/cart/add/",
            {"product_id": self.product.id, "quantity": 1},
        )
        self.assertEqual(response.status_code, 200)

    def test_view_cart(self):
        self.client.post(
            "/store/api/cart/add/",
            {"product_id": self.product.id, "quantity": 2},
        )

        response = self.client.get("/store/api/cart/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)

    def test_update_cart(self):
        self.client.post(
            "/store/api/cart/add/",
            {"product_id": self.product.id, "quantity": 1},
        )

        response = self.client.patch(
            f"/store/api/cart/update/{self.product.id}/",
            {"quantity": 3},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_from_cart(self):
        self.client.post(
            "/store/api/cart/add/",
            {"product_id": self.product.id, "quantity": 1},
        )

        response = self.client.delete(
            f"/store/api/cart/remove/{self.product.id}/"
        )
        self.assertEqual(response.status_code, 200)

    # --------------------------------------------------
    # ORDER TESTS
    # --------------------------------------------------

    def test_place_order(self):
        self.client.post(
            "/store/api/cart/add/",
            {"product_id": self.product.id, "quantity": 1},
        )

        response = self.client.post(
            "/store/api/orders/",
            {
                "address": "Test Address",
                "payment_method": "COD"
            }
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(Decimal(data["total_amount"]), Decimal("200.00"))

    def test_cancel_order(self):
        self.client.post(
            "/store/api/cart/add/",
            {"product_id": self.product.id, "quantity": 1},
        )

        order_response = self.client.post(
            "/store/api/orders/",
            {
                "address": "Test Address",
                "payment_method": "COD"
            }
        )

        order_id = order_response.json()["id"]

        cancel_response = self.client.post(
            f"/store/api/orders/{order_id}/cancel/",
            {"reason": "Changed mind"}
        )

        self.assertEqual(cancel_response.status_code, 200)

    def test_return_order(self):
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("200.00"),
            status="DELIVERED",
            payment_method="COD",
            address="Test"
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=Decimal("200.00")
        )

        response = self.client.post(
            f"/store/api/orders/{order.id}/return/",
            {"reason": "Defective"}
        )

        self.assertEqual(response.status_code, 200)

    # --------------------------------------------------
    # WALLET TESTS
    # --------------------------------------------------

    def test_wallet_topup_and_payment(self):

        # ---- Topup Wallet ----
        topup_response = self.client.post(
            "/store/api/wallet/topup/",
            {"amount": "500.00"}
        )

        self.assertEqual(topup_response.status_code, 200)
        self.wallet.refresh_from_db()

        self.assertEqual(self.wallet.balance, Decimal("500.00"))

        # ---- Place Order ----
        self.client.post(
            "/store/api/cart/add/",
            {"product_id": self.product.id, "quantity": 1},
        )

        order_response = self.client.post(
            "/store/api/orders/",
            {
                "address": "Wallet Address",
                "payment_method": "WALLET"
            }
        )

        order_id = order_response.json()["id"]

        # ---- Pay Using Wallet ----
        pay_response = self.client.post(
            f"/store/api/wallet/pay/{order_id}/"
        )

        self.assertEqual(pay_response.status_code, 200)

        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal("300.00"))
