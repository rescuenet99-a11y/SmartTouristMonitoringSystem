let watchId = null;

function getLocation() {

    if (navigator.geolocation) {

        watchId = navigator.geolocation.watchPosition(
            showPosition,
            showError,
            {
                enableHighAccuracy: true,
                maximumAge: 0,
                timeout: 5000
            }
        );

    } else {

        alert("Geolocation is not supported by this browser.");

    }
}

function showPosition(position) {

    document.getElementById("lat").innerHTML =
        position.coords.latitude.toFixed(6);

    document.getElementById("lon").innerHTML =
        position.coords.longitude.toFixed(6);

    document.getElementById("status").innerHTML =
        "🟢 Live Tracking Running";
}

function showError(error) {

    switch(error.code) {
        case error.PERMISSION_DENIED:
            document.getElementById("status").innerHTML = "❌ Location permission denied";
            break;
        case error.POSITION_UNAVAILABLE:
            document.getElementById("status").innerHTML = "❌ Location unavailable";
            break;
        case error.TIMEOUT:
            document.getElementById("status").innerHTML = "❌ Request timed out";
            break;
        default:
            document.getElementById("status").innerHTML = "❌ Unknown error";
    }
}

function stopTracking() {

    if (watchId !== null) {

        navigator.geolocation.clearWatch(watchId);

        document.getElementById("status").innerHTML =
            "🔴 Tracking Stopped";
    }

}