document.addEventListener("DOMContentLoaded", () => {

  const productContainer = document.querySelector(".row.g-4");

  if (!productContainer) return;

  // ===============================
  // CSRF TOKEN HELPER
  // ===============================
  function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.content;
  }

  // ===============================
  // ADD TO CART (EVENT DELEGATION)
  // ===============================
  productContainer.addEventListener("click", (e) => {
    const button = e.target.closest(".btn-add-cart");
    if (!button) return;

    console.log("BUTTON CLICKED", button);

    const productId = button.dataset.id;
    if (!productId) return;

    button.disabled = true;
    button.innerText = "Adding...";

    fetch(`/store/add-cart/${productId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    })

      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          if (data.cart_count !== undefined) {
            const counter = document.getElementById("cart-counter");
            if (counter) {
              counter.innerText = data.cart_count;
            }
          }

        }
      })
      .catch(err => console.error("Fetch error:", err))
      .finally(() => {
        button.disabled = false;
        button.innerText = "Add to Cart";
      });
  });


  // ===============================
  // CATEGORY TOGGLE
  // ===============================
  document.querySelectorAll(".category-title").forEach(title => {
    title.addEventListener("click", () => {
      const list = title.nextElementSibling;
      if (!list) return;
      list.classList.toggle("show");
    });
  });


  // ===============================
  // CATEGORY SEARCH
  // ===============================
  const searchInput = document.getElementById("categorySearch");

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      const value = searchInput.value.toLowerCase();

      document.querySelectorAll(".category-group").forEach(group => {
        const text = group.innerText.toLowerCase();
        group.style.display = text.includes(value) ? "block" : "none";
      });
    });
  }

});
