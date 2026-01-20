// =========================
// Password Show/Hide Toggle
// =========================
document.addEventListener("DOMContentLoaded", () => {
    const passwordFields = document.querySelectorAll('input[type="password"]');

    passwordFields.forEach(field => {
        // Create toggle button
        const toggle = document.createElement('span');
        toggle.innerHTML = '👁';
        toggle.style.cursor = 'pointer';
        toggle.style.position = 'absolute';
        toggle.style.right = '12px';
        toggle.style.top = '50%';
        toggle.style.transform = 'translateY(-50%)';
        toggle.style.fontSize = '0.9rem';
        toggle.style.color = '#64748b';

        // Position parent relatively
        field.parentNode.style.position = 'relative';
        field.parentNode.appendChild(toggle);

        toggle.addEventListener('click', () => {
            if(field.type === 'password'){
                field.type = 'text';
                toggle.innerHTML = '🙈';
            } else {
                field.type = 'password';
                toggle.innerHTML = '👁';
            }
        });
    });
});
