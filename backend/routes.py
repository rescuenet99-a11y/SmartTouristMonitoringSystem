from flask import Blueprint, request, jsonify
from datetime import datetime
from database import db
from models import Trip

# Define a Blueprint for our routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/trips', methods=['GET'])
def get_trips():
    """
    Retrieve all trips from the database.
    Returns:
        JSON list of all trips, sorted chronologically by start date.
    """
    try:
        # Sort trips by startDate chronologically
        trips = Trip.query.order_by(Trip.start_date.asc()).all()
        return jsonify([trip.to_dict() for trip in trips]), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch trips", "details": str(e)}), 500


@api_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """
    Retrieve a single trip by its unique ID.
    """
    try:
        trip = db.session.get(Trip, trip_id)
        if trip:
            return jsonify(trip.to_dict()), 200
        return jsonify({"error": f"Trip with ID {trip_id} not found"}), 404
    except Exception as e:
        return jsonify({"error": "Failed to fetch trip", "details": str(e)}), 500


@api_bp.route('/trips', methods=['POST'])
def create_trip():
    """
    Create a new trip in the database.
    Expects request body with:
        destination (str), startDate (str, YYYY-MM-DD), endDate (str, YYYY-MM-DD),
        time (str, e.g. HH:MM), transport (str), notes (str, optional), budget (float, optional)
    """
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

        # Create new trip model instance
        new_trip = Trip(
            destination=data['destination'].strip(),
            start_date=start_dt,
            end_date=end_dt,
            time=data['time'],
            transport=data['transport'],
            notes=data.get('notes', '').strip(),
            budget=float(data.get('budget', 0.0))
        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify(new_trip.to_dict()), 201

    except ValueError:
        return jsonify({
            "error": "Bad Request",
            "message": "Invalid date format. Use YYYY-MM-DD."
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create trip", "details": str(e)}), 500


@api_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def update_trip(trip_id):
    """
    Update details of an existing trip.
    """
    data = request.get_json() or {}
    
    try:
        # Find the trip
        trip = db.session.get(Trip, trip_id)
        if not trip:
            return jsonify({"error": f"Trip with ID {trip_id} not found"}), 404

        if 'destination' in data: 
            trip.destination = data['destination'].strip()
            
        if 'startDate' in data or 'endDate' in data:
            start_str = data.get('startDate', trip.start_date.strftime('%Y-%m-%d'))
            end_str = data.get('endDate', trip.end_date.strftime('%Y-%m-%d'))
            
            # Re-check date logic
            start_dt = datetime.strptime(start_str, '%Y-%m-%d').date()
            end_dt = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            if start_dt > end_dt:
                return jsonify({
                    "error": "Bad Request",
                    "message": "Start Date cannot be after End Date."
                }), 400
                
            trip.start_date = start_dt
            trip.end_date = end_dt

        if 'time' in data: trip.time = data['time']
        if 'transport' in data: trip.transport = data['transport']
        if 'notes' in data: trip.notes = data['notes'].strip()
        if 'budget' in data: trip.budget = float(data['budget'])

        db.session.commit()
        return jsonify(trip.to_dict()), 200

    except ValueError:
        return jsonify({
            "error": "Bad Request",
            "message": "Invalid date format. Use YYYY-MM-DD."
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update trip {trip_id}", "details": str(e)}), 500


@api_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
    """
    Delete a trip from the database.
    """
    try:
        trip = db.session.get(Trip, trip_id)
        if not trip:
            return jsonify({"error": f"Trip with ID {trip_id} not found"}), 404

        db.session.delete(trip)
        db.session.commit()
        
        return jsonify({
            "message": "Trip successfully deleted",
            "deleted_id": trip_id
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete trip {trip_id}", "details": str(e)}), 500


@api_bp.route('/cities', methods=['GET'])
def get_cities():
    """
    Autocomplete API for destinations.
    Expects a query parameter 'q'.
    """
    query = request.args.get('q', '').strip().lower()
    
    # Hardcoded dataset of major Indian and Tamil Nadu cities
    cities = [
        # Tamil Nadu
        "Chennai, Tamil Nadu", "Coimbatore, Tamil Nadu", "Madurai, Tamil Nadu", 
        "Tiruchirappalli, Tamil Nadu", "Salem, Tamil Nadu", "Tirunelveli, Tamil Nadu", 
        "Vellore, Tamil Nadu", "Erode, Tamil Nadu", "Thoothukudi, Tamil Nadu", 
        "Dindigul, Tamil Nadu", "Thanjavur, Tamil Nadu", "Kanyakumari, Tamil Nadu",
        "Ooty, Tamil Nadu", "Kodaikanal, Tamil Nadu",
        # Other Major Indian Cities
        "Mumbai, Maharashtra", "Delhi", "Bengaluru, Karnataka", "Hyderabad, Telangana",
        "Ahmedabad, Gujarat", "Kolkata, West Bengal", "Pune, Maharashtra", 
        "Jaipur, Rajasthan", "Lucknow, Uttar Pradesh", "Kanpur, Uttar Pradesh",
        "Nagpur, Maharashtra", "Indore, Madhya Pradesh", "Thane, Maharashtra",
        "Bhopal, Madhya Pradesh", "Visakhapatnam, Andhra Pradesh", "Patna, Bihar",
        "Vadodara, Gujarat", "Kochi, Kerala", "Thiruvananthapuram, Kerala",
        "Goa", "Agra, Uttar Pradesh", "Varanasi, Uttar Pradesh"
    ]
    
    if not query:
        return jsonify([])
        
    filtered_cities = [city for city in cities if query in city.lower()]
    
    return jsonify(filtered_cities[:10]), 200
