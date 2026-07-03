import os
import random
from datetime import datetime
import mysql.connector
from flask import Flask, jsonify, request, send_from_directory, render_template

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip()

load_env()

# ────────────────────────────────────────────────────────────────────────
# TWILIO SMS CONFIGURATION
# Fill in your Twilio credentials below to enable real SMS alerts.
# Get free credentials at: https://www.twilio.com/try-twilio
# ────────────────────────────────────────────────────────────────────────
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')   # or paste directly
TWILIO_AUTH_TOKEN  = os.environ.get('TWILIO_AUTH_TOKEN',  '')   # or paste directly
TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER', '')   # e.g. '+15551234567'

TWILIO_ENABLED = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER)

# ────────────────────────────────────────────────────────────────────────
# MYSQL DATABASE CONFIGURATION
# ────────────────────────────────────────────────────────────────────────
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'tourist_safety')

def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

def get_sms_config():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sos_config WHERE id = 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row:
            return {
                "enabled": bool(row["enabled"]),
                "numbers": [n.strip() for n in row["numbers"].split(",") if n.strip()]
            }
    except Exception as e:
        print(f"Error fetching SMS config: {e}")
    return {"enabled": True, "numbers": ['+919876543210']}

def send_sms_alert(lat, lng):
    """Send SOS SMS to all family contacts via Twilio."""
    config = get_sms_config()
    if not config["enabled"]:
        return False, "SMS alerts disabled by user"
    if not TWILIO_ENABLED:
        # Print simulated SMS details to server logs
        print("\n" + "="*60)
        print("[SIMULATED SMS DELIVERED]")
        print(f"Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
        print(f"Location: {lat}, {lng}")
        print("To Contacts:")
        for num in config["numbers"]:
            print(f"  - {num}")
        print("-"*60)
        print(f"Message Body:\n[SOS EMERGENCY ALERT]\nYour family member needs help!\nLocation: {lat}, {lng}\nGoogle Maps: https://maps.google.com/?q={lat},{lng}\nPlease call emergency services: 112")
        print("="*60 + "\n")
        return True, "Simulated SMS Broadcasted"
    if not config["numbers"]:
        return False, "No phone numbers registered"
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        msg = (
            f"🚨 SOS EMERGENCY ALERT!\n"
            f"Your family member needs help!\n"
            f"📍 Location: {lat}, {lng}\n"
            f"Google Maps: https://maps.google.com/?q={lat},{lng}\n"
            f"⏰ Time: {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n"
            f"Please call emergency services: 112"
        )
        for number in config["numbers"]:
            client.messages.create(body=msg, from_=TWILIO_FROM_NUMBER, to=number)
        return True, f"SMS sent to {len(config['numbers'])} contact(s)"
    except Exception as e:
        return False, str(e)

app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_page(filename):
    if filename.endswith('.html'):
        return render_template(filename)
    return send_from_directory('.', filename)

# API Endpoints
@app.route('/api/sos', methods=['POST'])
def trigger_sos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch current location for defaults
    cursor.execute("SELECT * FROM location WHERE id = 1")
    loc = cursor.fetchone()
    
    data = request.get_json(silent=True) or {}
    lat = data.get('lat', loc['lat'] if loc else "48.8584°N")
    lng = data.get('lng', loc['lng'] if loc else "2.2945°E")

    # Send SMS via Twilio
    sms_success, sms_note = send_sms_alert(lat, lng)

    alert_id = f"SOS-{random.randint(10000, 99999)}"
    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # Insert notification
    cursor.execute("""
        INSERT INTO notifications (title, desc_text, icon_class, icon, time, unread)
        VALUES (%s, %s, %s, %s, %s, 1)
    """, (
        "🚨 SOS Alert Activated (You)",
        f"SOS triggered at {now_str}. SMS {'sent' if sms_success else 'not sent'} to family. Responders alerted.",
        "ni-sos",
        "bi-telephone-forward",
        "Just now"
    ))

    # Insert alert
    cursor.execute("""
        INSERT INTO alerts (type, desc_text, icon_class, icon, severity, severity_class, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        f"SOS Emergency – Alert ID: {alert_id}",
        f"Active SOS tracking from your device at {lat}, {lng}. Rescue teams routing to your GPS coordinates.",
        "icon-critical",
        "bi-telephone-forward",
        "Critical",
        "sev-critical",
        "Just now"
    ))

    # Insert incident
    cursor.execute("""
        INSERT INTO incidents (id, type, type_class, desc_text, priority, priority_class, status, status_class, time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        alert_id,
        "Emergency",
        "dot-emergency",
        f"User-triggered SOS Emergency Alert – Location: {lat}, {lng}",
        "High",
        "pri-high",
        "Open",
        "st-open",
        "Just now"
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "status": "success",
        "message": "SOS activated",
        "alert_id": alert_id,
        "sms_sent": sms_success,
        "sms_note": sms_note,
        "twilio_enabled": TWILIO_ENABLED,
        "timestamp": now_str
    })

@app.route('/api/location', methods=['GET', 'POST'])
def handle_location():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.json or {}
        cursor.execute("SELECT * FROM location WHERE id = 1")
        current_loc = cursor.fetchone()
        
        lat = data.get('lat', current_loc['lat'] if current_loc else '48.8584°N')
        lng = data.get('lng', current_loc['lng'] if current_loc else '2.2945°E')
        
        cursor.execute("""
            INSERT INTO location (id, lat, lng, accuracy, last_updated)
            VALUES (1, %s, %s, '±3m', 'Just now')
            ON DUPLICATE KEY UPDATE lat=%s, lng=%s, last_updated='Just now'
        """, (lat, lng, lat, lng))
        conn.commit()
        
    cursor.execute("SELECT * FROM location WHERE id = 1")
    loc = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not loc:
        loc = {
            "lat": "48.8584°N",
            "lng": "2.2945°E",
            "accuracy": "±3m",
            "last_updated": "Just now"
        }
    return jsonify(loc)

@app.route('/api/sos/config', methods=['GET', 'POST'])
def handle_sos_config():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        cursor.execute("SELECT * FROM sos_config WHERE id = 1")
        row = cursor.fetchone()
        
        enabled = int(data.get('enabled', row['enabled'] if row else 1))
        numbers_list = data.get('numbers', row['numbers'].split(',') if row else ['+919876543210'])
        numbers_str = ",".join(numbers_list)
        
        cursor.execute("""
            INSERT INTO sos_config (id, enabled, numbers)
            VALUES (1, %s, %s)
            ON DUPLICATE KEY UPDATE enabled=%s, numbers=%s
        """, (enabled, numbers_str, enabled, numbers_str))
        conn.commit()

    cursor.execute("SELECT * FROM sos_config WHERE id = 1")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not row:
        row = {"enabled": 1, "numbers": "+919876543210"}
        
    config = {
        "enabled": bool(row["enabled"]),
        "numbers": [n.strip() for n in row["numbers"].split(",") if n.strip()]
    }
    return jsonify(config)

@app.route('/api/family', methods=['GET', 'POST'])
def handle_family():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        name = data.get('name')
        location = data.get('location')
        if not name or not location:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Missing name or location"}), 400
        
        initials = "".join([part[0].upper() for part in name.split()[:2]]) if name else "FM"
        
        cursor.execute("SELECT COUNT(*) as count FROM family")
        count_row = cursor.fetchone()
        count = count_row['count'] if count_row else 0
        
        avatar_classes = ["avatar-blue", "avatar-pink", "avatar-green", "avatar-purple"]
        avatar_class = avatar_classes[count % len(avatar_classes)]

        distance = "Tracking live" if data.get('share_location', True) else "Location Hidden"
        share_location = int(data.get('share_location', True))
        proximity_alert = int(data.get('proximity_alert', True))

        cursor.execute("""
            INSERT INTO family (name, avatar, avatar_class, location, status, status_class, dot_class, distance, is_me, share_location, proximity_alert)
            VALUES (%s, %s, %s, %s, 'Safe', 'status-safe', 'dot-green', %s, 0, %s, %s)
        """, (name, initials, avatar_class, location, distance, share_location, proximity_alert))
        conn.commit()
        
        member_id = cursor.lastrowid
        cursor.execute("SELECT * FROM family WHERE id = %s", (member_id,))
        member = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if member:
            member['is_me'] = bool(member['is_me'])
            member['share_location'] = bool(member['share_location'])
            member['proximity_alert'] = bool(member['proximity_alert'])
        return jsonify({"status": "success", "member": member})
        
    cursor.execute("SELECT * FROM family ORDER BY id ASC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    for r in rows:
        r['is_me'] = bool(r['is_me'])
        r['share_location'] = bool(r['share_location'])
        r['proximity_alert'] = bool(r['proximity_alert'])
    return jsonify(rows)

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, type, desc_text as `desc`, icon_class, icon, severity, severity_class, time FROM alerts ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, desc_text as `desc`, icon_class, icon, time, unread FROM notifications ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    for r in rows:
        r['unread'] = bool(r['unread'])
    return jsonify(rows)

@app.route('/api/notifications/read-all', methods=['POST'])
def read_all_notifications():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET unread = 0")
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/incidents', methods=['GET', 'POST'])
def handle_incidents():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        incident_type = data.get('type')
        desc = data.get('desc')
        priority = data.get('priority')
        if not incident_type or not desc or not priority:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
        dot_classes = {
            "Emergency": "dot-emergency",
            "Safety": "dot-safety",
            "Medical": "dot-medical",
            "Theft": "dot-theft",
            "Other": "dot-other"
        }
        priority_classes = {
            "High": "pri-high",
            "Medium": "pri-medium",
            "Low": "pri-low"
        }
        
        cursor.execute("SELECT COUNT(*) as count FROM incidents")
        count_row = cursor.fetchone()
        count = count_row['count'] if count_row else 0
        incident_id = f"IR-{2062 + count}"
        
        cursor.execute("""
            INSERT INTO incidents (id, type, type_class, desc_text, priority, priority_class, status, status_class, time)
            VALUES (%s, %s, %s, %s, %s, %s, 'Open', 'st-open', 'Just now')
        """, (incident_id, incident_type, dot_classes.get(incident_type, "dot-other"), desc, priority, priority_classes.get(priority, "pri-low")))
        
        cursor.execute("""
            INSERT INTO notifications (title, desc_text, icon_class, icon, time, unread)
            VALUES (%s, %s, %s, %s, 'Just now', 1)
        """, (
            f"New {incident_type} Incident Filed",
            desc,
            "ni-alert" if priority == "High" else "ni-system",
            "bi-exclamation-triangle" if priority == "High" else "bi-info-circle"
        ))
        conn.commit()
        
        cursor.execute("SELECT id, type, type_class, desc_text as `desc`, priority, priority_class, status, status_class, time FROM incidents WHERE id = %s", (incident_id,))
        incident = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "incident": incident})
        
    cursor.execute("SELECT id, type, type_class, desc_text as `desc`, priority, priority_class, status, status_class, time FROM incidents ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as count FROM incidents WHERE status IN ('Open', 'In Progress')")
    active_incidents = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM alerts WHERE severity IN ('Critical', 'Warning')")
    alerts_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE unread = 1")
    unread_notifications = cursor.fetchone()['count']
    
    cursor.execute("SELECT title, time, desc_text as `desc` FROM notifications ORDER BY id DESC LIMIT 3")
    recent_notifications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "active_incidents": active_incidents,
        "responders": 45,
        "alerts": alerts_count,
        "unread_notifications": unread_notifications,
        "recent_activities": recent_notifications
    })

