import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes import api_bp
from database import db
from config import Config

def create_app():
    """
    Application factory pattern to create and configure the Flask app.
    Connected to MySQL using SQLAlchemy.
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)

    # Initialize SQLAlchemy
    db.init_app(app)

    # Enable CORS for all routes under /api to allow frontend connection
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register blueprints (API routes)
    app.register_blueprint(api_bp)
    
    # Create required tables automatically
    with app.app_context():
        db.create_all()

    # Root route to verify backend status
    @app.route('/')
    def status():
        return jsonify({
            "status": "online",
            "message": "Smart Tourist Monitoring System Backend API is active.",
            "module": "Trip Planner",
            "database": "Connected to MySQL via SQLAlchemy"
        }), 200

    return app

if __name__ == '__main__':
    app = create_app()
    # Run on 127.0.0.1 explicitly to match frontend fetch calls
    app.run(host='127.0.0.1', port=5000, debug=True)
