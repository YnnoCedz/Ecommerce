// document.addEventListener("DOMContentLoaded", function () {
//     // Password match validation
//     document.querySelector("form").addEventListener("submit", function (e) {
//         const password = document.querySelector('input[name="password"]').value;
//         const confirmPassword = document.querySelector('input[name="confirm-password"]').value;

//         if (password !== confirmPassword) {
//             e.preventDefault();
//             alert("Passwords do not match. Please try again.");
//         }
//     });

//     // Modal Handling  
//     const modal = document.getElementById("successModal");
//     const closeButton = document.querySelector(".close");

//     function showModal() {
//         if (modal) {
//             modal.style.display = "flex"; // Ensure it becomes visible
//         }
//     }

//     function hideModal() {
//         if (modal) {
//             modal.style.display = "none";
//             window.location.href = "/login"; // Redirect to login page
//         }
//     }

//     // Event Listeners for Modal Close
//     if (modal && closeButton) {
//         closeButton.addEventListener("click", hideModal);
//         window.addEventListener("click", function (event) {
//             if (event.target === modal) {
//                 hideModal();
//             }
//         });
//     }

//     // Check if Registration was Successful
//     if (document.body.dataset.success === "True") {
//         showModal();
//     }

//     // Load Address Dropdowns
//     const provinceSelect = document.getElementById("province");
//     const municipalitySelect = document.getElementById("city");
//     const barangaySelect = document.getElementById("barangay");

//     async function loadProvinces() {
//         try {
//             const response = await fetch("https://psgc.gitlab.io/api/provinces");
//             const data = await response.json();
//             provinceSelect.innerHTML = '<option value="" disabled selected>Select Province</option>';
//             data.forEach(province => {
//                 const option = document.createElement("option");
//                 option.value = province.code;
//                 option.textContent = province.name;
//                 provinceSelect.appendChild(option);
//             });
//         } catch (error) {
//             console.error("Error loading provinces:", error);
//         }
//     }

//     async function loadMunicipalities() {
//         const provinceCode = provinceSelect.value;
//         if (!provinceCode) return;
//         try {
//             const response = await fetch(`https://psgc.gitlab.io/api/provinces/${provinceCode}/municipalities`);
//             const data = await response.json();
//             municipalitySelect.innerHTML = '<option value="" disabled selected>Select City</option>';
//             data.forEach(municipality => {
//                 const option = document.createElement("option");
//                 option.value = municipality.code;
//                 option.textContent = municipality.name;
//                 municipalitySelect.appendChild(option);
//             });
//         } catch (error) {
//             console.error("Error loading municipalities:", error);
//         }
//     }

//     async function loadBarangays() {
//         const municipalityCode = municipalitySelect.value;
//         if (!municipalityCode) return;
//         try {
//             const response = await fetch(`https://psgc.gitlab.io/api/municipalities/${municipalityCode}/barangays`);
//             const data = await response.json();
//             barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
//             data.forEach(barangay => {
//                 const option = document.createElement("option");
//                 option.value = barangay.code;
//                 option.textContent = barangay.name;
//                 barangaySelect.appendChild(option);
//             });
//         } catch (error) {
//             console.error("Error loading barangays:", error);
//         }
//     }

//     if (provinceSelect && municipalitySelect && barangaySelect) {
//         provinceSelect.addEventListener("change", loadMunicipalities);
//         municipalitySelect.addEventListener("change", loadBarangays);
//         loadProvinces();
//     }
// });


document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector(".seller-registration-form");
    const modal = document.getElementById("successModal");
    const closeModalBtn = document.querySelector(".close");
    const modalText = document.querySelector("#successModal p");

    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = new FormData(form);

        fetch("/courier_registration", {
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

    closeModalBtn.onclick = function () {
        modal.style.display = "none";
    };

    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };

    // Load Address Dropdowns
    const provinceSelect = document.getElementById("province");
    const municipalitySelect = document.getElementById("city");
    const barangaySelect = document.getElementById("barangay");

    async function loadProvinces() {
        try {
            const response = await fetch("https://psgc.gitlab.io/api/provinces");
            const data = await response.json();
            provinceSelect.innerHTML = '<option value="" disabled selected>Select Province</option>';
            data.forEach(province => {
                const option = document.createElement("option");
                option.value = province.code;
                option.textContent = province.name;
                provinceSelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error loading provinces:", error);
        }
    }

    async function loadMunicipalities() {
        const provinceCode = provinceSelect.value;
        if (!provinceCode) return;
        try {
            const response = await fetch(`https://psgc.gitlab.io/api/provinces/${provinceCode}/municipalities`);
            const data = await response.json();
            municipalitySelect.innerHTML = '<option value="" disabled selected>Select City</option>';
            data.forEach(municipality => {
                const option = document.createElement("option");
                option.value = municipality.code;
                option.textContent = municipality.name;
                municipalitySelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error loading municipalities:", error);
        }
    }

    async function loadBarangays() {
        const municipalityCode = municipalitySelect.value;
        if (!municipalityCode) return;
        try {
            const response = await fetch(`https://psgc.gitlab.io/api/municipalities/${municipalityCode}/barangays`);
            const data = await response.json();
            barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
            data.forEach(barangay => {
                const option = document.createElement("option");
                option.value = barangay.code;
                option.textContent = barangay.name;
                barangaySelect.appendChild(option);
            });
        } catch (error) {
            console.error("Error loading barangays:", error);
        }
    }

    provinceSelect.addEventListener("change", loadMunicipalities);
    municipalitySelect.addEventListener("change", loadBarangays);
    loadProvinces();
});
