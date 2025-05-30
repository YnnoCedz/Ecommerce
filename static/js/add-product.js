document.getElementById('category').addEventListener('change', function() {
    const category = this.value;
    const subcategoryContainer = document.getElementById('subcategory');
    
    subcategoryContainer.innerHTML = ''; // Clear previous checkboxes
    
    const options = {
        books: ['Adventure','Autobiography','Fantasy','History','Sci-fi','Psychology','Philosophy','Romance','Thriller'],
        games: ['Action','Adventure','Horror','Simulation','Sport','RPG'],
        movies: ['Action','Animation','Comedy','Drama','Horror','Romance']
    };

    if (options[category]) {
        options[category].forEach(function(sub) {
            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.name = 'subcategory[]'; // Use an array to send multiple values
            checkbox.value = sub.toLowerCase();
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(sub));

            const div = document.createElement('div');
            div.classList.add('checkbox-item');
            div.appendChild(label);
            subcategoryContainer.appendChild(div);
        });
    }
});

// Ensure subcategory[] is sent, even if no checkboxes are selected
document.querySelector('.product-form').addEventListener('submit', function(event) {
    const checkboxes = document.querySelectorAll('input[name="subcategory[]"]:checked');
    const subcategoryContainer = document.getElementById('subcategory');
    
    // If no checkboxes are selected, create a hidden input with an empty value
    if (checkboxes.length === 0) {
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'subcategory[]';
        hiddenInput.value = '';  // empty value
        subcategoryContainer.appendChild(hiddenInput);
    }
});


// Show preview of uploaded image in the image-container
document.getElementById('product-image').addEventListener('change', function(event) {
    const previewImage = document.getElementById('preview-image');
    const file = event.target.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            previewImage.src = e.target.result; // Set the image source to the uploaded file
        };
        reader.readAsDataURL(file); // Read the file as a data URL
    } else {
        previewImage.src = ''; // Reset the preview image if no file is selected
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const mainImageInput = document.getElementById("product-image");
    const mainPreview = document.getElementById("main-preview");
    const imageContainer = document.getElementById("image-container");
    const additionalImagesInput = document.getElementById("additional-images");
    const additionalImagesContainer = document.querySelector(".additional-images-container");
    const additionalImagesList = document.getElementById("additional-images-list");

    // Ensure the main preview starts hidden
    mainPreview.style.display = "none";

    // Handle Main Product Image Upload
    mainImageInput.addEventListener("change", function (event) {
        const file = event.target.files[0];

        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                mainPreview.src = e.target.result;
                mainPreview.style.display = "block"; // Show preview
                imageContainer.style.backgroundImage = "none"; // Remove plus icon background
                additionalImagesContainer.style.display = "block"; // Show additional image upload section
            };
            reader.readAsDataURL(file);
        } else {
            mainPreview.src = "{{ url_for('static', filename='uploads/default-image.jpg') }}";
            mainPreview.style.display = "none"; // Hide preview if no file selected
            imageContainer.style.background = "#f0f2f5 url('../static/images/plus-icon.png') no-repeat center center";
            additionalImagesContainer.style.display = "none"; // Hide additional images if main image is removed
        }
    });

    // Handle Additional Image Uploads
    additionalImagesInput.addEventListener("change", function (event) {
        const files = event.target.files;

        for (let i = 0; i < files.length; i++) {
            const file = files[i];

            if (file) {
                const reader = new FileReader();
                const div = document.createElement("div");
                div.classList.add("additional-image-preview");

                const img = document.createElement("img");
                img.classList.add("preview-image");

                const deleteButton = document.createElement("button");
                deleteButton.innerText = "Delete";
                deleteButton.classList.add("delete-btn");

                reader.onload = function (e) {
                    img.src = e.target.result;
                    img.style.display = "block";
                    deleteButton.style.display = "inline-block"; // Show delete button
                };

                reader.readAsDataURL(file);

                deleteButton.addEventListener("click", function (event) {
                    event.preventDefault();
                    div.remove();
                });

                div.appendChild(img);
                div.appendChild(deleteButton);
                additionalImagesList.appendChild(div);
            }
        }
    });

    // Function to create an additional image upload input
    function createAdditionalImageUpload() {
        const div = document.createElement("div");
        div.classList.add("additional-image-preview");

        const img = document.createElement("img");
        img.classList.add("preview-image");
        img.style.display = "none";

        const input = document.createElement("input");
        input.type = "file";
        input.accept = "image/*";
        input.classList.add("file-input");

        const deleteButton = document.createElement("button");
        deleteButton.innerText = "Delete";
        deleteButton.classList.add("delete-btn");
        deleteButton.style.display = "none"; // Initially hidden

        // Handle image selection for the additional image
        input.addEventListener("change", function () {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    img.src = e.target.result;
                    img.style.display = "block";
                    deleteButton.style.display = "inline-block"; // Show delete button
                };
                reader.readAsDataURL(file);

                // Create another additional image upload field dynamically
                createAdditionalImageUpload();
            }
        });

        // Handle delete button click
        deleteButton.addEventListener("click", function (event) {
            event.preventDefault();
            div.remove();

            // If all additional images are deleted, reset the input field
            if (additionalImagesList.children.length === 0) {
                createAdditionalImageUpload(); // Ensure there's at least one field
            }
        });

        // Append elements to the container
        div.appendChild(img);
        div.appendChild(input);
        div.appendChild(deleteButton);
        additionalImagesList.appendChild(div);
    }

    // Initialize the first additional image upload input
    createAdditionalImageUpload();
});


