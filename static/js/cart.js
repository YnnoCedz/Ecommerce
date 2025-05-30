const selectAllCheckbox = document.getElementById('select-all');
const itemCheckboxes = document.querySelectorAll('.select-item');
const totalPriceLabel = document.getElementById('total-price');
const checkoutForm = document.getElementById('checkout-form');
const deleteButtons = document.querySelectorAll('.delete-btn');
const quantityInputs = document.querySelectorAll('.quantity-input');
const decreaseButtons = document.querySelectorAll('.quantity-decrease');
const increaseButtons = document.querySelectorAll('.quantity-increase');

let totalPrice = 0;


function recalculateTotal() {
    totalPrice = 0;

    itemCheckboxes.forEach(item => {
        if (item.checked) {
            const quantityInput = document.querySelector(`.quantity-input[data-id="${item.dataset.id}"]`);
            const quantity = parseInt(quantityInput.value) || 1;  // Default to 1 if quantity is invalid
            const pricePerItem = parseFloat(item.dataset.price);
            totalPrice += pricePerItem * quantity;  // Add to total price
        }
    });

    totalPriceLabel.textContent = `${totalPrice.toFixed(2)}`; // Update the total price label
}

function updateQuantity(cartId, newQuantity) {
    const checkedItems = Array.from(document.querySelectorAll('input[name="selected_items[]"]:checked'))
                               .map(checkbox => checkbox.value); // Store the IDs of the checked items

    fetch(`/update_quantity/${cartId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQuantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            localStorage.setItem('checkedItems', JSON.stringify(checkedItems)); // Store checked items
            location.reload(); // Reload the page
        } else {
            alert('Failed to update quantity.');
        }
    });
}
function validateStockWithModal() {
    let isValid = true;
    const errorMessages = [];

    itemCheckboxes.forEach(item => {
        if (item.checked) {
            const stock = parseInt(item.dataset.quantity); // Available stock
            const quantityInput = document.querySelector(`.quantity-input[data-id="${item.dataset.id}"]`);
            const quantity = parseInt(quantityInput.value);

            if (quantity > stock) {
                isValid = false;
                errorMessages.push(`Product "${item.dataset.productName}" exceeds stock! Available: ${stock}, Selected: ${quantity}`);
            }
        }
    });

    if (!isValid) {
        showModal(errorMessages.join('<br>'));
    }

    return isValid;
}
function showModal(message) {
    const modal = document.getElementById('validation-modal');
    const modalMessage = document.getElementById('modal-message');
    modalMessage.innerHTML = message; // Allow HTML for line breaks
    modal.style.display = 'block';
}
function closeModal() {
    const modal = document.getElementById('validation-modal');
    modal.style.display = 'none';  // Close the modal
}

// Close the modal when the close button is clicked
document.querySelector('.close-btn').addEventListener('click', closeModal);

// Close the modal when clicking outside the modal content
window.addEventListener('click', (event) => {
    if (event.target === document.getElementById('validation-modal')) {
        closeModal();
    }
});
selectAllCheckbox.addEventListener('change', function () {
    itemCheckboxes.forEach(item => {
        item.checked = selectAllCheckbox.checked;
    });
    recalculateTotal(); // Update total price
});
itemCheckboxes.forEach(item => {
    item.addEventListener('change', recalculateTotal);
});
deleteButtons.forEach(button => {
    button.addEventListener('click', function() {
        const cartId = this.getAttribute('data-id');
        fetch(`/delete_item/${cartId}`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const row = document.querySelector(`tr[data-id="${cartId}"]`);
                    if (row) row.remove();
                    recalculateTotal(); // Recalculate the total after removal
                } else {
                    alert('Failed to delete item.');
                }
            });
    });
});
quantityInputs.forEach(input => {
    input.addEventListener('change', function() {
        const cartId = this.getAttribute('data-id');
        const newQuantity = parseInt(this.value);
        if (newQuantity > 0) {
            updateQuantity(cartId, newQuantity);
        } else {
            this.value = 1;  // Set minimum quantity to 1
        }
    });
});

increaseButtons.forEach(button => {
    button.addEventListener('click', function() {
        const input = this.previousElementSibling;
        const cartId = input.getAttribute('data-id');
        const newQuantity = parseInt(input.value) + 1;
        input.value = newQuantity;
        updateQuantity(cartId, newQuantity);
    });
});

decreaseButtons.forEach(button => {
    button.addEventListener('click', function() {
        const input = this.nextElementSibling;
        const cartId = input.getAttribute('data-id');
        const newQuantity = Math.max(parseInt(input.value) - 1, 1);
        input.value = newQuantity;
        updateQuantity(cartId, newQuantity);
    });
});
checkoutForm.onsubmit = function (e) {
    e.preventDefault(); // Prevent form submission

    const checkboxes = document.querySelectorAll('input[name="selected_items[]"]:checked');
    if (checkboxes.length === 0) {
        alert('Please select at least one item to proceed to checkout.');
    } else if (!validateStockWithModal()) {
        // Prevent form submission if stock validation fails
    } else {
        const formData = new FormData(checkoutForm);
        
        // Create an AbortController instance to manage the timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000); // Timeout after 3 seconds

        fetch('/proceedCheckout', {
            method: 'POST',
            body: formData,
            signal: controller.signal  // Attach the abort signal to the fetch request
        })
        .then(response => response.json())
        .then(data => {
            clearTimeout(timeoutId);  // Clear the timeout if the request completes in time

            if (data.success) {
                window.location.href = data.redirect;
            } else {
                if (data.invalid_items) {
                    const messages = data.invalid_items.map(item => 
                        `Product "${item.product_name}" exceeds Available stock!`
                    ).join('<br>');
                    showModal(messages);
                } else if (data.message) {
                    showModal(data.message);
                }
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);  // Clear the timeout in case of error

            // Check if the error was due to the fetch being aborted
            if (error.name === 'AbortError') {
                showModal('Request timed out. Please try again later.');
            } else {
                showModal('An unexpected error occurred. Please try again later.');
            }
        });
    }
};

// Restore checked checkboxes after page reload
window.addEventListener('load', () => {
    const checkedItems = JSON.parse(localStorage.getItem('checkedItems')) || [];

    checkedItems.forEach(cartId => {
        const checkbox = document.querySelector(`input[name="selected_items[]"][value="${cartId}"]`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
});



//modal for about us
function openAboutUsModal() {
    document.getElementById('aboutUsModal').style.display = 'block';
}

function closeAboutUsModal() {
    document.getElementById('aboutUsModal').style.display = 'none';
}

// Close modal when clicking outside the modal content
window.onclick = function(event) {
    const aboutModal = document.getElementById('aboutUsModal');
    if (event.target == aboutModal) {
        aboutModal.style.display = 'none';
    }
}
//modal for FAQs
function openFAQsModal() {
    document.getElementById('faqsModal').style.display = 'block';
}

function closeFAQsModal() {
    document.getElementById('faqsModal').style.display = 'none';
}

// Close modal when clicking outside the modal content
window.onclick = function(event) {
    const faqsModal = document.getElementById('faqsModal');
    if (event.target == faqsModal) {
        faqsModal.style.display = 'none';
    }
}