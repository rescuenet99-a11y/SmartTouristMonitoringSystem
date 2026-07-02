from flask_socketio import emit
from database import mysql
from services.geofence import check_geofence
from services.risk_detector import check_risk_zone


def register_socket_events(socketio):

    @socketio.on("connect")
    def connect():
        print("Client Connected")

    @socketio.on("disconnect")
    def disconnect():
        print("Client Disconnected")

    @socketio.on("location_update")
    def location_update(data):

        latitude = data["latitude"]
        longitude = data["longitude"]
        speed = data["speed"]

        cursor = mysql.connection.cursor()

        cursor.execute("""
        INSERT INTO location_history
        (tourist_id, latitude, longitude, speed)
        VALUES (%s,%s,%s,%s)
        """,

        (1, latitude, longitude, speed))

        mysql.connection.commit()

        cursor.close()

        geofence = check_geofence(latitude, longitude)

        risk = check_risk_zone(latitude, longitude)

        emit("tracking_update",{

            "latitude":latitude,
            "longitude":longitude,
            "speed":speed,
            "geofence":geofence,
            "risk":risk

        },broadcast=True)