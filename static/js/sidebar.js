/* ==========================================================
   DermaVision AI — Collapsible Sidebar JavaScript
========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("sidebarToggleBtn");
    const mobileBtn = document.getElementById("mobileMenuBtn");
    const backdrop = document.getElementById("mobileBackdrop");

    // Restore saved collapse state from localStorage
    const savedCollapsed = localStorage.getItem("sidebar-collapsed");
    if (savedCollapsed === "true") {
        document.body.classList.add("sidebar-collapsed");
    }

    // Toggle Desktop Collapsed State
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            document.body.classList.toggle("sidebar-collapsed");
            const isCollapsed = document.body.classList.contains("sidebar-collapsed");
            localStorage.setItem("sidebar-collapsed", isCollapsed ? "true" : "false");
        });
    }

    // Toggle Mobile Drawer
    if (mobileBtn) {
        mobileBtn.addEventListener("click", function () {
            document.body.classList.toggle("mobile-sidebar-open");
        });
    }

    if (backdrop) {
        backdrop.addEventListener("click", function () {
            document.body.classList.remove("mobile-sidebar-open");
        });
    }
});
