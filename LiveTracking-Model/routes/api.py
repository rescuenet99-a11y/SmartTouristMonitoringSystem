from flask import Blueprint
from flask import request
from flask import jsonify

from models.location import Location

api_bp=Blueprint("api",__name__)

@api_bp.route("/api/location",methods=["POST"])

def save_location():

    data=request.json

    tourist_id=1

    lat=data["latitude"]

    lng=data["longitude"]

    speed=data["speed"]

    Location.save_location(

        tourist_id,

        lat,

        lng,

        speed

    )

    return jsonify({

        "status":"success"

    })