import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

class Config:
    """
    Configuration class for the Flask Application.
    Provides standard settings and handles the Database URI connection string.
    """
    # Secret key for session security (optional for basic APIs, but good practice)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-12345")
    
    # Read individual database parameters from .env
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")
    
    # Check if MySQL variables are set. If not, default to SQLite for simple local running.
    if DB_USER and DB_NAME:
        # Construct MySQL connection string using PyMySQL driver
        # Format: mysql+pymysql://user:password@host:port/dbname
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        # Fallback to local SQLite file database for beginner ease of use
        SQLALCHEMY_DATABASE_URI = "sqlite:///trips.db"
        print("💡 DB_USER or DB_NAME not set in .env. Falling back to local SQLite database: sqlite:///trips.db")
        
    # Disable modification tracking feature of SQLAlchemy to save overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False
