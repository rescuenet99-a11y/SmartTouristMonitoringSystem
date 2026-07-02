from flask import Flask, render_template, request
from config import get_db_connection
import random

app = Flask(__name__)


# ===========================
# HOME PAGE
# ===========================

@app.route("/")
def home():
    return render_template("index.html")


# ===========================
# REGISTER TOURIST
# ===========================

@app.route("/register", methods=["POST"])
def register():

    tourist_id = "TID" + str(random.randint(100000, 999999))

    full_name = request.form["full_name"]
    gender = request.form["gender"]
    age = request.form["age"]
    phone = request.form["phone"]
    email = request.form["email"]

    source_location = request.form["source_location"]
    destination = request.form["destination"]
    travel_date = request.form["travel_date"]
    duration = request.form["duration"]

    transport_mode = request.form["transport_mode"]

    emergency_contact_name = request.form["emergency_contact_name"]
    relationship = request.form["relationship"]
    emergency_contact_number = request.form["emergency"]

    # Distance & Estimated Time
    distance = request.form.get("distance", "")
    estimated_time = request.form.get("estimated_time", "")

    connection = get_db_connection()

    cursor = connection.cursor()

    sql = """

    INSERT INTO tourists
    (
        tourist_id,
        full_name,
        gender,
        age,
        phone_number,
        email,
        source_location,
        destination,
        travel_date,
        travel_duration,
        transport_mode,
        distance,
        estimated_time,
        emergency_contact_name,
        relationship,
        emergency_contact_number
    )
    VALUES
    (
        %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s
    )
    """

    values = (
        tourist_id,
        full_name,
        gender,
        age,
        phone,
        email,
        source_location,
        destination,
        travel_date,
        duration,
        transport_mode,
        distance,
        estimated_time,
        emergency_contact_name,
        relationship,
        emergency_contact_number
    )

    cursor.execute(sql, values)

    connection.commit()

    cursor.close()

    connection.close()

    return f"""
    
    <!DOCTYPE html>
    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Registration Successful</title>

        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="background:#eef4ff;">

        <div class="container mt-5">

            <div class="card shadow-lg border-0 mx-auto"
                 style="max-width:700px; border-radius:20px;">

                <div class="card-body text-center p-5">

                    <h1 class="text-success">

                        ✅ Tourist Registered Successfully

                    </h1>

                    <hr>

                    <h4 class="mt-4">

                        Tourist ID

                    </h4>

                    <h2 class="text-primary">

                        {tourist_id}

                    </h2>

                    <br>

                    <a href="/"
                       class="btn btn-primary btn-lg">

                        Register Another Tourist

                    </a>

                </div>

            </div>

        </div>

    </body>

    </html>
    """


# ===========================
# RUN APPLICATION
# ===========================

if __name__ == "__main__":

    app.run(debug=True)