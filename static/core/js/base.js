console.log("Base JS loaded successfully");
// Fade in login inputs (Log-in Page)
const loginInputs = document.querySelectorAll('.login-form input, .btn-login');
loginInputs.forEach((el, index) => {
    el.style.opacity = 0;
    el.style.transform = 'translateY(20px)';
    setTimeout(() => {
        el.style.transition = 'all 0.5s ease';
        el.style.opacity = 1;
        el.style.transform = 'translateY(0)';
    }, 200 * index);
});
