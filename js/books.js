
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


function toggleFiction() {
            const fictionList = document.getElementById('fiction-list');
            fictionList.style.display = fictionList.style.display === 'block' ? 'none' : 'block';
        }

        function toggleNonFiction() {
            const nonfictionList = document.getElementById('nonfiction-list');
            nonfictionList.style.display = nonfictionList.style.display === 'block' ? 'none' : 'block';
        }

        // Initialize genre lists as hidden
        document.getElementById('fiction-list').style.display = 'none';
        document.getElementById('nonfiction-list').style.display = 'none';