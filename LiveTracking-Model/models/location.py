from database import mysql

class Location:

    @staticmethod
    def save_location(tourist_id, lat, lng, speed):

        cursor = mysql.connection.cursor()

        cursor.execute("""

        INSERT INTO location_history

        (tourist_id,latitude,longitude,speed)

        VALUES(%s,%s,%s,%s)

        """,(tourist_id,lat,lng,speed))

        mysql.connection.commit()

        cursor.close()