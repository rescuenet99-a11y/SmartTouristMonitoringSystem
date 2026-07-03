from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for, flash
import os
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "smart_tourist_secret_key_2026"

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

# ------------------------------------------------------------
# Tourist Registration page
# ------------------------------------------------------------
from flask import request, redirect, url_for, flash
import hashlib

def execute_db(query, params=None):
    """Execute a non-SELECT query (INSERT/UPDATE/DELETE) using the existing DB config."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params or ())
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def ensure_tourist_columns():
    """Ensure required columns exist in Tourist table, adding them if missing."""
    required = {
        'email': "VARCHAR(255) UNIQUE",
        'phone': "VARCHAR(20)",
        'password_hash': "VARCHAR(64)",
        'destination': "VARCHAR(255)"
    }
    for col, definition in required.items():
        # Check column existence
        check_sql = (
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'Tourist' AND COLUMN_NAME = %s"
        )
        rows = query_db(check_sql, (DB_CONFIG['database'], col))
        if not rows:
            # Add column
            alter_sql = f"ALTER TABLE Tourist ADD COLUMN {col} {definition}"
            try:
                execute_db(alter_sql)
                print(f"Added missing column {col} to Tourist table.")
            except Exception as e:
                print(f"Failed to add column {col}: {e}")

# Call ensure_tourist_columns at module load to prepare schema
ensure_tourist_columns()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        destination = request.form.get('destination')
        # Simple hash for demonstration (not production ready)
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest() if password else ''
        # Ensure required columns exist (add if missing)
        # Add email, phone, password_hash, destination if they do not exist
        try:
            # Try inserting with all fields; missing columns will raise an error which we catch
            insert_sql = """
                INSERT INTO Tourist (name, email, phone, password_hash, destination, latitude, longitude, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            execute_db(insert_sql, (name, email, phone, password_hash, destination, 0, 0, 'Active'))
        except Exception as e:
            # Attempt to add missing columns dynamically
            missing_cols = []
            if 'email' in str(e).lower():
                missing_cols.append("email VARCHAR(255)")
            if 'phone' in str(e).lower():
                missing_cols.append("phone VARCHAR(50)")
            if 'password_hash' in str(e).lower():
                missing_cols.append("password_hash VARCHAR(64)")
            if 'destination' in str(e).lower():
                missing_cols.append("destination VARCHAR(255)")
            for col_def in missing_cols:
                try:
                    alter_sql = f"ALTER TABLE Tourist ADD COLUMN {col_def}"
                    execute_db(alter_sql)
                except Exception:
                    pass  # ignore if already added
            # Retry insert after adding columns
            execute_db(insert_sql, (name, email, phone, password_hash, destination, 0, 0, 'Active'))
        flash('Tourist registered successfully!', 'success')
        return redirect(url_for('register'))
    # GET request – render registration form
    return render_template('registration.html')

# ------------------------------------------------------------
# Tourist Login page
# ------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest() if password else ''
        # Try to fetch stored hash; add column if missing
        try:
            rows = query_db('SELECT tourist_id, name, password_hash FROM Tourist WHERE email = %s', (email,))
        except Exception as e:
            if 'password_hash' in str(e).lower():
                execute_db('ALTER TABLE Tourist ADD COLUMN password_hash VARCHAR(64)')
                rows = query_db('SELECT tourist_id, name, password_hash FROM Tourist WHERE email = %s', (email,))
            else:
                rows = []
        if rows and rows[0].get('password_hash') == password_hash:
            flash(f"Welcome back, {rows[0].get('name')}!", 'success')
            return redirect(url_for('update_location', tourist_id=rows[0].get('tourist_id')))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')
    # ------------------------------------------------------------
# Tourist location update after login
# ------------------------------------------------------------

@app.route('/update_location/<int:tourist_id>', methods=['GET'])
def update_location(tourist_id):
    return render_template('location.html', tourist_id=tourist_id)

@app.route('/api/update_location', methods=['POST'])
def api_update_location():
    data = request.get_json()
    tourist_id = data.get('tourist_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    try:
        execute_db('UPDATE Tourist SET latitude=%s, longitude=%s WHERE tourist_id=%s', (latitude, longitude, tourist_id))
    except Exception as e:
        # Add missing columns if needed
        if 'latitude' in str(e).lower():
            execute_db('ALTER TABLE Tourist ADD COLUMN latitude DOUBLE')
        if 'longitude' in str(e).lower():
            execute_db('ALTER TABLE Tourist ADD COLUMN longitude DOUBLE')
        # Retry update
        execute_db('UPDATE Tourist SET latitude=%s, longitude=%s WHERE tourist_id=%s', (latitude, longitude, tourist_id))
    return jsonify({'status': 'ok'})

# ------------------------------------------------------------
# End of location update routes

# Removed stray return statement


# Serve static files (Flask does this automatically under /static)

if __name__ == '__main__':
    # Enable debug for development; production will use a proper WSGI server.
    app.run(debug=True, host='0.0.0.0', port=5000)
