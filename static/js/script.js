document.addEventListener("DOMContentLoaded", () => {

    // match template IDs/classes: `chooseImage`, `imageInput`, `.preview-wrapper`, `previewImage`, `dropZone`
    const browseBtn = document.getElementById("chooseImage") || document.getElementById("browseBtn");
    const imageInput = document.getElementById("imageInput");
    const previewContainer = document.querySelector('.preview-wrapper');
    const previewImage = document.getElementById("previewImage");
    const dropArea = document.getElementById("dropZone") || document.getElementById("dropArea");

    // Browse Button
    if (browseBtn && imageInput) {
        browseBtn.addEventListener("click", () => {
            imageInput.click();
        });
    }

    // Display Image Preview
    function showPreview(file) {

        if (!file) return;

        if (!file.type.startsWith("image/")) {
            alert("Please upload a valid image.");
            return;
        }

        const reader = new FileReader();

        reader.onload = function (event) {

            if (previewContainer) {
                previewContainer.style.display = "block";
            }

            if (previewImage) {
                previewImage.src = event.target.result;
            }

        };

        reader.readAsDataURL(file);

    }

    // File Selected
    if (imageInput) {

        imageInput.addEventListener("change", function () {

            if (this.files.length > 0) {
                showPreview(this.files[0]);
            }

        });

    }

    // Prevent Default Browser Behavior
    ["dragenter", "dragover", "dragleave", "drop"].forEach(eventName => {

        if (!dropArea) return;

        dropArea.addEventListener(eventName, function (e) {

            e.preventDefault();
            e.stopPropagation();

        });

    });

    // Highlight Drop Area
    ["dragenter", "dragover"].forEach(eventName => {

        if (!dropArea) return;

        dropArea.addEventListener(eventName, function () {

            dropArea.classList.add("dragging");

        });

    });

    // Remove Highlight
    ["dragleave", "drop"].forEach(eventName => {

        if (!dropArea) return;

        dropArea.addEventListener(eventName, function () {

            dropArea.classList.remove("dragging");

        });

    });

    // Handle File Drop
    if (dropArea) {

        dropArea.addEventListener("drop", function (e) {

            const files = e.dataTransfer.files;

            if (files.length > 0) {

                imageInput.files = files;

                showPreview(files[0]);

            }

        });

    }

});