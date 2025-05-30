
function showPopup(successMessage, errorMessage) {
    if (successMessage) {
        alert(successMessage);
    } else if (errorMessage) {
        alert(errorMessage);
    }
}

// Call this function when the page loads
window.onload = function() {
    const successMessage = document.getElementById("success-message").value;
    const errorMessage = document.getElementById("error-message").value;
    showPopup(successMessage, errorMessage);

};

document.addEventListener("DOMContentLoaded", function() {
    const loginButton = document.getElementById("loginButton");

    loginButton.addEventListener("click", function() {
        window.open("/loginPage", "_blank"); 

    });
});
