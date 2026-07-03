console.log("heatmaps.js loaded");

function initHeatmap() {

    const map = L.map("map").setView([13.0827, 80.2707], 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    // Sample tourist locations
    const tourists = [
        {
            name: "John",
            lat: 13.0827,
            lng: 80.2707,
            status: "Safe"
        },
        {
            name: "Maria",
            lat: 12.9716,
            lng: 77.5946,
            status: "SOS Alert"
        },
        {
            name: "David",
            lat: 11.0168,
            lng: 76.9558,
            status: "Missing Tourist"
        },
        {
            name: "Alex",
            lat: 9.9252,
            lng: 78.1198,
            status: "High Risk"
        }
    ];

    tourists.forEach(t => {
        L.marker([t.lat, t.lng])
            .addTo(map)
            .bindPopup(
                "<b>" + t.name + "</b><br>Status : " + t.status
            );
    });

    // Heatmap layer
    const heatData = [
        [13.0827,80.2707,0.9],
        [13.05,80.25,0.8],
        [12.9716,77.5946,0.7],
        [11.0168,76.9558,0.6],
        [9.9252,78.1198,1.0]
    ];

    L.heatLayer(heatData,{
        radius:25,
        blur:20,
        maxZoom:17
    }).addTo(map);
}

document.addEventListener("DOMContentLoaded", initHeatmap);