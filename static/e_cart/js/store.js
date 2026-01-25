document.addEventListener("DOMContentLoaded", () => {

    console.log("🛒 store.js loaded");

    const csrfMeta = document.querySelector("meta[name='csrf-token']");
    if (!csrfMeta) {
        console.error("❌ CSRF token meta tag missing.");
        return;
    }
    const csrfToken = csrfMeta.content;

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

});
