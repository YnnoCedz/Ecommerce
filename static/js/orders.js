function openModal(productId) {
    document.getElementById('modalProductId').value = productId;
    document.getElementById('ratingModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('ratingModal').style.display = 'none';
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



let currentForm = null;

function showReasonModal(message, form) {
    currentForm = form; // Save the reference to the form
    document.getElementById("reasonModalMessage").textContent = message; // Set modal message
    document.getElementById("reasonModal").style.display = "block"; // Show the modal
}

function closeModal() {
    document.getElementById("reasonModal").style.display = "none"; // Hide the modal
}

// Handle showing/hiding the additional reason textarea
document.addEventListener("DOMContentLoaded", function () {
    const reasonRadios = document.querySelectorAll('input[name="reason"]');
    const additionalReasonField = document.getElementById("additionalReason");

    reasonRadios.forEach((radio) => {
        radio.addEventListener("change", function () {
            additionalReasonField.style.display = this.value === "Other" ? "block" : "none";
        });
    });

    // Handle Submit Button
    document.getElementById("submitReasonButton").addEventListener("click", function () {
        const selectedReason = document.querySelector('input[name="reason"]:checked');
        const additionalReason = additionalReasonField.value.trim();

        if (!selectedReason) {
            alert("Please select a reason.");
            return;
        }

        const hiddenReasonInput = document.createElement("input");
        hiddenReasonInput.type = "hidden";
        hiddenReasonInput.name = "reason";
        hiddenReasonInput.value = selectedReason.value;

        const hiddenAdditionalInput = document.createElement("input");
        hiddenAdditionalInput.type = "hidden";
        hiddenAdditionalInput.name = "additional_reason";
        hiddenAdditionalInput.value = additionalReason;

        currentForm.appendChild(hiddenReasonInput);
        currentForm.appendChild(hiddenAdditionalInput);

        currentForm.submit();
        closeModal();
    });

    // Handle Cancel Button
    document.getElementById("cancelReasonButton").addEventListener("click", closeModal);
});