def init_db():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        cursor.close()
        conn.close()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS location (
                id INT PRIMARY KEY DEFAULT 1,
                lat VARCHAR(50) NOT NULL,
                lng VARCHAR(50) NOT NULL,
                accuracy VARCHAR(50) NOT NULL,
                last_updated VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS family (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                avatar VARCHAR(10) NOT NULL,
                avatar_class VARCHAR(50) NOT NULL,
                location VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL,
                status_class VARCHAR(50) NOT NULL,
                dot_class VARCHAR(50) NOT NULL,
                distance VARCHAR(100) NOT NULL,
                is_me BOOLEAN NOT NULL DEFAULT 0,
                share_location BOOLEAN NOT NULL DEFAULT 1,
                proximity_alert BOOLEAN NOT NULL DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type VARCHAR(255) NOT NULL,
                desc_text TEXT NOT NULL,
                icon_class VARCHAR(50) NOT NULL,
                icon VARCHAR(50) NOT NULL,
                severity VARCHAR(50) NOT NULL,
                severity_class VARCHAR(50) NOT NULL,
                time VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                desc_text TEXT NOT NULL,
                icon_class VARCHAR(50) NOT NULL,
                icon VARCHAR(50) NOT NULL,
                time VARCHAR(50) NOT NULL,
                unread BOOLEAN NOT NULL DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id VARCHAR(50) PRIMARY KEY,
                type VARCHAR(50) NOT NULL,
                type_class VARCHAR(50) NOT NULL,
                desc_text TEXT NOT NULL,
                priority VARCHAR(50) NOT NULL,
                priority_class VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                status_class VARCHAR(50) NOT NULL,
                time VARCHAR(50) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sos_config (
                id INT PRIMARY KEY DEFAULT 1,
                enabled BOOLEAN NOT NULL DEFAULT 1,
                numbers TEXT NOT NULL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM location")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO location (id, lat, lng, accuracy, last_updated) 
                VALUES (1, '48.8584°N', '2.2945°E', '±3m', 'Just now')
            """)

        cursor.execute("SELECT COUNT(*) FROM family")
        if cursor.fetchone()[0] == 0:
            family_seed = [
                (1, "Lakshmi Sri", "LS", "avatar-blue", "Eiffel Tower, Paris", "Safe", "status-safe", "dot-green", "0 km (You)", 1, 1, 1),
                (2, "Riya Sharma", "RS", "avatar-pink", "Louvre Museum, Paris", "Moving", "status-moving", "dot-blue", "2.4 km", 0, 1, 1),
                (3, "Arun Kumar", "AK", "avatar-green", "Champs-Élysées, Paris", "Safe", "status-safe", "dot-green", "3.1 km", 0, 1, 1),
                (4, "Priya Devi", "PD", "avatar-purple", "Last seen: Hotel Le Marais", "Offline", "status-offline", "dot-gray", "Last seen: 45 min ago", 0, 1, 1)
            ]
            cursor.executemany("""
                INSERT INTO family (id, name, avatar, avatar_class, location, status, status_class, dot_class, distance, is_me, share_location, proximity_alert)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, family_seed)

        cursor.execute("SELECT COUNT(*) FROM alerts")
        if cursor.fetchone()[0] == 0:
            alerts_seed = [
                (1, "Flash Flood Warning – Venice", "High water levels expected in the San Marco area. Tourists advised to evacuate immediately.", "icon-critical", "bi-exclamation-triangle", "Critical", "sev-critical", "12 min ago"),
                (2, "Security Threat – Central Station", "Unattended baggage reported near Platform 3. Security team dispatched.", "icon-critical", "bi-shield-exclamation", "Critical", "sev-critical", "28 min ago"),
                (3, "Severe Weather Advisory", "Thunderstorms expected across the Mediterranean coast from 2 PM to 8 PM.", "icon-warning", "bi-cloud-lightning", "Warning", "sev-warning", "1 hr ago"),
                (4, "Geo-fence Breach – Restricted Zone", "Tourist ID #4582 entered restricted archaeological area near Pompeii.", "icon-warning", "bi-geo-fill", "Warning", "sev-warning", "2 hrs ago"),
                (5, "System Maintenance Scheduled", "GPS tracking module upgrade planned for tonight 2 AM – 4 AM UTC.", "icon-info", "bi-info-circle", "Info", "sev-info", "3 hrs ago"),
                (6, "All Clear – Rome Zone A", "Previous crowd congestion alert has been resolved. Normal operations resumed.", "icon-low", "bi-check-circle", "Resolved", "sev-low", "5 hrs ago")
            ]
            cursor.executemany("""
                INSERT INTO alerts (id, type, desc_text, icon_class, icon, severity, severity_class, time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, alerts_seed)

        cursor.execute("SELECT COUNT(*) FROM notifications")
        if cursor.fetchone()[0] == 0:
            notifications_seed = [
                (1, "SOS Alert Triggered", "Tourist John Doe activated SOS near Eiffel Tower. Emergency responders dispatched.", "ni-sos", "bi-telephone-forward", "2 min ago", 1),
                (2, "Flash Flood Warning", "High water levels expected in Venice San Marco area. Evacuation advisory issued.", "ni-alert", "bi-exclamation-triangle", "15 min ago", 1),
                (3, "Family Member Offline", "Priya Devi has been offline for 45 minutes. Last known location: Hotel Le Marais.", "ni-family", "bi-people", "45 min ago", 1),
                (4, "Geo-fence Breach Detected", "Tourist ID #4582 entered restricted area near Pompeii archaeological site.", "ni-location", "bi-geo-alt", "2 hrs ago", 0),
                (5, "Weather Advisory Updated", "Thunderstorm warning extended until 10 PM for Mediterranean coastal regions.", "ni-alert", "bi-cloud-lightning", "3 hrs ago", 0),
                (6, "System Maintenance Complete", "GPS tracking module upgrade completed successfully. All systems operational.", "ni-system", "bi-gear", "6 hrs ago", 0),
                (7, "Daily Report Generated", "Your daily safety summary for June 30 is now available in Incident Reports.", "ni-system", "bi-bar-chart", "8 hrs ago", 0),
                (8, "Location Sharing Enabled", "Your live location is now being shared with 3 family members.", "ni-location", "bi-check-circle", "1 day ago", 0)
            ]
            cursor.executemany("""
                INSERT INTO notifications (id, title, desc_text, icon_class, icon, time, unread)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, notifications_seed)

        cursor.execute("SELECT COUNT(*) FROM incidents")
        if cursor.fetchone()[0] == 0:
            incidents_seed = [
                ("IR-2061", "Emergency", "dot-emergency", "Tourist fell near Cliffside trail – requires medical evacuation", "High", "pri-high", "Open", "st-open", "Jul 1, 10:12"),
                ("IR-2060", "Theft", "dot-theft", "Wallet stolen near Central Market – police notified", "Medium", "pri-medium", "In Progress", "st-progress", "Jul 1, 09:30"),
                ("IR-2059", "Safety", "dot-safety", "Broken railing on observation deck – maintenance dispatched", "High", "pri-high", "In Progress", "st-progress", "Jun 30, 16:45"),
                ("IR-2058", "Medical", "dot-medical", "Tourist experienced heat exhaustion at beach area", "Medium", "pri-medium", "Resolved", "st-resolved", "Jun 30, 14:22"),
                ("IR-2057", "Other", "dot-other", "Lost ID card reported at airport information desk", "Low", "pri-low", "Resolved", "st-resolved", "Jun 30, 11:00"),
                ("IR-2056", "Emergency", "dot-emergency", "Group of hikers stranded due to sudden weather change", "High", "pri-high", "Closed", "st-closed", "Jun 29, 18:30")
            ]
            cursor.executemany("""
                INSERT INTO incidents (id, type, type_class, desc_text, priority, priority_class, status, status_class, time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, incidents_seed)

        cursor.execute("SELECT COUNT(*) FROM sos_config")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO sos_config (id, enabled, numbers)
                VALUES (1, 1, '+919876543210')
            """)

        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5000)
