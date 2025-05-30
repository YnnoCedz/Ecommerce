let currentForm = null;
    
// Show confirmation modal
function showModal(form) {
    currentForm = form;
    document.getElementById("confirmationModal").style.display = "flex";
    document.getElementById("modalTitle").textContent = "Confirm Update";
    document.getElementById("modalMessage").textContent = "Are you sure you want to proceed with this update?";
}

// Close confirmation modal
function closeModal() {
    document.getElementById("confirmationModal").style.display = "none";
}

// Show success modal
function showSuccessModal() {
    document.getElementById("successModal").style.display = "flex";
}

// Close success modal
function closeSuccessModal() {
    document.getElementById("successModal").style.display = "none";
}

// Submit update with AJAX and show success message
function submitUpdate() {
    closeModal();

    if (currentForm) {
        // Use AJAX to submit the form without refreshing the page
        const formData = new FormData(currentForm);
        const actionUrl = currentForm.action;

        fetch(actionUrl, {
            method: currentForm.method,
            body: formData
        })
        .then(response => {
            if (response.ok) {
                showSuccessModal(); // Show success modal on successful submission
            } else {
                alert("Failed to update. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        });
    }
}

// Attach the showModal function to each form's submit event
document.querySelectorAll(".settings-form").forEach(form => {
    form.addEventListener("submit", function(event) {
        event.preventDefault(); // Prevent actual form submission
        showModal(this); // Show confirmation modal and pass the form reference
    });
});