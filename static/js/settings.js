// ======================================
// DermaVision AI
// settings.js
// ======================================

document.addEventListener("DOMContentLoaded", () => {

    // ----------------------------
    // Clear Scan History
    // ----------------------------

    const clearBtn = document.getElementById("clearHistoryBtn");

    if (clearBtn) {

        clearBtn.addEventListener("click", async function () {

            const confirmed = confirm(
                "Are you sure you want to permanently delete all scan history?"
            );

            if (!confirmed) return;

            try {

                const response = await fetch("/clear_history", {
                    method: "POST"
                });

                if (response.ok) {

                    alert("Scan history cleared successfully.");

                    window.location.href = "/history";

                } else {

                    alert("Unable to clear history.");

                }

            } catch (error) {

                console.error(error);

                alert("Something went wrong.");

            }

        });

    }

    // ----------------------------
// Reset Preferences
// ----------------------------

    const resetBtn = document.getElementById("resetPreferencesBtn");

    if (resetBtn && !resetBtn.dataset.resetBound) {
        resetBtn.dataset.resetBound = "true";

        resetBtn.addEventListener("click", function () {
            const confirmed = window.confirm("Reset all preferences to default?");

            if (!confirmed) return;

            // Remove saved preferences
            localStorage.removeItem("language");
            localStorage.removeItem("darkMode");
            localStorage.removeItem("theme");
            localStorage.setItem("theme", "light");

            // Reset language selector
            const languageSelect = document.getElementById("languageSelect");

            if (languageSelect) {
                languageSelect.value = "en";
            }

            // Remove dark mode from the page
            document.body.classList.remove("dark-mode");
            document.documentElement.classList.remove("dark-mode");

            // Reset theme toggle
            const themeToggle = document.getElementById("themeToggle");

            if (themeToggle) {
                themeToggle.checked = false;
            }

            // Apply English immediately and update the page state
            if (typeof applyLanguage === "function") {
                applyLanguage("en");
            }

            window.alert("Preferences reset successfully.");
        });
    }

});