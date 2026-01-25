// --------------------------
//  WALLET MAIN
// --------------------------
const form = document.getElementById("topupForm");
const button = form.querySelector("button");

form.addEventListener("submit", () => {
    button.innerText = "Processing...";
});
// --------------------------
//  WALLET PAYMENT
// --------------------------
const btn = document.querySelector(".btn-primary");

if (btn) {
    btn.addEventListener("click", () => {
        btn.innerText = "Processing Payment...";
    });
}

// --------------------------
//  WALLET PROCESSING
// --------------------------
setTimeout(() => {
    window.location.href = "/store/wallet/topup/";
}, 2500);
