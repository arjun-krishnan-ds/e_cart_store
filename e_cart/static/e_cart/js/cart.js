document.addEventListener("DOMContentLoaded", () => {
    console.log("🛒 cart.js loaded");

    const csrftoken = document.querySelector("meta[name='csrf-token']")?.content;

    if (!csrftoken) {
        console.error("❌ CSRF token meta tag missing.");
        return;
    }

    // ---------------------------
    // NAVBAR COUNTER
    // ---------------------------
    function updateCartCounter(count) {
        const counter = document.getElementById("cart-counter");
        if (counter) counter.innerText = count;
    }

    // ---------------------------
    // TOAST
    // ---------------------------
    function showToast(message, type = "success") {
        const toast = document.createElement("div");
        toast.className = `cart-toast ${type}`;
        toast.innerText = message;
        document.body.appendChild(toast);

        setTimeout(() => toast.classList.add("show"), 50);
        setTimeout(() => {
            toast.classList.remove("show");
            setTimeout(() => toast.remove(), 300);
        }, 1800);
    }

    // ---------------------------
    // UPDATE ORDER SUMMARY
    // ---------------------------
    function updateSummary(cartCount, cartTotal) {
        const totalItems = document.getElementById("cart-items-count");
        const totalPrice = document.getElementById("cart-total");

        if (totalItems) totalItems.innerText = cartCount;
        if (totalPrice) totalPrice.innerText = Number(cartTotal).toFixed(2);

        updateCartCounter(cartCount);
    }

    // ---------------------------
    // EVENT DELEGATION
    // ---------------------------
    document.body.addEventListener("click", (e) => {
        const btn = e.target.closest(".btn-remove-cart, .btn-qty-plus, .btn-qty-minus");
        if (!btn) return;

        const productId = btn.dataset.id;
        if (!productId) return;

        const row = document.getElementById(`cart-row-${productId}`);
        if (!row) return;

        const qtySpan = row.querySelector(".cart-qty");
        const subtotalSpan = row.querySelector(".cart-item-subtotal");

        const currentQty = parseInt(qtySpan.innerText) || 1;
        const currentSubtotal = parseFloat(subtotalSpan.innerText) || 0;

        // ✅ SAFE: avoid divide by zero
        const unitPrice = currentQty ? (currentSubtotal / currentQty) : 0;

        // ==================================================
        // REMOVE (decrement first, delete if reaches 0)
        // ==================================================
        if (btn.classList.contains("btn-remove-cart")) {

            const mode = currentQty > 1 ? "single" : "all";

            fetch(`${REMOVE_CART_URL_PREFIX}${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `mode=${mode}`
            })
            .then(async res => {
                const text = await res.text();
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.error("❌ Invalid JSON from server:", text);
                    throw new Error("Invalid JSON");
                }
            })
            .then(data => {
                if (!data.success) {
                    showToast("❌ Failed to remove item", "error");
                    return;
                }

                // ✅ If item still exists → update qty + subtotal
                if (data.remaining_qty > 0) {
                    const newQty = data.remaining_qty;
                    const newSubtotal = unitPrice * newQty;

                    qtySpan.innerText = newQty;
                    subtotalSpan.innerText = newSubtotal.toFixed(2);

                    showToast("➖ 1 item removed from cart", "success");
                }
                // ✅ If qty became zero → remove row
                else {
                    row.remove();
                    showToast("🗑️ Item removed from cart", "success");
                }

                // ✅ Always update summary
                updateSummary(data.cart_count, data.cart_total);

                // ✅ Empty cart UI
                if (data.cart_count === 0) {
                    const wrapper = document.querySelector(".cart-wrapper");
                    if (wrapper) {
                        wrapper.innerHTML = `
                            <div class="text-center py-5">
                                <h4>🛒 Your cart is empty</h4>
                                <a href="${PRODUCT_LIST_URL}" class="btn btn-primary mt-3">
                                    Continue Shopping
                                </a>
                            </div>
                        `;
                    }
                }
            })
            .catch((err) => {
                console.error(err);
                showToast("⚠️ Network error. Try again.", "error");
            });
        }

        // ==================================================
        // INCREMENT QUANTITY
        // ==================================================
        if (btn.classList.contains("btn-qty-plus")) {

            fetch(`${UPDATE_CART_URL_PREFIX}${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: `qty=${currentQty + 1}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "success") {
                    showToast("❌ Failed to update quantity", "error");
                    return;
                }

                qtySpan.innerText = currentQty + 1;
                subtotalSpan.innerText = Number(data.subtotal).toFixed(2);

                updateSummary(data.cart_count, data.total);
            })
            .catch(() => {
                showToast("⚠️ Network error. Try again.", "error");
            });
        }

        // ==================================================
        // DECREMENT QUANTITY
        // ==================================================
        if (btn.classList.contains("btn-qty-minus")) {
            if (currentQty <= 1) return;

            fetch(`${UPDATE_CART_URL_PREFIX}${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: `qty=${currentQty - 1}`
            })
            .then(res => res.json())
            .then(data => {
                if (data.status !== "success") {
                    showToast("❌ Failed to update quantity", "error");
                    return;
                }

                qtySpan.innerText = currentQty - 1;
                subtotalSpan.innerText = Number(data.subtotal).toFixed(2);

                updateSummary(data.cart_count, data.total);
            })
            .catch(() => {
                showToast("⚠️ Network error. Try again.", "error");
            });
        }

    });
});
