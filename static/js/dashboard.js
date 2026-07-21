document.addEventListener("DOMContentLoaded", function () {

    console.log("Dashboard JS Loaded");

    if (typeof diseaseLabels === "undefined") {
        console.error("Disease data not received from Flask.");
        return;
    }

    // ===============================
    // Disease Distribution Pie Chart
    // ===============================

    const diseaseCanvas = document.getElementById("diseaseChart");

    if (diseaseCanvas) {

        new Chart(diseaseCanvas, {

            type: "pie",

            data: {

                labels: diseaseLabels,

                datasets: [

                    {

                        data: diseaseCounts,

                        backgroundColor: [

                            "#1976d2",
                            "#43a047",
                            "#ef6c00",
                            "#ab47bc",
                            "#26a69a",
                            "#f4511e",
                            "#5c6bc0",
                            "#ec407a",
                            "#8d6e63"

                        ]

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom"

                    }

                }

            }

        });

    }

    // ===============================
    // Average Confidence by Disease
    // ===============================

    const confidenceCanvas = document.getElementById("confidenceChart");

    if (confidenceCanvas) {

        new Chart(confidenceCanvas, {

            type: "bar",

            data: {

                labels: confidenceLabels,

                datasets: [

                    {

                        label: "Average Confidence (%)",

                        data: confidenceValues,

                        backgroundColor: [

                            "#1976d2",
                            "#42a5f5",
                            "#64b5f6",
                            "#90caf9",
                            "#1e88e5",
                            "#5c6bc0",
                            "#26a69a",
                            "#66bb6a",
                            "#7e57c2"

                        ],

                        borderRadius: 10,

                        borderSkipped: false

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        display: false

                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                return context.raw + "%";

                            }

                        }

                    }

                },

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 100,

                        title: {

                            display: true,

                            text: "Average Confidence (%)"

                        }

                    },

                    x: {

                        ticks: {

                            maxRotation: 25,

                            minRotation: 25

                        }

                    }

                }

            }

        });

    }

});