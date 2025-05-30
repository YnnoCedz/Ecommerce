document.addEventListener('DOMContentLoaded', function () {
    const categories = {
        books: ['Adventure', 'Autobiography', 'Fantasy', 'History', 'Sci-fi', 'Psychology', 'Philosophy', 'Romance', 'Thriller'],
        games: ['Action', 'Adventure', 'Horror', 'Simulation', 'Sport', 'RPG'],
        movies: ['Action', 'Animation', 'Comedy', 'Drama', 'Horror', 'Romance']
    };

    const categorySelect = document.getElementById('category');
    const subcategoryContainer = document.getElementById('subcategory-container');
    let selectedSubcategories = [];

    // Load selected subcategories from server-rendered template
    try {
        selectedSubcategories = JSON.parse('{{ product["subcategory"] | tojson }}');
    } catch (error) {
        console.error('Error parsing selected subcategories:', error);
    }

    // Function to update the subcategories
    function updateSubcategories() {
        const selectedCategory = categorySelect.value;
        subcategoryContainer.innerHTML = ''; // Clear the container

        if (categories[selectedCategory]) {
            categories[selectedCategory].forEach(subcat => {
                const label = document.createElement('label');
                label.className = 'checkbox-label';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.name = 'subcategory';
                checkbox.value = subcat;

                // Check the box if it was previously selected
                if (selectedSubcategories.includes(subcat)) {
                    checkbox.checked = true;
                }

                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(subcat));
                subcategoryContainer.appendChild(label);
            });
        }
    }

    // Initialize the subcategories when the page loads
    updateSubcategories();

    // Update subcategories when the category changes
    categorySelect.addEventListener('change', updateSubcategories);

    const form = document.getElementById('editProductForm');
    const errorModal = document.getElementById('errorModal');
    const modalErrorMessage = document.getElementById('modalErrorMessage');
    const closeErrorModal = document.getElementById('closeErrorModal');
    const dismissErrorModal = document.getElementById('dismissErrorModal');
    const confirmModal = document.getElementById('confirmModal');
    const confirmYesBtn = document.getElementById('confirmYesBtn');
    const confirmCancelBtn = document.getElementById('confirmCancelBtn');

    // Validate form before showing confirmation modal
    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const productName = document.getElementById('product_name').value.trim();
        const description = document.getElementById('product_description').value.trim();
        const price = document.getElementById('product_price').value.trim();
        const selectedCategory = categorySelect.value;
        const subcategories = Array.from(subcategoryContainer.querySelectorAll('input[type="checkbox"]:checked'));

        if (!productName || !description || !price || !selectedCategory || subcategories.length === 0) {
            modalErrorMessage.textContent = "Please fill out all required fields and select at least one subcategory.";
            errorModal.style.display = 'block';
            return;
        }

        // Show confirmation modal
        confirmModal.style.display = 'block';
    });

    // Confirm update action
    confirmYesBtn.addEventListener('click', function () {
        confirmModal.style.display = 'none';
        form.submit(); // Proceed with form submission
    });

    // Cancel update action
    confirmCancelBtn.addEventListener('click', function () {
        confirmModal.style.display = 'none';
        // No further action needed on cancel
    });

    // Close error modal
    closeErrorModal.addEventListener('click', () => errorModal.style.display = 'none');
    dismissErrorModal.addEventListener('click', () => errorModal.style.display = 'none');
});


function previewNewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const previewImage = document.getElementById('preview-image');
            previewImage.src = e.target.result; // Update the image src with the new file's data URL
        };
        reader.readAsDataURL(file);
    }
}