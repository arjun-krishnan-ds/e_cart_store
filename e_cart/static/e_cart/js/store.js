document.addEventListener("DOMContentLoaded", () => {

    console.log("🛒 store.js loaded");

    const csrfToken = document.querySelector("meta[name='csrf-token']")?.content;
    if (!csrfToken) {
        console.error("❌ CSRF token missing in meta tag");
        return;
    }

    // --------------------------
    // QUANTITY SELECTOR
    // --------------------------
    const qtyInput = document.getElementById("qty-input");
    const btnMinus = document.querySelector(".btn-minus");
    const btnPlus = document.querySelector(".btn-plus");

    let quantity = parseInt(qtyInput?.value || "1");

    if (qtyInput && btnMinus && btnPlus) {

        btnMinus.addEventListener("click", () => {
            if (quantity > 1) quantity--;
            qtyInput.value = quantity;
        });

        btnPlus.addEventListener("click", () => {
            quantity++;
            qtyInput.value = quantity;
        });
    }

    // --------------------------
    // TOAST
    // --------------------------
    function showToast(message, type = "success") {
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

    // --------------------------
    // UPDATE NAVBAR COUNTER
    // --------------------------
    function updateNavbarCounter(count) {
        const badge = document.getElementById("cart-counter");
        if (badge && typeof count === "number") {
            badge.innerText = count;
        }
    }

    // --------------------------
    // ADD TO CART
    // --------------------------
    const addBtn = document.querySelector(".btn-add-cart");

    if (addBtn) {
        addBtn.addEventListener("click", () => {

            const productId = addBtn.dataset.id;

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
                    updateNavbarCounter(data.cart_count);
                    showToast(`✅ Added ${quantity} item(s) to cart`);
                } else {
                    showToast("❌ Failed to add", "error");
                }
            })
            .catch(err => {
                console.error("Add error:", err);
                showToast("⚠️ Server error", "error");
            });
        });
    }

    // --------------------------
    // BUY NOW
    // --------------------------
    const buyBtn = document.querySelector(".btn-buy-now");

    if (buyBtn) {
        buyBtn.addEventListener("click", () => {

            const productId = buyBtn.dataset.id;

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
                    showToast("❌ Failed to add", "error");
                }
            })
            .catch(() => showToast("⚠️ Server error", "error"));
        });
    }

});
