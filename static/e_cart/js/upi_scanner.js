const btn = document.getElementById("confirmBtn");
const statusText = document.getElementById("status");

btn.addEventListener("click", function () {
    btn.disabled = true;
    statusText.classList.remove("hidden");
    statusText.innerText = "Verifying payment...";

    setTimeout(() => {
        statusText.innerText = "Payment Successful ✔ Redirecting...";
        setTimeout(() => {
            window.location.href = ORDER_SUCCESS_URL;
        }, 1200);
    }, 2000);
});
