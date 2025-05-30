const deleteButtons = document.querySelectorAll('.delete-btn');
        
// Function to delete item with confirmation and auto-refresh
deleteButtons.forEach(button => {
    button.addEventListener('click', function() {
        const productId = this.getAttribute('data-id');
        
        // Confirmation prompt before deletion
        if (confirm("Are you sure you want to delete this product?")) {
            fetch(`/delete_product/${productId}`, { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert("Product deleted successfully.");
                        location.reload(); // Reloads the page to update the product list
                    } else {
                        alert("Failed to delete product.");
                    }
                });
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector(".search-bar input");
    const tableRows = document.querySelectorAll("table tbody tr");

    searchInput.addEventListener("input", function () {
        const query = searchInput.value.toLowerCase();

        tableRows.forEach(row => {
            const productNameCell = row.querySelector("td:nth-child(3)");
            const productName = productNameCell ? productNameCell.textContent.toLowerCase() : "";

            if (productName.includes(query)) {
                row.style.display = ""; // Show row
            } else {
                row.style.display = "none"; // Hide row
            }
        });
    });
});


