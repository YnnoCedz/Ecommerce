function showModal(button) {
    const sellerId = button.getAttribute('data-seller-id');
    const action = button.getAttribute('data-action');
    const modal = document.getElementById("confirmationModal");
    const modalText = document.getElementById("modalText");
    const modalForm = document.getElementById("modalForm");

    modalText.textContent = action === 'archive' ? 
        "Are you sure you want to archive this seller?" : 
        "Are you sure you want to retrieve this seller?";

    modalForm.action = `/toggle_archived/${sellerId}?action=${action}`;
    modal.style.display = "block";
}



    function hideModal() {
        document.getElementById("confirmationModal").style.display = "none";
    }