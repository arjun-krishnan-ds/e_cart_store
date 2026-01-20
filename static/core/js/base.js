// =========================
// Global JS for E-Cart Core
// =========================

// ---------- Sticky header shadow on scroll ----------
window.addEventListener('scroll', function () {
    const header = document.querySelector('.main-header');
    if (!header) return; // Safety check: do nothing if header doesn't exist

    if (window.scrollY > 10) {
        header.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
    } else {
        header.style.boxShadow = "none";
    }
});

// ---------- Smooth scroll for anchor links ----------
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const targetID = this.getAttribute('href');

        // Skip invalid or dummy links
        if (!targetID || targetID === "#") return;

        const target = document.querySelector(targetID);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// ---------- CSRF token helper ----------
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// Make CSRF token globally accessible
window.csrfToken = getCSRFToken();

// ---------- Optional: global fetch wrapper with CSRF ----------
async function csrfFetch(url, options = {}) {
    options.headers = {
        ...options.headers,
        "X-CSRFToken": window.csrfToken,
        "Content-Type": "application/json"
    };
    return fetch(url, options);
}

// Example usage:
// csrfFetch('/some-url/', { method: 'POST', body: JSON.stringify({ key: 'value' }) })
//     .then(response => response.json())
//     .then(data => console.log(data))
//     .catch(err => console.error(err));
