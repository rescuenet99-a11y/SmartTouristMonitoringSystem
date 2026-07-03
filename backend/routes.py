from flask import Blueprint, request, jsonify
from datetime import datetime

# Define a Blueprint for our routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# IN-MEMORY STORAGE FOR DEMO PURPOSES (Replaces MySQL database)
TRIPS_DB = []
TRIP_ID_COUNTER = 1

@api_bp.route('/trips', methods=['GET'])
def get_trips():
    """
    Retrieve all trips from the in-memory database.
    Returns:
        JSON list of all trips, sorted chronologically by start date.
    """
    try:
        # Sort trips by startDate chronologically
        sorted_trips = sorted(TRIPS_DB, key=lambda t: t['startDate'])
        return jsonify(sorted_trips), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch trips", "details": str(e)}), 500


@api_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """
    Retrieve a single trip by its unique ID.
    """
    try:
        trip = next((t for t in TRIPS_DB if t['id'] == trip_id), None)
        if trip:
            return jsonify(trip), 200
        return jsonify({"error": f"Trip with ID {trip_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to fetch trip", "details": str(e)}), 500


@api_bp.route('/trips', methods=['POST'])
def create_trip():
    """
    Create a new trip in the in-memory database.
    Expects request body with:
        destination (str), startDate (str, YYYY-MM-DD), endDate (str, YYYY-MM-DD),
        time (str, e.g. HH:MM), transport (str), notes (str, optional), budget (float, optional)
    """
    global TRIP_ID_COUNTER
    data = request.get_json() or {}

    # Basic validations
    required_fields = ['destination', 'startDate', 'endDate', 'time', 'transport']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            "error": "Bad Request",
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }), 400

    try:
        # Validate date formats and logic
        start_dt = datetime.strptime(data['startDate'], '%Y-%m-%d').date()
        end_dt = datetime.strptime(data['endDate'], '%Y-%m-%d').date()

        if start_dt > end_dt:
            return jsonify({
                "error": "Bad Request",
                "message": "Start Date cannot be after End Date."
            }), 400

        # Create new trip dict
        new_trip = {
            "id": TRIP_ID_COUNTER,
            "destination": data['destination'].strip(),
            "startDate": data['startDate'],
            "endDate": data['endDate'],
            "time": data['time'],
            "transport": data['transport'],
            "notes": data.get('notes', '').strip(),
            "budget": float(data.get('budget', 0.0))
        }

        TRIPS_DB.append(new_trip)
        TRIP_ID_COUNTER += 1

        return jsonify(new_trip), 201

    except ValueError:
        return jsonify({
            "error": "Bad Request",
            "message": "Invalid date format. Use YYYY-MM-DD."
        }), 400
    except Exception as e:
        return jsonify({"error": "Failed to create trip", "details": str(e)}), 500


@api_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    """
    Update details of an existing trip.
    """
    data = request.get_json() or {}
    
    # Find the trip
    trip_idx = next((i for i, t in enumerate(TRIPS_DB) if t['id'] == trip_id), None)
    if trip_idx is None:
        return jsonify({"error": f"Trip with ID {trip_id} not found"}), 404

    trip = TRIPS_DB[trip_idx]

    try:
        if 'destination' in data: trip['destination'] = data['destination'].strip()
        if 'startDate' in data: trip['startDate'] = data['startDate']
        if 'endDate' in data: trip['endDate'] = data['endDate']
        
        # Re-check date logic
        start_dt = datetime.strptime(trip['startDate'], '%Y-%m-%d').date()
        end_dt = datetime.strptime(trip['endDate'], '%Y-%m-%d').date()
        if start_dt > end_dt:
            return jsonify({
                "error": "Bad Request",
                "message": "Start Date cannot be after End Date."
            }), 400

        if 'time' in data: trip['time'] = data['time']
        if 'transport' in data: trip['transport'] = data['transport']
        if 'notes' in data: trip['notes'] = data['notes'].strip()
        if 'budget' in data: trip['budget'] = float(data['budget'])

        TRIPS_DB[trip_idx] = trip
        return jsonify(trip), 200

    except ValueError:
        return jsonify({
            "error": "Bad Request",
            "message": "Invalid date format. Use YYYY-MM-DD."
        }), 400
    except Exception as e:
        return jsonify({"error": f"Failed to update trip {trip_id}", "details": str(e)}), 500


@api_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    """
    Delete a trip from the in-memory database.
    """
    global TRIPS_DB
    
    trip_exists = any(t['id'] == trip_id for t in TRIPS_DB)
    if not trip_exists:
        return jsonify({"error": f"Trip with ID {trip_id} not found"}), 404

    try:
        TRIPS_DB = [t for t in TRIPS_DB if t['id'] != trip_id]
        return jsonify({
            "message": "Trip successfully deleted",
            "deleted_id": trip_id
        }), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete trip {trip_id}", "details": str(e)}), 500
