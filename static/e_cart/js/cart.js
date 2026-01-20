document.addEventListener("DOMContentLoaded", () => {

    console.log("🛒 cart.js loaded");

    const csrfToken = document.querySelector("meta[name='csrf-token']").content;

    // -------------------------
    // REMOVE ITEM BUTTON
    // -------------------------
    document.querySelectorAll(".btn-remove-cart").forEach(btn => {
        btn.addEventListener("click", () => {
            const productId = btn.dataset.id;
            if (!productId) return;
            removeOneItem(productId, btn);
        });
    });

    function removeOneItem(productId, btn) {
        btn.disabled = true;

        fetch(`${REMOVE_CART_URL_PREFIX}${productId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: "mode=single" // server interprets this as decrement by 1
        })
        .then(res => res.json())
        .then(data => {
            btn.disabled = false;

            if (!data.success) {
                showToast("❌ Unable to update cart", "error");
                return;
            }

            const row = document.getElementById(`cart-row-${productId}`);
            const qtySpan = row?.querySelector(".cart-qty");

            // ✅ Update quantity live
            if (qtySpan) {
                qtySpan.innerText = data.remaining_qty;
            }

            // ✅ Remove row if quantity reaches 0
            if (data.remaining_qty === 0) {
                row?.remove();
            }

            // ✅ Update totals
            const itemsCountElem = document.getElementById("cart-items-count");
            const totalElem = document.getElementById("cart-total");
            if (itemsCountElem) itemsCountElem.innerText = data.cart_count;
            if (totalElem) totalElem.innerText = data.cart_total;

            // ✅ Show empty cart if cart_count = 0
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

            // ✅ Show success toast
            showToast("✅ Item removed successfully", "success");

        })
        .catch(() => {
            btn.disabled = false;
            showToast("⚠️ Server error. Please try again.", "error");
        });
    }

    // -------------------------
    // Toast Notification
    // -------------------------
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
