document.getElementById('province').addEventListener('change', function() {
    const provinceCode = this.value;

    // Fetch cities based on the selected province
    fetch(`/get-cities/${provinceCode}`)
        .then(response => response.json())
        .then(data => {
            const citySelect = document.getElementById('city');
            citySelect.innerHTML = '<option value="" disabled selected>Select City/Municipality</option>';
            data.forEach(city => {
                citySelect.innerHTML += `<option value="${city.code}">${city.name}</option>`;
            });

            // Clear barangay dropdown
            document.getElementById('barangay').innerHTML = '<option value="" disabled selected>Select Barangay</option>';
        });
});

document.getElementById('city').addEventListener('change', function() {
    const cityCode = this.value;

    // Fetch barangays based on the selected city
    fetch(`/get-barangays/${cityCode}`)
        .then(response => response.json())
        .then(data => {
            const barangaySelect = document.getElementById('barangay');
            barangaySelect.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
            data.forEach(barangay => {
                barangaySelect.innerHTML += `<option value="${barangay.code}">${barangay.name}</option>`;
            });
        });
});