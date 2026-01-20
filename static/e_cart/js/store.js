document.addEventListener("DOMContentLoaded", () => {

    console.log("🛒 store.js loaded");

    const csrfToken = document.querySelector("meta[name='csrf-token']").content;

    // --------------------------
    // QUANTITY SELECTOR (Product Detail Page)
    // --------------------------
    const qtyDisplay = document.getElementById("qty-display");
    const btnMinus = document.querySelector(".btn-minus");
    const btnPlus = document.querySelector(".btn-plus");

    let quantity = parseInt(qtyDisplay?.innerText) || 1;

    if (qtyDisplay && btnMinus && btnPlus) {
        btnMinus.addEventListener("click", () => {
            if (quantity > 1) quantity--;
            qtyDisplay.innerText = quantity;
        });

        btnPlus.addEventListener("click", () => {
            quantity++;
            qtyDisplay.innerText = quantity;
        });
    }

    // --------------------------
    // ADD TO CART
    // --------------------------
    const btnAddCart = document.querySelector(".btn-add-cart");
    if (btnAddCart) {
        btnAddCart.addEventListener("click", () => {
            const productId = btnAddCart.dataset.id;
            fetch(`${ADD_CART_URL_PREFIX}${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: `qty=${quantity}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    showToast(`✅ Added ${quantity} item(s) to cart!`, "success");
                    const badge = document.getElementById("cart-counter");
                    if (badge) badge.innerText = data.cart_count;
                } else {
                    showToast(data.message || "⚠️ Failed to add item.", "error");
                }
            })
            .catch(() => showToast("⚠️ Server error. Try again.", "error"));
        });
    }

    // --------------------------
    // BUY NOW
    // --------------------------
    const btnBuyNow = document.querySelector(".btn-buy-now");
    if (btnBuyNow) {
        btnBuyNow.addEventListener("click", () => {
            const productId = btnBuyNow.dataset.id;
            fetch(`${ADD_CART_URL_PREFIX}${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: `qty=${quantity}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    window.location.href = CHECKOUT_URL;
                } else {
                    showToast(data.message || "⚠️ Failed to add item.", "error");
                }
            })
            .catch(() => showToast("⚠️ Server error. Try again.", "error"));
        });
    }

    // --------------------------
    // PLACE ORDER (Checkout Page)
    // --------------------------
    const btnPlaceOrder = document.querySelector(".btn-place-order");
    if (btnPlaceOrder) {
        btnPlaceOrder.addEventListener("click", async () => {
            btnPlaceOrder.disabled = true;
            btnPlaceOrder.innerText = "Placing order...";

            try {
                const res = await fetch(PLACE_ORDER_URL, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "Content-Type": "application/x-www-form-urlencoded",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: ""
                });

                // If redirected (login required), go to login
                if (res.redirected) {
                    window.location.href = res.url;
                    return;
                }

                // Try parsing JSON
                let data;
                try {
                    data = await res.json();
                } catch (err) {
                    // If not JSON, probably login page
                    window.location.href = "/login/?next=" + window.location.pathname;
                    return;
                }

                btnPlaceOrder.disabled = false;
                btnPlaceOrder.innerText = "Place Order";

                // Handle login-required response from backend
                if (data.success === false && data.message === "Login required.") {
                    window.location.href = "/login/?next=" + window.location.pathname;
                    return; // Stop execution so success toast doesn't show
                }

                // Show success toast only if order succeeded
                if (data.success === true) {
                    showToast("✅ Order placed successfully!", "success");
                    setTimeout(() => window.location.href = data.redirect_url, 1500);
                } else if (data.success === false) {
                    showToast(data.message || "⚠️ Failed to place order.", "error");
                }

            } catch (err) {
                btnPlaceOrder.disabled = false;
                btnPlaceOrder.innerText = "Place Order";
                showToast("⚠️ Server error. Try again.", "error");
            }
        });
    }

    // --------------------------
    // TOAST FUNCTION
    // --------------------------
    function showToast(message, type) {
        const toast = document.createElement("div");
        toast.className = `cart-toast ${type}`;
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add("show"), 50);
        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => toast.remove(), 300);
        }, 2200);
    }

});
