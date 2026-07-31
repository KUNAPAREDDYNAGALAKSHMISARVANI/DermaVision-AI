/* ==========================================================
   DermaVision AI — Sidebar Navigation & Theme Controller
========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("sidebarToggleBtn");
    const mobileBtn = document.getElementById("mobileMenuBtn");
    const backdrop = document.getElementById("mobileBackdrop");
    const darkToggleBtn = document.getElementById("darkModeToggle");

    // Restore Desktop Collapse State
    const savedCollapsed = localStorage.getItem("sidebar-collapsed");
    if (savedCollapsed === "true") {
        document.body.classList.add("sidebar-collapsed");
    }

    // Toggle Desktop Sidebar Collapsed State
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            document.body.classList.toggle("sidebar-collapsed");
            const isCollapsed = document.body.classList.contains("sidebar-collapsed");
            localStorage.setItem("sidebar-collapsed", isCollapsed ? "true" : "false");
        });
    }

    // Toggle Mobile Sidebar Drawer
    if (mobileBtn) {
        mobileBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            document.body.classList.toggle("mobile-sidebar-open");
        });
    }

    if (backdrop) {
        backdrop.addEventListener("click", function () {
            document.body.classList.remove("mobile-sidebar-open");
        });
    }

    // Functional Dark Mode Toggle Button
    function syncThemeIcon() {
        if (!darkToggleBtn) return;
        const isDark = document.body.classList.contains("dark-mode") || document.documentElement.classList.contains("dark-mode");
        darkToggleBtn.innerHTML = isDark ? '<i class="fa-solid fa-sun" style="color:#f59e0b;"></i>' : '<i class="fa-solid fa-moon"></i>';
    }

    syncThemeIcon();

    if (darkToggleBtn) {
        darkToggleBtn.addEventListener("click", function () {
            document.documentElement.classList.toggle("dark-mode");
            document.body.classList.toggle("dark-mode");

            const isDark = document.documentElement.classList.contains("dark-mode") || document.body.classList.contains("dark-mode");
            localStorage.setItem("theme", isDark ? "dark" : "light");

            syncThemeIcon();
        });
    }
});