// document.addEventListener("DOMContentLoaded", function () {
//     const mainImageInput = document.getElementById("product-image");
//     const mainPreview = document.getElementById("main-preview");
//     const imageContainer = document.getElementById("image-container");
//     const additionalImagesContainer = document.querySelector(".additional-images-container");
//     const additionalImagesList = document.getElementById("additional-images-list");

//     // Ensure the main preview starts hidden
//     mainPreview.style.display = "none";

//     // Handle Main Product Image Upload
//     mainImageInput.addEventListener("change", function (event) {
//         const file = event.target.files[0];

//         if (file) {
//             const reader = new FileReader();
//             reader.onload = function (e) {
//                 mainPreview.src = e.target.result;
//                 mainPreview.style.display = "block"; // Show preview
//                 imageContainer.style.backgroundImage = "none"; // Remove plus icon background
//                 additionalImagesContainer.style.display = "block"; // Show additional image upload section
//             };
//             reader.readAsDataURL(file);
//         } else {
//             mainPreview.src = "{{ url_for('static', filename='uploads/default-image.jpg') }}";
//             mainPreview.style.display = "none"; // Hide preview if no file selected
//             imageContainer.style.background = "#f0f2f5 url('../static/images/plus-icon.png') no-repeat center center";
//             additionalImagesContainer.style.display = "none"; // Hide additional images if main image is removed
//         }
//     });

//     // Function to create an additional image upload input
//     function createAdditionalImageUpload() {
//         const div = document.createElement("div");
//         div.classList.add("additional-image-preview");

//         const img = document.createElement("img");
//         img.classList.add("preview-image");
//         img.style.display = "none";

//         const input = document.createElement("input");
//         input.type = "file";
//         input.accept = "image/*";
//         input.classList.add("file-input");

//         const deleteButton = document.createElement("button");
//         deleteButton.innerText = "Delete";
//         deleteButton.classList.add("delete-btn");
//         deleteButton.style.display = "none"; // Initially hidden

//         // Handle image selection for the additional image
//         input.addEventListener("change", function () {
//             const file = input.files[0];
//             if (file) {
//                 const reader = new FileReader();
//                 reader.onload = function (e) {
//                     img.src = e.target.result;
//                     img.style.display = "block";
//                     deleteButton.style.display = "inline-block"; // Show delete button
//                 };
//                 reader.readAsDataURL(file);

