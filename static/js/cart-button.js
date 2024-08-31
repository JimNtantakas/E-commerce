/*
const cart_btn = document.querySelector('.add-to-cart-btn');
document.querySelectorAll('.add-to-cart-btn').forEach(button => {
    button.addEventListener('click', () => {
        const productId = button.getAttribute('data-product-id');
        // Send the product ID to the Flask endpoint using fetch
        fetch("/add-to-cart", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({product_id: productId})
        }).then(response => response.json())
        .then(data => {
            if (!data.success) {
                alert(data.message)
            }
        });
    });
});
*/

const cart_btn = document.querySelector('#unlogged');
cart_btn.addEventListener("click", () => {
    alert("You must be logged in to do this")
});