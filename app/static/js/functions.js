document.addEventListener("DOMContentLoaded", function () {
    const decreaseButtons = document.querySelectorAll(".cartminus");
    const increaseButtons = document.querySelectorAll(".cartplus");
    const removeButtons = document.querySelectorAll(".remove");

    //Handle Decrease Quantity
    document.querySelectorAll(".cartminus").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
    
            const itemId = this.getAttribute("data-cart-item-id");
            const quantitySpans = document.querySelectorAll(`.quantity-${itemId}`);
            let quantity = parseInt(quantitySpans[0].textContent);
    
            if (quantity > 1) {
                quantity--;
    
                quantitySpans.forEach(span => span.textContent = quantity);
    
                fetch(`/api/cart/update_quantity/${itemId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ quantity: quantity })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.message) {
                        showSuccessMessage(data.message);
                        updateCartTotal();
                    }
                })
                .catch(error => console.error("Error:", error));
            } else {
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
    
    document.querySelectorAll(".cartplus").forEach(button => {
        button.addEventListener("click", function(event) {
            event.preventDefault();
    
            const itemId = this.getAttribute("data-cart-item-id");
            console.log(`Looking for .quantity-${itemId}`);
    
            const quantitySpans = document.querySelectorAll(`.quantity-${itemId}`);
    
            if (quantitySpans.length === 0) {
                console.error(`Elements with class .quantity-${itemId} not found.`);
                return;
            }
    
            let quantity = parseInt(quantitySpans[0].textContent);
            quantity++;
    
            quantitySpans.forEach(span => span.textContent = quantity);
    

            fetch(`/api/cart/update_quantity/${itemId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.message) {
                    showSuccessMessage(data.message);
                    updateCartTotal();
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
                    showSuccessMessage(data.message);
                    this.closest(".cart-item").remove();
                } else if (data.error) {
                    showErrorMessage(data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                showErrorMessage("An unexpected error occurred");
            });
        });
    });
    // Addding to Cart
    document.getElementById("prodbasket").addEventListener("click", function (event) {
        event.preventDefault();

        const productId = this.getAttribute("data-product-id");
        const quantity = document.getElementById("quantity").textContent;

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
                showSuccessMessage(data.message);
            } else if (data.error) {
                showErrorMessage(data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    // Addding to Cart on Midsize Screens
    document.getElementById("prodbasketmid").addEventListener("click", function (event) {
        event.preventDefault();

        const productId = this.getAttribute("data-product-id");
        const quantity = document.getElementById("quantity").textContent;

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
                showSuccessMessage(data.message);
            } else if (data.error) {
                showErrorMessage(data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    //Product Page Quantity Buttons
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

    //Updating Cart Function
    function updateCartTotal() {
        let total = 0;
    

        document.querySelectorAll('.cart-item').forEach(item => {
            const quantity = parseInt(item.querySelector('.cartquantitybutton h3').textContent);
            const priceElement = item.querySelector('.item-price');
            const subtotalElement = item.querySelector('.price');
            if (priceElement && subtotalElement) {
                const price = parseFloat(priceElement.textContent.replace("£", ""));
                const subtotal = quantity * price;
                subtotalElement.textContent = `£${subtotal.toFixed(2)}`;
                total += subtotal;
            }
        });
    
        //Updating Total Price
        const totalElement = document.querySelector('#cart-total');
        if (totalElement) {
            totalElement.textContent = `£${total.toFixed(2)}`;
        }
    }

    //Add to Wishlist
    document.getElementById("prodwishadd").addEventListener("click", function (event) {
        event.preventDefault();

        const productId = this.getAttribute("data-product-id");

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
                showSuccessMessage(data.message);
            } else if (data.error) {
                showErrorMessage(data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    //Add to Wishlist on midscreens
    document.getElementById("prodwishaddmid").addEventListener("click", function (event) {
        event.preventDefault();

        const productId = this.getAttribute("data-product-id");

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
                showSuccessMessage(data.message);
            } else if (data.error) {
                showErrorMessage(data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    });
    
    
    

    //Show Success Flash
    function showSuccessMessage(message) {
        showFlashMessage(message, "linear-gradient(90deg, #B8C6F4, #6388EA)");
    }

    //Show Error Flash
    function showErrorMessage(message) {
        showFlashMessage(message, "linear-gradient(90deg, #6388EA, #B8C6F4)");
    }

    //Creating and Styling Flash Messages
    function showFlashMessage(message, background) {
        const alertDiv = document.createElement("div");
        alertDiv.classList.add("custom-flash-message");
        alertDiv.innerText = message;

        //Applying an Ombre Background
        alertDiv.style.background = background;
        alertDiv.style.color = " #10042F";
        alertDiv.style.padding = "10px 20px";
        alertDiv.style.borderRadius = "5px";
        alertDiv.style.fontSize = "24px";
        
        //Positioning
        alertDiv.style.position = "fixed";
        alertDiv.style.top = "80px";
        alertDiv.style.left = "50%";
        alertDiv.style.transform = "translateX(-50%)";
        alertDiv.style.zIndex = "1000";
        alertDiv.style.width = "100%";

        document.body.insertBefore(alertDiv, document.body.firstChild);

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

        setTimeout(() => {
            alertDiv.classList.remove("show");
            alertDiv.classList.add("fade");
        }, 4000);
    }

});

document.addEventListener("DOMContentLoaded", function () {
    const removeButtons = document.querySelectorAll('.wishremove');
    //Removing from Wishlist
    removeButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            const itemId = this.getAttribute("data-item-id");

            fetch(`/api/wishlist/remove/${itemId}`, {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = "/wishlist";
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

document.addEventListener("DOMContentLoaded", function () {
    // Handling Vitamin Dropdown
    document.querySelectorAll('#vitaminDropdown .dropdown-item').forEach(item => {
        item.addEventListener('click', function() {
            let selectedVitamin = this.getAttribute('data-value');
            document.getElementById('selected-vitamin').value = selectedVitamin;
            document.getElementById('vitaminDropdown').textContent = `Vitamin: ${selectedVitamin}`;
            let vitaminDropdownMenu = document.querySelector('#vitaminDropdown + .dropdown-menu');
            vitaminDropdownMenu.classList.remove('show');
        });
    });

    //Handling Flavour Dropdown
    document.querySelectorAll('#flavourDropdown .dropdown-item').forEach(item => {
        item.addEventListener('click', function() {
            let selectedFlavour = this.getAttribute('data-value');
            document.getElementById('selected-flavour').value = selectedFlavour;
            document.getElementById('flavourDropdown').textContent = `Flavour: ${selectedFlavour}`;
            let flavourDropdownMenu = document.querySelector('#flavourDropdown + .dropdown-menu');
            flavourDropdownMenu.classList.remove('show');
        });
    });

    // Handling Sort Dropdown
    const dropdownItems = document.querySelectorAll(".dropdown-item");
    const dropdownButton = document.querySelector(".custom-dropdown");
    const selectedSortInput = document.getElementById("selected-sort");

    
    const currentSort = selectedSortInput.value;
    if (currentSort) {
        dropdownItems.forEach(item => {
            if (item.getAttribute("data-value") === currentSort) {
                dropdownButton.textContent = item.textContent;
            }
        });
    }

    dropdownItems.forEach(item => {
        item.addEventListener("click", function (e) {
            e.preventDefault();
            const selectedValue = this.getAttribute("data-value");
            dropdownButton.textContent = this.textContent;
            selectedSortInput.value = selectedValue;
        });
    });

    

    //Clear Filter Button
    document.getElementById("clearfilter").addEventListener("click", function(e) {
        e.preventDefault();
        const url = new URL(window.location.href);
        url.searchParams.delete("vitamin");
        url.searchParams.delete("flavour");
        url.searchParams.delete("price_min");
        url.searchParams.delete("price_max");
        window.location.href = url.toString();
    });
});



