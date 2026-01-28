// =========================
// Hero Banner Animation
// =========================
document.addEventListener("DOMContentLoaded", () => {
    const heroContent = document.querySelector('.hero-content');
    if(heroContent){
        heroContent.style.opacity = 0;
        heroContent.style.transform = "translateY(30px)";
        setTimeout(() => {
            heroContent.style.transition = "all 0.8s ease-out";
            heroContent.style.opacity = 1;
            heroContent.style.transform = "translateY(0)";
        }, 300);
    }
});

// =========================
// Product Card Hover Effects
// (additional, optional, can be extended later)
// =========================
const cards = document.querySelectorAll('.cards .card');
cards.forEach(card => {
    card.addEventListener('mouseenter', () => {
        card.style.transform = "translateY(-8px)";
        card.style.boxShadow = "0 20px 50px rgba(2,6,23,0.15)";
    });
    card.addEventListener('mouseleave', () => {
        card.style.transform = "translateY(0)";
        card.style.boxShadow = "0 10px 30px rgba(2,6,23,0.08)";
    });
});
