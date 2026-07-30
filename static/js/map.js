/* ==========================================================
   DermaVision AI — Nearby Dermatologist Leaflet Map JS
========================================================== */

document.addEventListener("DOMContentLoaded", function () {
    const mapCanvas = document.getElementById("mapView");
    if (!mapCanvas || !window.doctorsData || !typeof L === "undefined") return;

    const doctors = window.doctorsData;

    // Default center (Hyderabad)
    const defaultLat = 17.4065;
    const defaultLng = 78.4772;

    const map = L.map("mapView").setView([defaultLat, defaultLng], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const markersMap = {};
    const doctorGroup = L.featureGroup();

    // Custom Stethoscope Map Pin Marker Icon
    const doctorIcon = L.divIcon({
        className: "custom-leaflet-marker",
        html: `<div style="background:#4f46e5;color:white;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 10px rgba(0,0,0,0.3);border:2px solid white;"><i class="fas fa-user-doctor"></i></div>`,
        iconSize: [34, 34],
        iconAnchor: [17, 17]
    });

    doctors.forEach(doc => {
        if (doc.latitude && doc.longitude) {
            const marker = L.marker([doc.latitude, doc.longitude], { icon: doctorIcon })
                .bindPopup(`
                    <div style="font-family:'Inter',sans-serif;padding:5px;">
                        <h4 style="margin:0 0 4px;font-size:14px;color:#0f172a;">${doc.name}</h4>
                        <p style="margin:0 0 6px;font-size:12px;color:#4f46e5;">${doc.hospital} (${doc.city})</p>
                        <p style="margin:0 0 8px;font-size:12px;color:#64748b;">${doc.specialization}</p>
                        <a href="/doctor/${doc.id}" style="display:inline-block;background:#4f46e5;color:white;padding:4px 10px;border-radius:6px;font-size:11px;text-decoration:none;font-weight:600;">View Profile</a>
                    </div>
                `);

            marker.addTo(doctorGroup);
            markersMap[doc.id] = marker;
        }
    });

    if (doctors.length > 0) {
        map.fitBounds(doctorGroup.getBounds().pad(0.2));
    }

    // Sidebar card click listener to pan map
    const tiles = document.querySelectorAll(".map-doc-tile");
    tiles.forEach(tile => {
        tile.addEventListener("click", function () {
            const docId = this.getAttribute("data-id");
            const lat = parseFloat(this.getAttribute("data-lat"));
            const lng = parseFloat(this.getAttribute("data-lng"));

            tiles.forEach(t => t.classList.remove("active"));
            this.classList.add("active");

            if (lat && lng) {
                map.setView([lat, lng], 15, { animate: true });
                if (markersMap[docId]) {
                    markersMap[docId].openPopup();
                }
            }
        });
    });

    // Haversine Distance Calculation (in km)
    function calcDistance(lat1, lon1, lat2, lon2) {
        const R = 6371.0;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return (R * c).toFixed(1);
    }

    // Geolocation Find Near Me Handler
    const locateBtn = document.getElementById("locateUserBtn");
    const geoStatusText = document.getElementById("geoStatusText");
    const sortNoticeTag = document.getElementById("sortNoticeTag");

    if (locateBtn) {
        locateBtn.addEventListener("click", function () {
            if (!navigator.geolocation) {
                alert("Geolocation is not supported by your browser.");
                return;
            }

            geoStatusText.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Detecting your current position...`;

            navigator.geolocation.getCurrentPosition(
                function (position) {
                    const userLat = position.coords.latitude;
                    const userLng = position.coords.longitude;

                    geoStatusText.innerHTML = `<i class="fas fa-circle-check" style="color:#16a34a;"></i> GPS Location Found (${userLat.toFixed(2)}, ${userLng.toFixed(2)})`;
                    sortNoticeTag.innerText = "Sorted by proximity";

                    // User Marker
                    const userIcon = L.divIcon({
                        className: "user-location-marker",
                        html: `<div style="background:#ef4444;color:white;width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 3px 10px rgba(0,0,0,0.3);border:3px solid white;"><i class="fas fa-crosshairs"></i></div>`,
                        iconSize: [34, 34],
                        iconAnchor: [17, 17]
                    });

                    L.marker([userLat, userLng], { icon: userIcon })
                        .addTo(map)
                        .bindPopup("<b>Your Current Location</b>")
                        .openPopup();

                    map.setView([userLat, userLng], 13);

                    // Compute distance for each doctor and update UI pills
                    const listContainer = document.getElementById("mapDoctorList");
                    const doctorElements = Array.from(document.querySelectorAll(".map-doc-tile"));

                    doctorElements.forEach(el => {
                        const docLat = parseFloat(el.getAttribute("data-lat"));
                        const docLng = parseFloat(el.getAttribute("data-lng"));
                        const docId = el.getAttribute("data-id");

                        if (docLat && docLng) {
                            const dist = calcDistance(userLat, userLng, docLat, docLng);
                            el.dataset.distance = dist;

                            const distPill = document.getElementById(`distPill-${docId}`);
                            if (distPill) {
                                distPill.innerHTML = `<i class="fas fa-location-arrow"></i> <strong>${dist} km</strong> away`;
                            }
                        }
                    });

                    // Sort list by proximity distance
                    doctorElements.sort((a, b) => parseFloat(a.dataset.distance || 9999) - parseFloat(b.dataset.distance || 9999));
                    doctorElements.forEach(el => listContainer.appendChild(el));
                },
                function (err) {
                    geoStatusText.innerHTML = `<i class="fas fa-circle-exclamation" style="color:#dc2626;"></i> Unable to retrieve location (${err.message})`;
                }
            );
        });
    }
});