//                 // Create another additional image upload field dynamically
//                 createAdditionalImageUpload();
//             }
//         });

//         // Handle delete button click
//         deleteButton.addEventListener("click", function (event) {
//             event.preventDefault();
//             div.remove();

//             // If all additional images are deleted, reset the input field
//             if (additionalImagesList.children.length === 0) {
//                 createAdditionalImageUpload(); // Ensure there's at least one field
//             }
//         });

//         // Append elements to the container
//         div.appendChild(img);
//         div.appendChild(input);
//         div.appendChild(deleteButton);
//         additionalImagesList.appendChild(div);
//     }

//     // Initialize the first additional image upload input
//     createAdditionalImageUpload();
// });



// document.addEventListener("DOMContentLoaded", function () {
//     const mainImageInput = document.getElementById("product-image");
//     const mainPreview = document.getElementById("main-preview");
//     const imageContainer = document.getElementById("image-container");
//     const additionalImagesContainer = document.querySelector(".additional-images-container");
//     const additionalImagesList = document.getElementById("additional-images-list");
//     const additionalImagesInput = document.getElementById("additional-images");

//     // Hide the main preview until an image is uploaded
//     mainPreview.style.display = "none";

//     // Handle Main Product Image Upload
//     mainImageInput.addEventListener("change", function (event) {
//         const file = event.target.files[0];

//         if (file) {
//             const reader = new FileReader();
//             reader.onload = function (e) {
//                 mainPreview.src = e.target.result;
//                 mainPreview.style.display = "block"; // Show preview
//                 imageContainer.style.backgroundImage = "none"; // Remove plus icon background
//                 additionalImagesContainer.style.display = "block"; // Show additional image upload section
//             };
//             reader.readAsDataURL(file);
//         } else {
//             mainPreview.src = "{{ url_for('static', filename='uploads/default-image.jpg') }}";
//             mainPreview.style.display = "none"; // Hide preview if no file selected
//             imageContainer.style.background = "#f0f2f5 url('../static/images/plus-icon.png') no-repeat center center";
//             additionalImagesContainer.style.display = "none"; // Hide additional images if main image is removed
//         }
//     });

//     function createAdditionalImageUpload() {
//         const div = document.createElement("div");
//         div.classList.add("additional-image-preview");

//         const img = document.createElement("img");
//         img.classList.add("preview-image");
//         img.style.display = "none";

//         const input = document.createElement("input");
//         input.type = "file";
//         input.accept = "image/*";
//         input.classList.add("file-input");

//         const deleteButton = document.createElement("button");
//         deleteButton.innerText = "Delete";
//         deleteButton.classList.add("delete-btn");
//         deleteButton.style.display = "none"; // Initially hidden

//         input.addEventListener("change", function () {
//             const file = input.files[0];
//             if (file) {
//                 const reader = new FileReader();
//                 reader.onload = function (e) {
//                     img.src = e.target.result;
//                     img.style.display = "block";
//                     deleteButton.style.display = "inline-block";
//                 };
//                 reader.readAsDataURL(file);

//                 createAdditionalImageUpload(); // Add another upload field dynamically
//             }
//         });

//         deleteButton.addEventListener("click", function (event) {
//             event.preventDefault();
//             div.remove();

//             // If all additional images are deleted, reset the input field
//             if (additionalImagesList.children.length === 0) {
//                 additionalImagesInput.value = "";
//                 createAdditionalImageUpload();
//             }
//         });

//         div.appendChild(img);
//         div.appendChild(input);
//         div.appendChild(deleteButton);
//         additionalImagesList.appendChild(div);
//     }

//     // Initialize the First Additional Image Input with delete button
//     createAdditionalImageUpload();
// });
