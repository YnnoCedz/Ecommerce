// function searchProducts() {
//     const query = document.getElementById('search-input').value;

//     if (query.length === 0) {
//         document.getElementById('search-results').style.display = 'none';
//         return;
//     }

//     fetch(`/search?query=${encodeURIComponent(query)}`)
//         .then(response => response.json())
//         .then(data => {
//             const resultsContainer = document.getElementById('search-results');
//             resultsContainer.innerHTML = '';
//             resultsContainer.style.display = 'block';

//             if (data.length > 0) {
//                 data.forEach(product => {
//                     const resultItem = document.createElement('div');
//                     resultItem.classList.add('search-result-item');

//                     resultItem.innerHTML = `
//                         <a href="/product/${product.product_id}" class="result-link">
//                             <img src="/${product.image_path}" alt="${product.product_name}" class="result-image">
//                             <span class="result-text">${product.product_name}</span>
//                         </a>
//                     `;
//                     resultsContainer.appendChild(resultItem);
//                 });
//             } else {
//                 resultsContainer.innerHTML = '<p>No results found.</p>';
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching search results:', error);
//         });
// }



// Filter Functions for Specific Categories


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


function filterBooks(subcategory) {
    window.location.href = `/book-products?subcategory=${subcategory}`;
}
function filterGames(subcategory) {
    window.location.href = `/game-products?subcategory=${subcategory}`;
}
function filterMovies(subcategory) {
    window.location.href = `/movie-products?subcategory=${subcategory}`;
}


function scrollLeft(containerId) {
    const container = document.getElementById(containerId);
    container.scrollBy({
        left: -300, // Adjust scroll distance
        behavior: 'smooth', // Smooth scrolling effect
    });
}

function scrollRight(containerId) {
    const container = document.getElementById(containerId);
    container.scrollBy({
        left: 300, // Adjust scroll distance
        behavior: 'smooth', // Smooth scrolling effect
    });
}






// on sale

function showPage(pageNumber) {
    const pages = document.querySelectorAll('.flash-page');
    pages.forEach((page, index) => {
        if (index === pageNumber - 1) {
            page.style.display = 'block';
        } else {
            page.style.display = 'none';
        }
    });

    // Update active button
    const buttons = document.querySelectorAll('.page-btn');
    buttons.forEach((button, index) => {
        if (index === pageNumber - 1) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// Initialize first page
document.addEventListener('DOMContentLoaded', () => {
    showPage(1);
});

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