from flask import Flask, render_template, request
from config import get_db_connection

from geopy.distance import geodesic
import folium
import os

app = Flask(__name__)


# ==========================
# HOME PAGE
# ==========================

@app.route("/")
def home():
    return render_template("zone.html")


# ==========================
# CHECK ZONE
# ==========================

@app.route("/check_zone", methods=["POST"])
def check_zone():

    try:

        latitude = float(request.form["latitude"])
        longitude = float(request.form["longitude"])

    except:

        return "Invalid Latitude or Longitude."

    user_location = (latitude, longitude)

    connection = get_db_connection()

    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM risk_zones")

    zones = cursor.fetchall()

    nearest_zone = None

    nearest_distance = float("inf")

    selected_zone = None

        # ==========================
    # CHECK EVERY RISK ZONE
    # ==========================

    for zone in zones:

        zone_location = (

            zone["latitude"],

            zone["longitude"]

        )

        distance = geodesic(

            user_location,

            zone_location

        ).meters

        # Find nearest zone

        if distance < nearest_distance:

            nearest_distance = distance

            nearest_zone = zone

        # Check whether tourist entered zone

        if distance <= zone["radius"]:

            selected_zone = zone

            break


    # ==========================
    # DECIDE RISK LEVEL
    # ==========================

    if selected_zone:

        zone_name = selected_zone["zone_name"]

        risk_level = selected_zone["risk_level"]

    else:

        zone_name = "Unknown Area"

        risk_level = "Safe"


    # ==========================
    # SAVE HISTORY
    # ==========================

    cursor.execute("""

        INSERT INTO zone_history

        (

        zone_name,

        risk_level,

        latitude,

        longitude

        )

        VALUES

        (%s,%s,%s,%s)

    """,

    (

        zone_name,

        risk_level,

        latitude,

        longitude

    ))

    connection.commit()

        # ==========================
    # CREATE FOLIUM MAP
    # ==========================

    tourist_map = folium.Map(

        location=user_location,

        zoom_start=15

    )

    # Tourist Marker

    folium.Marker(

        location=user_location,

        popup="Tourist Current Location",

        tooltip="You are Here",

        icon=folium.Icon(
            color="blue",
            icon="info-sign"
        )

    ).add_to(tourist_map)


    # Add Nearest Zone Marker

    if nearest_zone:

        folium.Marker(

            location=(

                nearest_zone["latitude"],

                nearest_zone["longitude"]

            ),

            popup=nearest_zone["zone_name"],

            tooltip=nearest_zone["risk_level"],

            icon=folium.Icon(
                color="red",
                icon="info-sign"
            )

        ).add_to(tourist_map)


        # Risk Zone Circle

        folium.Circle(

            location=(

                nearest_zone["latitude"],

                nearest_zone["longitude"]

            ),

            radius=nearest_zone["radius"],

            color="red",

            fill=True,

            fill_color="red",

            fill_opacity=0.3,

            popup="Risk Zone Radius"

        ).add_to(tourist_map)


    # ==========================
    # SAVE MAP
    # ==========================

    os.makedirs("static/maps", exist_ok=True)

    map_path = "static/maps/tourist_map.html"

    tourist_map.save(map_path)

        # ==========================
    # CLOSE DATABASE
    # ==========================

    cursor.close()

    connection.close()


    # ==========================
    # SHOW RESULT PAGE
    # ==========================

    return render_template(

        "result.html",

        zone_name=zone_name,

        risk_level=risk_level,

        latitude=latitude,

        longitude=longitude,

        distance=round(nearest_distance, 2),

        nearest_zone=nearest_zone["zone_name"] if nearest_zone else "None",

        map_file="maps/tourist_map.html"

    )


# ==========================
# RUN FLASK
# ==========================

if __name__ == "__main__":

    app.run(
        debug=True
    )