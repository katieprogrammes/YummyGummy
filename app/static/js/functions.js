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
                    // Optionally, remove item from DOM
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
            const quantity = parseInt(item.querySelector('.cartquantitybutton h2').textContent);
            const priceElement = item.querySelector('.item-price');
            const subtotalElement = item.querySelector('.price');
            if (priceElement && subtotalElement) {
                const price = parseFloat(priceElement.textContent.replace("£", ""));
                const subtotal = quantity * price;
                subtotalElement.textContent = `£${subtotal.toFixed(2)}`; // Update subtotal dynamically
                total += subtotal;
            }
        });
    
        // Update the total price in the cart
        const totalElement = document.querySelector('#cart-total');
        if (totalElement) {
            totalElement.textContent = `£${total.toFixed(2)}`;
        }
    }

    // Show success message
    function showSuccessMessage(message) {
        const alertDiv = document.createElement('div');
        alertDiv.classList.add('alert', 'alert-success', 'alert-dismissible', 'fade', 'show');
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;

        document.body.insertBefore(alertDiv, document.body.firstChild);

        window.scrollTo({
            top: 0, 
            behavior: 'smooth' 
        });

        setTimeout(() => {
            alertDiv.classList.remove('show');
            alertDiv.classList.add('fade');
        }, 5000);  // Hide after 5 seconds
    }

    // Show error message
    function showErrorMessage(message) {
        const alertDiv = document.createElement('div');
        alertDiv.classList.add('alert', 'alert-danger', 'alert-dismissible', 'fade', 'show');
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `${message} <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`;

        document.body.insertBefore(alertDiv, document.body.firstChild);

        window.scrollTo({
            top: 0, 
            behavior: 'smooth'
        });

        setTimeout(() => {
            alertDiv.classList.remove('show');
            alertDiv.classList.add('fade');
        }, 5000);  // Hide after 5 seconds
    }
});
