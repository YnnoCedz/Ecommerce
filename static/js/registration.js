
// Password match validation
document.querySelector("form").addEventListener("submit", function (e) {
    const password = document.querySelector('input[name="password"]').value;
    const confirmPassword = document.querySelector('input[name="confirm-password"]').value;

    if (password !== confirmPassword) {
        e.preventDefault();
        alert("Passwords do not match. Please try again.");
    }
});

// Modal handling
var modal = document.getElementById("successModal");
var span = document.getElementsByClassName("close")[0];
span.onclick = function() {
    window.location.href = '/login'; // Redirect to login page
}
window.onclick = function(event) {
    if (event.target == modal) {
        window.location.href = '/login'; // Redirect to login page
    }
}

// Check if registration was successful and display modal
if (document.body.getAttribute("data-success") === "True") {
    modal.style.display = "flex";
}


// ADDRESS
const provinceSelect = document.getElementById('province');
    const municipalitySelect = document.getElementById('city');
    const barangaySelect = document.getElementById('barangay');

    // Load provinces
    function loadProvinces() {
        fetch('https://psgc.gitlab.io/api/provinces')
            .then(response => response.json())
            .then(data => {
                data.forEach(province => {
                    const option = document.createElement('option');
                    option.value = province.code;
                    option.textContent = province.name;
                    provinceSelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading provinces:', error));
    }

    // Load municipalities
    function loadMunicipalities() {
        const provinceCode = provinceSelect.value;

        fetch(`https://psgc.gitlab.io/api/provinces/${provinceCode}/municipalities`)
            .then(response => response.json())
            .then(data => {
                municipalitySelect.innerHTML = '<option value="" disabled selected>Select City</option>';
                data.forEach(municipality => {
                    const option = document.createElement('option');
                    option.value = municipality.code;
                    option.textContent = municipality.name;
                    municipalitySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading municipalities:', error));
    }

    // Load barangays
    function loadBarangays() {
        const municipalityCode = municipalitySelect.value;

        fetch(`https://psgc.gitlab.io/api/municipalities/${municipalityCode}/barangays`)
            .then(response => response.json())
            .then(data => {
                barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
                data.forEach(barangay => {
                    const option = document.createElement('option');
                    option.value = barangay.code;
                    option.textContent = barangay.name;
                    barangaySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading barangays:', error));
    }

    // Event Listeners
    provinceSelect.addEventListener('change', loadMunicipalities);
    municipalitySelect.addEventListener('change', loadBarangays);
    window.onload = loadProvinces;