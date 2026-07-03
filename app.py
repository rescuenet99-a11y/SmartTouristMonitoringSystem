from flask import Flask, render_template, send_from_directory, jsonify
import os
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database connection helper (reuse project settings)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "intern26AI@"),
    "database": os.getenv("DB_NAME", "smart_tourist_db")
}

def get_connection():
    """Create and return a new MySQL connection using project config."""
    print(DB_CONFIG)
    return mysql.connector.connect(**DB_CONFIG)

def query_db(query, params=None):
    """Execute a SELECT query and return list of dict rows."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()

# Routes for each dashboard page
@app.route('/')
def home():
    # Redirect to admin dashboard as default
    return render_template('admin_dashboard.html')

@app.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/tourist')
def tourist_dashboard():
    return render_template('tourist_dashboard.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/heatmaps')
def heatmaps():
    return render_template('heatmaps.html')

@app.route('/api/tourist_locations')
def api_tourist_locations():
    rows = query_db('SELECT tourist_id AS id, name, latitude, longitude, status FROM Tourist')
    return jsonify(rows)

@app.route('/reports')
def reports():
    return render_template('reports.html')

# Serve static files (Flask does this automatically under /static)

if __name__ == '__main__':
    # Enable debug for development; production will use a proper WSGI server.
    app.run(debug=True, host='0.0.0.0', port=5000)
