/* ==========================================================
   DermaVision AI — Progress Tracker JavaScript
   Handles Chart.js rendering, node highlighting & theme responsiveness
========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("confidenceTrendChart");

    if (!ctx) return;

    const dates = window.trendDates || [];
    const confidences = window.trendConfidences || [];
    const diseases = window.trendDiseases || [];
    const ids = window.trendIds || [];
    const scan1Id = window.scan1Id;
    const scan2Id = window.scan2Id;

    if (dates.length === 0) {
        ctx.parentNode.innerHTML = `
            <div class="empty-chart-notice">
                <i class="fas fa-chart-line" style="font-size: 3rem; color: #94a3b8; margin-bottom: 12px;"></i>
                <p style="color: #64748b; font-weight: 500;">No scan data available to generate trend graph. Perform scans to view progress tracking.</p>
            </div>
        `;
        return;
    }

    const isDarkMode = document.documentElement.classList.contains("dark-mode") || document.body.classList.contains("dark-mode");

    const gridColor = isDarkMode ? "rgba(255, 255, 255, 0.1)" : "rgba(0, 0, 0, 0.06)";
    const textColor = isDarkMode ? "#cbd5e1" : "#475569";
    const lineColor = "#1976d2";
    const defaultPointColor = "#42a5f5";
    const fillGradientColor = isDarkMode ? "rgba(25, 118, 210, 0.25)" : "rgba(25, 118, 210, 0.12)";

    // Highlight selected baseline (scan1) and comparison (scan2) points on the trend graph
    const pointColors = ids.map(id => {
        if (id === scan1Id) return "#f59e0b"; // Amber for Baseline scan
        if (id === scan2Id) return "#10b981"; // Emerald for Comparison scan
        return defaultPointColor;
    });

    const pointRadii = ids.map(id => {
        if (id === scan1Id || id === scan2Id) return 9;
        return 6;
    });

    const chartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: dates,
            datasets: [{
                label: "AI Diagnostic Confidence (%)",
                data: confidences,
                borderColor: lineColor,
                backgroundColor: fillGradientColor,
                borderWidth: 3,
                pointBackgroundColor: pointColors,
                pointBorderColor: "#ffffff",
                pointBorderWidth: 2,
                pointRadius: pointRadii,
                pointHoverRadius: 11,
                tension: 0.35,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: textColor,
                        font: {
                            family: "Inter, sans-serif",
                            size: 14,
                            weight: "600"
                        }
                    }
                },
                tooltip: {
                    backgroundColor: isDarkMode ? "#1e293b" : "#ffffff",
                    titleColor: isDarkMode ? "#f8fafc" : "#0f172a",
                    bodyColor: isDarkMode ? "#cbd5e1" : "#334155",
                    borderColor: isDarkMode ? "#334155" : "#e2e8f0",
                    borderWidth: 1,
                    padding: 14,
                    cornerRadius: 12,
                    displayColors: false,
                    callbacks: {
                        title: function (context) {
                            const index = context[0].dataIndex;
                            return dates[index];
                        },
                        label: function (context) {
                            const index = context.dataIndex;
                            const scanId = ids[index];
                            let tag = "";
                            if (scanId === scan1Id) tag = " [Baseline Selected]";
                            if (scanId === scan2Id) tag = " [Follow-up Selected]";

                            return [
                                `Condition: ${diseases[index]}${tag}`,
                                `Confidence: ${confidences[index]}%`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: gridColor,
                        drawBorder: false
                    },
                    ticks: {
                        color: textColor,
                        font: {
                            family: "Inter, sans-serif",
                            size: 12
                        }
                    }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: {
                        color: gridColor,
                        drawBorder: false
                    },
                    ticks: {
                        color: textColor,
                        stepSize: 20,
                        callback: function (value) {
                            return value + "%";
                        },
                        font: {
                            family: "Inter, sans-serif",
                            size: 12
                        }
                    }
                }
            }
        }
    });

    // Theme observer for smooth light/dark mode chart updates
    const observer = new MutationObserver(function () {
        const dark = document.documentElement.classList.contains("dark-mode") || document.body.classList.contains("dark-mode");
        const newGrid = dark ? "rgba(255, 255, 255, 0.1)" : "rgba(0, 0, 0, 0.06)";
        const newText = dark ? "#cbd5e1" : "#475569";

        chartInstance.options.scales.x.grid.color = newGrid;
        chartInstance.options.scales.x.ticks.color = newText;
        chartInstance.options.scales.y.grid.color = newGrid;
        chartInstance.options.scales.y.ticks.color = newText;
        chartInstance.options.plugins.legend.labels.color = newText;

        chartInstance.update();
    });

    observer.observe(document.body, { attributes: true, attributeFilter: ["class"] });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });
});