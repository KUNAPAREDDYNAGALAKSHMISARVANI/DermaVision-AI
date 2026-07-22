/* ==========================================================
   DermaVision AI — Dashboard Analytics JavaScript (Phase 3)
   Handles Chart.js rendering, theme adaptation, table search & sorting
========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const isDarkMode = () => document.documentElement.classList.contains("dark-mode") || document.body.classList.contains("dark-mode");

    const getGridColor = () => isDarkMode() ? "rgba(255, 255, 255, 0.08)" : "rgba(0, 0, 0, 0.05)";
    const getTextColor = () => isDarkMode() ? "#cbd5e1" : "#475569";

    // ==========================================
    // 1. Weekly Activity Bar Chart
    // ==========================================
    const weeklyCanvas = document.getElementById("weeklyActivityChart");
    let weeklyChart = null;

    if (weeklyCanvas && window.weeklyLabels && window.weeklyLabels.length > 0) {
        weeklyChart = new Chart(weeklyCanvas, {
            type: "bar",
            data: {
                labels: window.weeklyLabels,
                datasets: [{
                    label: "Scans",
                    data: window.weeklyCounts,
                    backgroundColor: "#1976d2",
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return `Scans: ${ctx.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: getGridColor() },
                        ticks: { color: getTextColor(), font: { family: "Inter", size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 1, color: getTextColor(), font: { family: "Inter", size: 11 } },
                        grid: { color: getGridColor() }
                    }
                }
            }
        });
    }

    // ==========================================
    // 2. Disease Distribution Chart
    // ==========================================
    const diseaseCanvas = document.getElementById("diseaseDistributionChart");
    let diseaseChart = null;

    if (diseaseCanvas && window.diseaseLabels && window.diseaseLabels.length > 0) {
        diseaseChart = new Chart(diseaseCanvas, {
            type: "doughnut",
            data: {
                labels: window.diseaseLabels,
                datasets: [{
                    data: window.diseaseCounts,
                    backgroundColor: [
                        "#1976d2", "#43a047", "#ef6c00", "#ab47bc",
                        "#26a69a", "#f4511e", "#5c6bc0", "#ec407a", "#8d6e63"
                    ],
                    borderWidth: 2,
                    borderColor: isDarkMode() ? "#162033" : "#ffffff"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: getTextColor(),
                            boxWidth: 12,
                            font: { family: "Inter", size: 11 }
                        }
                    }
                }
            }
        });
    }

    // ==========================================
    // 3. Monthly Confidence Trend Line Chart
    // ==========================================
    const monthlyCanvas = document.getElementById("monthlyConfidenceChart");
    let monthlyChart = null;

    if (monthlyCanvas && window.monthlyLabels && window.monthlyLabels.length > 0) {
        monthlyChart = new Chart(monthlyCanvas, {
            type: "line",
            data: {
                labels: window.monthlyLabels,
                datasets: [{
                    label: "Monthly Avg Confidence (%)",
                    data: window.monthlyConfidences,
                    borderColor: "#43a047",
                    backgroundColor: isDarkMode() ? "rgba(67, 160, 71, 0.2)" : "rgba(67, 160, 71, 0.1)",
                    borderWidth: 3,
                    pointBackgroundColor: "#43a047",
                    pointRadius: 5,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return `Avg Confidence: ${ctx.raw}%`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: getGridColor() },
                        ticks: { color: getTextColor(), font: { family: "Inter", size: 11 } }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: getGridColor() },
                        ticks: {
                            color: getTextColor(),
                            callback: function(v) { return v + "%"; },
                            font: { family: "Inter", size: 11 }
                        }
                    }
                }
            }
        });
    }

    // ==========================================
    // Theme Mutation Observer for Charts
    // ==========================================
    const themeObserver = new MutationObserver(function () {
        const grid = getGridColor();
        const text = getTextColor();

        [weeklyChart, diseaseChart, monthlyChart].forEach(chart => {
            if (chart) {
                if (chart.options.scales && chart.options.scales.x) {
                    chart.options.scales.x.grid.color = grid;
                    chart.options.scales.x.ticks.color = text;
                }
                if (chart.options.scales && chart.options.scales.y) {
                    chart.options.scales.y.grid.color = grid;
                    chart.options.scales.y.ticks.color = text;
                }
                if (chart.options.plugins && chart.options.plugins.legend && chart.options.plugins.legend.labels) {
                    chart.options.plugins.legend.labels.color = text;
                }
                chart.update();
            }
        });
    });

    themeObserver.observe(document.body, { attributes: true, attributeFilter: ["class"] });
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
});

/* ==========================================================
   Client-Side Table Search Filter
========================================================== */
function filterDashboardTable() {
    const input = document.getElementById("dashboardTableSearch");
    if (!input) return;
    const filter = input.value.toLowerCase();
    const table = document.getElementById("dashboardRecentTable");
    if (!table) return;
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName("td");
        let match = false;

        for (let j = 0; j < cells.length; j++) {
            const cellText = cells[j].textContent || cells[j].innerText;
            if (cellText.toLowerCase().indexOf(filter) > -1) {
                match = true;
                break;
            }
        }

        row.style.display = match ? "" : "none";
    }
}

/* ==========================================================
   Client-Side Table Column Sorting
========================================================== */
let sortDirections = {};

function sortDashboardTable(columnIndex) {
    const table = document.getElementById("dashboardRecentTable");
    if (!table) return;
    const tbody = table.querySelector("tbody");
    const rows = Array.from(tbody.querySelectorAll("tr"));

    const currentDir = sortDirections[columnIndex] || "asc";
    const newDir = currentDir === "asc" ? "desc" : "asc";
    sortDirections[columnIndex] = newDir;

    rows.sort((a, b) => {
        let valA = a.cells[columnIndex].textContent.trim();
        let valB = b.cells[columnIndex].textContent.trim();

        // Extract numeric value for confidence
        if (valA.endsWith("%")) {
            valA = parseFloat(valA.replace("%", "")) || 0;
            valB = parseFloat(valB.replace("%", "")) || 0;
        }

        if (valA < valB) return newDir === "asc" ? -1 : 1;
        if (valA > valB) return newDir === "asc" ? 1 : -1;
        return 0;
    });

    rows.forEach(row => tbody.appendChild(row));
}