/* ==========================================================
   DermaVision AI — Doctors Directory & Modal Booking JS
========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("bookingModal");
    const closeModalBtn = document.getElementById("closeBookingModal");
    const cancelModalBtn = document.getElementById("cancelBookingBtn");
    const modalDoctorId = document.getElementById("modalDoctorId");
    const modalDocName = document.getElementById("modalDocName");
    const dateInput = document.getElementById("appointment_date");

    // Set minimum date for appointment to today
    if (dateInput) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.min = today;
        dateInput.value = today;
    }

    // Attach click handlers to all "Book Appointment" buttons
    const bookingButtons = document.querySelectorAll(".open-booking-modal");
    bookingButtons.forEach(btn => {
        btn.addEventListener("click", function () {
            const docId = this.getAttribute("data-id");
            const docName = this.getAttribute("data-name");

            if (modalDoctorId) modalDoctorId.value = docId;
            if (modalDocName) modalDocName.innerText = docName;

            if (modal) {
                modal.classList.add("show");
            }
        });
    });

    // Close Modal Handler
    function closeModal() {
        if (modal) {
            modal.classList.remove("show");
        }
    }

    if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
    if (cancelModalBtn) cancelModalBtn.addEventListener("click", closeModal);

    // Close on overlay backdrop click
    if (modal) {
        modal.addEventListener("click", function (e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
});
