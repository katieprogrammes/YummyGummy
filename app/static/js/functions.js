document.addEventListener("DOMContentLoaded", function () {
    // Handle quantity decrease/increase for each cart item
    const decreaseButtons = document.querySelectorAll(".cartminus");
    const increaseButtons = document.querySelectorAll(".cartplus");
    const removeButtons = document.querySelectorAll(".remove");

    // Handle decrease quantity
    document.querySelectorAll(".cartminus").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
    
            const itemId = this.getAttribute("data-cart-item-id");
            const quantitySpan = document.getElementById(`quantity-${itemId}`);
            let quantity = parseInt(quantitySpan.textContent);
    
            if (quantity > 1) {
                quantity--;
                quantitySpan.textContent = quantity;
    
                fetch(`/api/cart/update_quantity/${itemId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ quantity: quantity })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        showSuccessMessage(data.message);
                        updateCartTotal(); // Call function to update cart total
                    }
                })
                .catch(error => console.error("Error:", error));
            } else {
                // Remove item from cart
                fetch(`/api/cart/remove/${itemId}`, {
                    method: "DELETE",
                    headers: { "Content-Type": "application/json" }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        showSuccessMessage(data.message);
                        this.closest(".cart-item").remove();
                        updateCartTotal();
                    }
                })
                .catch(error => console.error("Error:", error));
            }
        });
    });

    //Handle increase quantity
    document.querySelectorAll(".cartplus").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
    
            const itemId = this.getAttribute("data-cart-item-id");
            const quantitySpan = document.getElementById(`quantity-${itemId}`);
            let quantity = parseInt(quantitySpan.textContent);
    
            quantity++;
            quantitySpan.textContent = quantity;
    
            fetch(`/api/cart/update_quantity/${itemId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showSuccessMessage(data.message);
                    updateCartTotal(); // Call function to update cart total
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });
    
    //Deleting Item from Cart
    removeButtons.forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
    
            const itemId = this.getAttribute("data-item-id");
    
            fetch(`/api/cart/remove/${itemId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    return Promise.reject("Error: " + response.statusText);
                }
            })
            .then(data => {
                if (data.message) {
                    showSuccessMessage(data.message);  // Show success message
                    //remove item from DOM
                    this.closest(".cart-item").remove();  // Assumes cart items are wrapped in .cart-item
                } else if (data.error) {
                    showErrorMessage(data.error);  // Show error message
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showErrorMessage("An unexpected error occurred");
            });
        });
    });
    // Add to Cart functionality
    document.getElementById("prodbasket").addEventListener("click", function (event) {
        event.preventDefault();

        const productId = this.getAttribute("data-product-id");
        const quantity = document.getElementById("quantity").textContent;

        // Send the Add to Cart request (POST)
        fetch('/api/cart/add', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",  
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showSuccessMessage(data.message);  // Show success message on successful addition
            } else if (data.error) {
                showErrorMessage(data.error);  // Show error message if any
            }
        })
        .catch(error => console.error("Error:", error));
    });

    //Product Pages Quantity Buttons
    document.getElementById('quantplus').addEventListener("click", function(event) {
        event.preventDefault();
        let quantitySpan = document.getElementById('quantity');
        let quantity = parseInt(quantitySpan.textContent);
        quantity++;
        quantitySpan.textContent = quantity;
    });
    
    document.getElementById('quantminus').addEventListener("click", function(event) {
        event.preventDefault();
        let quantitySpan = document.getElementById('quantity');
        let quantity = parseInt(quantitySpan.textContent);
    
        if (quantity > 1) {
            quantity--;
            quantitySpan.textContent = quantity;
        }
    });
    //Updating Cart Total
    function updateCartTotal() {
        let total = 0;
    
        // Loop through all cart items
        document.querySelectorAll('.cart-item').forEach(item => {
            const quantity = parseInt(item.querySelector('.cartquantitybutton h3').textContent);
            const priceElement = item.querySelector('.item-price');
            const subtotalElement = item.querySelector('.price');
            if (priceElement && subtotalElement) {
                const price = parseFloat(priceElement.textContent.replace("£", ""));
                const subtotal = quantity * price;
                subtotalElement.textContent = `£${subtotal.toFixed(2)}`; // Update subtotal dynamically
                total += subtotal;
            }
        });
    
        // Update total price in the cart
        const totalElement = document.querySelector('#cart-total');
        if (totalElement) {
            totalElement.textContent = `£${total.toFixed(2)}`;
        }
    }
    // Add to Wishlist functionality
    document.getElementById("prodwishadd").addEventListener("click", function (event) {
        event.preventDefault();

        const productId = this.getAttribute("data-product-id");

        // Send the Add to Wishlist request (POST)
        fetch('/api/wishlist/add', {
            method: "POST",
            headers: {
                "Content-Type": "application/json",  
            },
            body: JSON.stringify({
                product_id: productId,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showSuccessMessage(data.message);  // Show success message on successful addition
            } else if (data.error) {
                showErrorMessage(data.error);  // Show error message if any
            }
        })
        .catch(error => console.error("Error:", error));
    });
    
    
    

    // Show success message
function showSuccessMessage(message) {
    showFlashMessage(message, "linear-gradient(90deg, #B8C6F4, #6388EA)");
}

// Show error message
function showErrorMessage(message) {
    showFlashMessage(message, "linear-gradient(90deg, #6388EA, #B8C6F4)");
}

// General function to create and style flash messages
function showFlashMessage(message, background) {
    const alertDiv = document.createElement("div");
    alertDiv.classList.add("custom-flash-message");
    alertDiv.innerText = message;

    // Apply ombre background
    alertDiv.style.background = background;
    alertDiv.style.color = " #10042F";
    alertDiv.style.padding = "10px 20px";
    alertDiv.style.borderRadius = "5px";
    alertDiv.style.fontSize = "24px";
    

    document.body.insertBefore(alertDiv, document.body.firstChild);

    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });

    setTimeout(() => {
        alertDiv.classList.remove("show");
        alertDiv.classList.add("fade");
    }, 4000); // Hide after 4 seconds
}

});

document.addEventListener("DOMContentLoaded", function () {
    const removeButtons = document.querySelectorAll('.wishremove');
    removeButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            const itemId = this.getAttribute("data-item-id");

            // Make DELETE request to the server
            fetch(`/api/wishlist/remove/${itemId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = "/wishlist"; // Force redirect to wishlist page after successful deletion
                } else {
                    console.error("Error with the request");
                }
            })
            .catch(error => {
                console.error("Error:", error);
            });
        });
    });
});


