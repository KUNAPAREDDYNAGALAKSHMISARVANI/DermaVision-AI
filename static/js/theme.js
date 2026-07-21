// ======================================
// DermaVision AI Theme Manager
// ======================================

// Load saved theme
const savedTheme = localStorage.getItem("theme");

if (savedTheme === "dark") {
    document.documentElement.classList.add("dark-mode");
    document.body.classList.add("dark-mode");
}

// Toggle Theme
function toggleTheme() {

    document.documentElement.classList.toggle("dark-mode");
    document.body.classList.toggle("dark-mode");

    if (document.documentElement.classList.contains("dark-mode") || document.body.classList.contains("dark-mode")) {

        localStorage.setItem("theme", "dark");

    } else {

        localStorage.setItem("theme", "light");

    }

}