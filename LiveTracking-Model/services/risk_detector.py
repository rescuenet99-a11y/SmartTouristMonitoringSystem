from geopy.distance import geodesic
from database import mysql

def check_risk_zone(latitude, longitude):

    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT zone_name,
               latitude,
               longitude,
               radius,
               risk_level
        FROM risk_zones
    """)

    zones = cursor.fetchall()

    cursor.close()

    current = (float(latitude), float(longitude))

    for zone in zones:

        zone_name = zone[0]
        zone_lat = float(zone[1])
        zone_lng = float(zone[2])
        radius = float(zone[3])
        risk = zone[4]

        distance = geodesic(
            current,
            (zone_lat, zone_lng)
        ).meters

        if distance <= radius:

            return {

                "risk":risk,

                "name":zone_name

            }

    return {

        "risk":"LOW",

        "name":"Safe Area"

    }