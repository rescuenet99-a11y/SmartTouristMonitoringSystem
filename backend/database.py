from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy object here.
# This avoids circular imports by decoupling app creation from database usage.
db = SQLAlchemy()
