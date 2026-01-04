// Category
document.querySelectorAll('.category-header').forEach(header => {
    header.addEventListener('click', () => {
        const parent = header.parentElement;
        parent.classList.toggle('active');
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const quickViewButtons = document.querySelectorAll('.quick-view-btn');
    const modal = new bootstrap.Modal(document.getElementById('quickViewModal'));

    quickViewButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const card = btn.closest('.product-card');

            // Fill modal with data
            document.getElementById('quickViewTitle').textContent = card.dataset.name;
            document.getElementById('quickViewImage').src = card.dataset.image;
            document.getElementById('quickViewCategory').textContent = card.dataset.category;
            document.getElementById('quickViewDescription').textContent = card.dataset.description;
            document.getElementById('quickViewPrice').textContent = `₹ ${card.dataset.price}`;

            // Add to cart button
            const cartBtn = document.getElementById('quickViewAddToCart');
            cartBtn.dataset.id = card.dataset.id;

            // View Details link
            const detailLink = document.getElementById('quickViewDetailLink');
            detailLink.href = `/products/${card.dataset.id}/`; // Or {% url 'product-detail' product.id %} rendered dynamically

            modal.show();
        });
    });

    // Add to Cart functionality
    document.querySelectorAll('.btn-cart').forEach(btn => {
        btn.addEventListener('click', () => {
            const productId = btn.dataset.id;

            fetch("{% url 'add-to-cart' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify({id: productId})
            })
            .then(res => res.json())
            .then(data => alert(data.message))
            .catch(err => console.error(err));
        });
    });
});

