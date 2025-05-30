function searchItems() {
    const query = document.getElementById('search-input').value;

    if (query.length === 0) {
        document.getElementById('search-results').style.display = 'none';
        return;
    }

    fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultsContainer = document.getElementById('search-results');
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'block';

            const { products, sellers } = data;

            if (products.length > 0 || sellers.length > 0) {
                if (products.length > 0) {
                    const productHeader = document.createElement('h3');
                    productHeader.textContent = 'Products';
                    resultsContainer.appendChild(productHeader);

                    products.forEach(product => {
                        const productItem = document.createElement('div');
                        productItem.classList.add('search-result-item');

                        productItem.innerHTML = `
                            <a href="/product/${product.product_id}" class="result-link">
                                <img src="/${product.image_path}" alt="${product.product_name}" class="result-image">
                                <span class="result-text">${product.product_name}</span>
                            </a>
                        `;
                        resultsContainer.appendChild(productItem);
                    });
                }

                if (sellers.length > 0) {
                    const sellerHeader = document.createElement('h3');
                    sellerHeader.textContent = 'Sellers';
                    resultsContainer.appendChild(sellerHeader);

                    sellers.forEach(seller => {
                        const sellerItem = document.createElement('div');
                        sellerItem.classList.add('search-result-item');

                        sellerItem.innerHTML = `
                            <a href="/shop/${seller.seller_id}" class="result-link">
                                <img src="/${seller.seller_image}" alt="${seller.store_name}" class="result-image">
                                <span class="result-text">${seller.store_name}</span>
                            </a>
                        `;
                        resultsContainer.appendChild(sellerItem);
                    });
                }
            } else {
                resultsContainer.innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}

function showModal() {
    const modal = document.getElementById("addToCartModal");
    modal.style.display = "flex"; // Display as flex for centering
    
    // Automatically close the modal after 1 second
    setTimeout(() => {
        modal.style.display = "none";
    }, 500);
}

// Handle form submission via AJAX
document.getElementById("addToCartForm").onsubmit = async function(event) {
    event.preventDefault(); // Prevent default form submission
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData,
        });

        if (response.ok) {
            showModal(); // Show modal on successful response
        } else {
            alert("Failed to add to cart.");
        }
    } catch (error) {
        console.error("Error adding to cart:", error);
        alert("An error occurred. Please try again.");
    }
};


    function changeQuantity(change) {
    const quantityInput = document.getElementById("quantityInput");
    let currentQuantity = parseInt(quantityInput.value);
    currentQuantity = isNaN(currentQuantity) ? 1 : currentQuantity;
    currentQuantity += change;

    // Ensure quantity is at least 1
    if (currentQuantity < 1) {
        currentQuantity = 1;
    }
    quantityInput.value = currentQuantity;
}

document.getElementById("addToCartForm").onsubmit = async function(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: form.method,
            body: formData,
        });

        if (response.ok) {
            showModal();
        } else {
            alert("Failed to add to cart.");
        }
    } catch (error) {
        console.error("Error adding to cart:", error);
        alert("An error occurred. Please try again.");
    }
};

//modal for privacy policy

function openPrivacyPolicyModal() {
    document.getElementById('privacyPolicyModal').style.display = 'block';
}

function closePrivacyPolicyModal() {
    document.getElementById('privacyPolicyModal').style.display = 'none';
}

// Close modal when clicking outside of the modal content
window.onclick = function(event) {
    const modal = document.getElementById('privacyPolicyModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}


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