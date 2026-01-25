// --------------------------
//  ORDER CONFIRMATION
// --------------------------
const form = document.getElementById("paymentForm");
const button = form.querySelector("button");

form.addEventListener("submit", function () {
    button.innerText = "Redirecting...";
});

// --------------------------
//  ORDER SUCCESS
// --------------------------
function downloadInvoice() {
    window.print();
}
// --------------------------
//  ORDER TRACKING
// --------------------------
// Reserved for future live updates or websocket tracking
// --------------------------
//  ORDER CANCEL 
// --------------------------
document.getElementById("cancelForm").addEventListener("submit", function () {
    return confirm("Are you sure you want to cancel this order?");
});
// --------------------------
//  ORDER RETURN
// --------------------------
document.getElementById("returnForm").addEventListener("submit", function () {
    return confirm("Confirm return request?");
});
