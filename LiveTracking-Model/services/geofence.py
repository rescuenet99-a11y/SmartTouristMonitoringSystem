from geopy.distance import geodesic

SAFE_ZONE = (13.0827, 80.2707)
SAFE_RADIUS = 500   # meters


def check_geofence(latitude, longitude):

    current = (latitude, longitude)

    distance = geodesic(current, SAFE_ZONE).meters

    if distance <= SAFE_RADIUS:
        return "SAFE"

    return "OUTSIDE"