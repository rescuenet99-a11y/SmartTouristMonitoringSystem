from flask import Flask
from flask_socketio import SocketIO

from database import mysql

from routes.tracking import tracking_bp
from routes.api import api_bp

from socket_events import register_socket_events

app = Flask(__name__)

app.config.from_pyfile("config.py")

mysql.init_app(app)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

# Register Blueprints
app.register_blueprint(tracking_bp)
app.register_blueprint(api_bp)

# Register Socket Events
register_socket_events(socketio)

if __name__ == "__main__":
    socketio.run(
        app,
        debug=True
    )