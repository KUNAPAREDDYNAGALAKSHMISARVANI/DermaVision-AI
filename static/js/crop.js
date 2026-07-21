/* ==========================================================
   DermaVision AI
   Professional Image Cropper
   Requires Cropper.js
========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const uploadPreview = document.getElementById("previewImage");
    const input = document.getElementById("imageInput");
    const preview = document.getElementById("cropImage");

    const cropModal = document.getElementById("cropModal");

    const cropBtn = document.getElementById("cropButton");
    const cancelBtn = document.getElementById("cancelCrop");

    const rotateLeft = document.getElementById("rotateLeft");
    const rotateRight = document.getElementById("rotateRight");

    const zoomIn = document.getElementById("zoomIn");
    const zoomOut = document.getElementById("zoomOut");

    const reset = document.getElementById("resetCrop");
    const flip = document.getElementById("flipHorizontal");

    let cropper;

    let scaleX = 1;

    if (!input) return;

    input.addEventListener("change", function (e) {

        const file = e.target.files[0];

        if (!file) return;

        const reader = new FileReader();

        reader.onload = function (event) {

            preview.src = event.target.result;

            cropModal.classList.add("show");

            if (cropper) {

                cropper.destroy();

            }
            if (typeof Cropper === "undefined") {

            console.error("Cropper.js is not loaded.");

            return;

        }

            cropper = new Cropper(preview, {

                aspectRatio: NaN,

                viewMode: 1,

                autoCropArea: 0.85,

                background: false,

                responsive: true,

                movable: true,

                scalable: true,

                zoomable: true,

                rotatable: true,

                dragMode: "move",

                guides: true,

                center: true,

                highlight: true,

                cropBoxMovable: true,

                cropBoxResizable: true,

                toggleDragModeOnDblclick: false

            });

        };

        reader.readAsDataURL(file);

    });
    /* ===========================================
       Rotate Controls
    =========================================== */

    rotateLeft.addEventListener("click", function () {

        if (cropper) {

            cropper.rotate(-90);

        }

    });

    rotateRight.addEventListener("click", function () {

        if (cropper) {

            cropper.rotate(90);

        }

    });


    /* ===========================================
       Zoom Controls
    =========================================== */

    zoomIn.addEventListener("click", function () {

        if (cropper) {

            cropper.zoom(0.1);

        }

    });

    zoomOut.addEventListener("click", function () {

        if (cropper) {

            cropper.zoom(-0.1);

        }

    });


    /* ===========================================
       Flip Image
    =========================================== */

    flip.addEventListener("click", function () {

        if (!cropper) return;

        scaleX = scaleX === 1 ? -1 : 1;

        cropper.scaleX(scaleX);

    });


    /* ===========================================
       Reset Cropper
    =========================================== */

    reset.addEventListener("click", function () {

        if (!cropper) return;

        cropper.reset();

        scaleX = 1;

    });


    /* ===========================================
       Cancel Crop
    =========================================== */

    cancelBtn.addEventListener("click", function () {

        cropModal.classList.remove("show");

        if (cropper) {

            cropper.destroy();

            cropper = null;

        }
        preview.src = "";

    });


    /* ===========================================
       Apply Crop
    =========================================== */

    cropBtn.addEventListener("click", function () {

        if (!cropper) return;

        const canvas = cropper.getCroppedCanvas({

            imageSmoothingEnabled: true,

            imageSmoothingQuality: "high",

            fillColor: "#ffffff"

        });

        canvas.toBlob(function (blob) {

            const croppedFile = new File(

                [blob],

                "cropped-image.png",

                {

                    type: "image/png",

                    lastModified: Date.now()

                }

            );

            const dataTransfer = new DataTransfer();

            dataTransfer.items.add(croppedFile);

            input.files = dataTransfer.files;

            const croppedData = canvas.toDataURL("image/png");

            preview.src = croppedData;
            uploadPreview.src = croppedData;
            uploadPreview.style.display = "block";

            cropModal.classList.remove("show");

            cropper.destroy();

            cropper = null;
            preview.src = "";

        }, "image/png");

    });

});