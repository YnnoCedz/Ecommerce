// // JavaScript to handle modal popup
// document.addEventListener("DOMContentLoaded", function() {
//     const modal = document.getElementById("successModal");
//     const closeModalBtn = document.querySelector(".close");
//     const isSuccess = document.body.getAttribute("data-success") === "true";

//     if (isSuccess) {
//         modal.style.display = "flex"; // Show modal

//         // Redirect to login after a delay or on modal close
//         setTimeout(() => {
//             window.location.href = '/login';
//         }, 3000); // Auto-close after 3 seconds
//     }

//     // Close modal manually when "x" is clicked
//     closeModalBtn.onclick = function() {
//         modal.style.display = "none";
//         window.location.href = '/login';
//     };

//     // Close modal when clicking outside of it
//     window.onclick = function(event) {
//         if (event.target == modal) {
//             modal.style.display = "none";
//             window.location.href = '/login';
//         }
//     };
// });


// const provinceSelect = document.getElementById('province');
//     const municipalitySelect = document.getElementById('city');
//     const barangaySelect = document.getElementById('barangay');

//     // Load provinces
//     function loadProvinces() {
//         fetch('https://psgc.gitlab.io/api/provinces')
//             .then(response => response.json())
//             .then(data => {
//                 data.forEach(province => {
//                     const option = document.createElement('option');
//                     option.value = province.code;
//                     option.textContent = province.name;
//                     provinceSelect.appendChild(option);
//                 });
//             })
//             .catch(error => console.error('Error loading provinces:', error));
//     }

//     // Load municipalities
//     function loadMunicipalities() {
//         const provinceCode = provinceSelect.value;

//         fetch(`https://psgc.gitlab.io/api/provinces/${provinceCode}/municipalities`)
//             .then(response => response.json())
//             .then(data => {
//                 municipalitySelect.innerHTML = '<option value="" disabled selected>Select City</option>';
//                 data.forEach(municipality => {
//                     const option = document.createElement('option');
//                     option.value = municipality.code;
//                     option.textContent = municipality.name;
//                     municipalitySelect.appendChild(option);
//                 });
//             })
//             .catch(error => console.error('Error loading municipalities:', error));
//     }

//     // Load barangays
//     function loadBarangays() {
//         const municipalityCode = municipalitySelect.value;

//         fetch(`https://psgc.gitlab.io/api/municipalities/${municipalityCode}/barangays`)
//             .then(response => response.json())
//             .then(data => {
//                 barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
//                 data.forEach(barangay => {
//                     const option = document.createElement('option');
//                     option.value = barangay.code;
//                     option.textContent = barangay.name;
//                     barangaySelect.appendChild(option);
//                 });
//             })
//             .catch(error => console.error('Error loading barangays:', error));
//     }

//     // Event Listeners
//     provinceSelect.addEventListener('change', loadMunicipalities);
//     municipalitySelect.addEventListener('change', loadBarangays);
//     window.onload = loadProvinces;

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".seller-registration-form");
    const modal = document.getElementById("successModal");
    const closeModalBtn = document.querySelector(".close");
    const modalText = document.querySelector("#successModal p");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);

        fetch("/seller-application", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            modalText.textContent = data.message;
            modal.style.display = "flex"; // Show modal

            if (data.status === "success") {
                setTimeout(() => {
                    window.location.href = "/login";
                }, 3000);
            }
        })
        .catch(error => console.error("Error:", error));
    });

    // Close modal manually when "x" is clicked
    closeModalBtn.onclick = function () {
        modal.style.display = "none";
    };

    // Close modal when clicking outside of it
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
});



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