from database import db
from datetime import datetime, date

class Trip(db.Model):
    """
    Trip Model representing the trips database table.
    Defines database columns matching the frontend form inputs.
    """
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination = db.Column(db.String(255), nullable=False)
    
    # Store dates. We can accept strings 'YYYY-MM-DD' and parse them to date objects
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    # Store travel departure time (e.g. '14:30' or '2:30 PM')
    time = db.Column(db.String(50), nullable=False)
    
    # Mode of transportation (e.g. Bus, Train, Flight, Car)
    transport = db.Column(db.String(100), nullable=False)
    
    # Optional field for special notes/itinerary
    notes = db.Column(db.Text, nullable=True)

    # Estimated budget for the trip
    budget = db.Column(db.Float, nullable=True, default=0.0)

    def to_dict(self):
        """
        Helper method to serialize the model object to a Python dictionary,
        making it easy to return as JSON in API responses.
        """
        return {
            'id': self.id,
            'destination': self.destination,
            'startDate': self.start_date.isoformat() if isinstance(self.start_date, (date, datetime)) else self.start_date,
            'endDate': self.end_date.isoformat() if isinstance(self.end_date, (date, datetime)) else self.end_date,
            'time': self.time,
            'transport': self.transport,
            'notes': self.notes if self.notes else "",
            'budget': self.budget if self.budget else 0.0
        }
