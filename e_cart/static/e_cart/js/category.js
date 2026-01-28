document.addEventListener("DOMContentLoaded", () => {

    console.log("📦 category.js loaded");

    const productContainer = document.getElementById("product-container");
    const csrfToken = document.querySelector("meta[name='csrf-token']")?.content;
    const navbarCounter = document.getElementById("cart-counter");

    const categorySearch = document.getElementById("categorySearch");
    const categoryGroups = document.querySelectorAll(".category-group");

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
        }, 2000);
    }

    // ---------------------------
    // CATEGORY DROPDOWN TOGGLE
    // ---------------------------
    categoryGroups.forEach(group => {
        const title = group.querySelector(".category-title");
        const subList = group.querySelector(".subcategory-list");

        if (!title || !subList) return;

        // Hide initially
        subList.style.display = "none";

        title.addEventListener("click", () => {
            const isOpen = subList.style.display === "block";
            subList.style.display = isOpen ? "none" : "block";
        });
    });

    // ---------------------------
    // CATEGORY SEARCH FILTER
    // ---------------------------
    if (categorySearch) {
        categorySearch.addEventListener("input", () => {
            const query = categorySearch.value.toLowerCase().trim();

            categoryGroups.forEach(group => {
                const titleText = group
                    .querySelector(".category-title")
                    .innerText.toLowerCase();

                const subItems = Array.from(group.querySelectorAll(".subcategory-item a")).map(
                    a => a.innerText.toLowerCase()
                );

                // Show group if category name or any subcategory matches query
                const match = titleText.includes(query) || subItems.some(text => text.includes(query));

                group.style.display = match ? "block" : "none";
            });
        });
    }

    // ---------------------------
    // ADD TO CART (unchanged)
    // ---------------------------
    if (productContainer) {
        productContainer.addEventListener("click", (e) => {
            const btn = e.target.closest(".btn-add-cart");
            if (!btn) return;

            const productId = btn.dataset.id;
            if (!productId) return;

            btn.disabled = true;

            fetch(`/store/add-cart/${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    if (navbarCounter) {
                        navbarCounter.innerText = data.cart_count;
                    }
                    showToast("✅ Added to cart");
                }
            })
            .finally(() => btn.disabled = false);
        });
    }

});
