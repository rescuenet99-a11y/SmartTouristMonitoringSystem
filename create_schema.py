import os
import mysql.connector

# Load DB config from environment (same as app.py)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "intern26AI@"),
    "database": os.getenv("DB_NAME", "smart_tourist_db"),
}

def exec_sql(cursor, sql):
    try:
        cursor.execute(sql)
    except mysql.connector.Error as e:
        print(f"SQL error [{sql[:30]}...]: {e}")
        raise

def main():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    # Ensure tables exist
    create_statements = [
        """
        CREATE TABLE IF NOT EXISTS Tourist (
            tourist_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            latitude DOUBLE NOT NULL,
            longitude DOUBLE NOT NULL,
            status VARCHAR(50) NOT NULL,
            destination VARCHAR(255),
            safety_score FLOAT,
            registration_date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Incidents (
            incident_id INT AUTO_INCREMENT PRIMARY KEY,
            tourist_name VARCHAR(255),
            description TEXT,
            risk_level VARCHAR(50),
            status VARCHAR(50),
            incident_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Alerts (
            alert_id INT AUTO_INCREMENT PRIMARY KEY,
            tourist_name VARCHAR(255),
            alert_type VARCHAR(100),
            alert_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS Risk_Zones (
            zone_id INT AUTO_INCREMENT PRIMARY KEY,
            risk_level VARCHAR(50) NOT NULL,
            description TEXT
        )
        """
    ]
    for stmt in create_statements:
        exec_sql(cursor, stmt)
    conn.commit()
    # Insert sample rows if tables are empty
    def table_empty(name):
        cursor.execute(f"SELECT COUNT(*) FROM {name}")
        return cursor.fetchone()[0] == 0
    if table_empty('Tourist'):
        cursor.execute(
            "INSERT INTO Tourist (name, latitude, longitude, status, destination, safety_score) "
            "VALUES ('Alice', 12.34, 56.78, 'Active', 'Museum', 85)"
        )
    if table_empty('Incidents'):
        cursor.execute(
            "INSERT INTO Incidents (tourist_name, description, risk_level, status) "
            "VALUES ('Alice', 'Lost in market', 'Medium', 'Open')"
        )
    if table_empty('Alerts'):
        cursor.execute(
            "INSERT INTO Alerts (tourist_name, alert_type, status) "
            "VALUES ('Alice', 'SOS', 'Pending')"
        )
    if table_empty('Risk_Zones'):
        cursor.execute(
            "INSERT INTO Risk_Zones (risk_level, description) "
            "VALUES ('High', 'High risk area near river')"
        )
    conn.commit()
    cursor.close()
    conn.close()
    print('Database schema created and sample data inserted.')

if __name__ == '__main__':
    main()
