import os
import mysql.connector

# Load .env
env_path = '.env'
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                os.environ[key.strip()] = val.strip()

host = os.environ.get('MYSQL_HOST', 'localhost')
user = os.environ.get('MYSQL_USER', 'root')
pw = os.environ.get('MYSQL_PASSWORD', '')
db = os.environ.get('MYSQL_DATABASE', 'tourist_safety')

print(f"Attempting to connect to MySQL at {host} as {user}...")
try:
    # 1. Test basic connection
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=pw
    )
    print("[SUCCESS] Connection to MySQL Server: SUCCESSFUL!")
    
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    dbs = [d[0] for d in cursor.fetchall()]
    
    if db in dbs:
        print(f"[SUCCESS] Target Database '{db}': EXISTS")
        # Connect to the database and check tables
        conn.close()
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=pw,
            database=db
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"[INFO] Tables present: {', '.join(tables) if tables else 'None'}")
    else:
        print(f"[INFO] Target Database '{db}' does not exist yet. It will be automatically created when you start 'app.py'.")
        
    conn.close()
except mysql.connector.Error as err:
    print(f"[ERROR] Connection Failed: {err}")
