console.log("heatmaps.js loaded");

function initHeatmap() {

    const map = L.map("map").setView([13.0827, 80.2707], 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    // Fetch tourist locations from backend API
    fetch('/api/tourist_locations')
        .then(response => response.json())
        .then(data => {
            // Data format: [{id, name, latitude, longitude, status}, ...]
            const tourists = data.map(item => ({
                name: item.name,
                lat: item.latitude,
                lng: item.longitude,
                status: item.status
            }));

            // Add markers for each tourist
            tourists.forEach(t => {
                L.marker([t.lat, t.lng])
                    .addTo(map)
                    .bindPopup(`<b>${t.name}</b><br>Status : ${t.status}`);
            });

            // Prepare heatmap data (intensity set to 0.9)
            const heatData = tourists.map(t => [t.lat, t.lng, 0.9]);

            // Add heatmap layer if there is data
            if (heatData.length) {
                L.heatLayer(heatData, {
                    radius: 25,
                    blur: 20,
                    maxZoom: 17
                }).addTo(map);
            }
        })
        .catch(err => {
            console.error('Failed to load tourist locations:', err);
        });
}

document.addEventListener("DOMContentLoaded", initHeatmap);