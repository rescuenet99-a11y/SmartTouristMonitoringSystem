const map = L.map('map').setView([13.0827, 80.2707], 15);

// OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

// Tourist Marker
let marker = L.marker([13.0827, 80.2707]).addTo(map);

// Route Polyline
let route = [];
let polyline = L.polyline(route, {
    color: 'blue',
    weight: 5
}).addTo(map);

// Socket Connection
const socket = io();

function updateLocation(position) {

    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
    const speed = position.coords.speed
        ? (position.coords.speed * 3.6).toFixed(2)
        : 0;

    document.getElementById("lat").innerHTML = lat.toFixed(6);
    document.getElementById("lng").innerHTML = lng.toFixed(6);
    document.getElementById("speed").innerHTML = speed + " km/h";
    document.getElementById("time").innerHTML =
        new Date().toLocaleTimeString();

    marker.setLatLng([lat, lng]);

    map.setView([lat, lng]);

    route.push([lat, lng]);

    polyline.setLatLngs(route);

    socket.emit("location_update", {
        latitude: lat,
        longitude: lng,
        speed: speed
    });

}

function showError(error){

    alert("GPS Permission Required");

}

if(navigator.geolocation){

    navigator.geolocation.watchPosition(

        updateLocation,

        showError,

        {
            enableHighAccuracy:true,
            maximumAge:0,
            timeout:5000
        }

    );

}
else{

    alert("Geolocation Not Supported");

}