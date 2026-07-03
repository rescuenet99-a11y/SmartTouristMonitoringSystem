from geopy.distance import geodesic
from database import mysql

def check_geofence(latitude, longitude):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT zone_name, latitude, longitude, radius, zone_type
        FROM geofence
    """)

    zones = cursor.fetchall()

    cursor.close()

    current = (float(latitude), float(longitude))

    for zone in zones:

        zone_name = zone[0]
        zone_lat = float(zone[1])
        zone_lng = float(zone[2])
        radius = float(zone[3])
        zone_type = zone[4]

        distance = geodesic(
            current,
            (zone_lat, zone_lng)
        ).meters

        if distance <= radius:

            return zone_type

    return "OUTSIDE SAFE ZONE"