function showModal(button) {
    const userId = button.getAttribute('data-user-id');
    const action = button.getAttribute('data-action');
    const modal = document.getElementById("confirmationModal");
    const modalText = document.getElementById("modalText");
    const modalForm = document.getElementById("modalForm");

    modalText.textContent = action === 'archive' ? 
        "Are you sure you want to archive this user?" : 
        "Are you sure you want to retrieve this user?";

    modalForm.action = `/toggle_archive/${userId}?action=${action}`;
    modal.style.display = "block";
}

function hideModal() {
    document.getElementById("confirmationModal").style.display = "none";
}