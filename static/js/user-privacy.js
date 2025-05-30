document.querySelectorAll('.privacy-setting').forEach(form => {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        openModal(form);
    });
});

function toggleModal(show) {
    document.getElementById('confirmation-modal').style.display = show ? 'block' : 'none';
}

function openModal(form) {
    toggleModal(true);
    document.getElementById('confirm-btn').onclick = () => {
        form.submit();
        toggleModal(false);
    };
}

// Fade out flash messages after 3 seconds
setTimeout(() => {
    document.getElementById('flash-messages')?.classList.add('fade');
}, 100);



function searchProducts() {
    let query = document.getElementById('search-input').value;

    if (query.length === 0) {
        document.getElementById('search-results').style.display = 'none';
        return;
    }

    fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            let resultsContainer = document.getElementById('search-results');
            resultsContainer.innerHTML = '';
            resultsContainer.style.display = 'block';

            if (data.length > 0) {
                data.forEach(product => {
                    let resultItem = document.createElement('div');
                    resultItem.classList.add('search-result-item');

                    // Create a link to the product details page with the product image, name, and price
                    resultItem.innerHTML = `
                        <a href="/product/${product.product_id}">
                            <img src="/${product.image_path}" alt="${product.product_name}">
                            <div>
                                <p><strong>${product.product_name}</strong></p>
                                <p>Php ${product.price}</p>
                            </div>
                        </a>
                    `;

                    resultsContainer.appendChild(resultItem);
                });
            } else {
                resultsContainer.innerHTML = '<p>No results found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching search results:', error);
        });
}



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