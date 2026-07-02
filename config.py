import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Santhavi@0803",
        database="TouristSafetyDB"
    )
    return connection