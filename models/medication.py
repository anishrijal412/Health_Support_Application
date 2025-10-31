# models/medication.py
from extensions import db
from datetime import date

class Medication(db.Model):
    __tablename__ = 'medications'

    id = db.Column(db.Integer, primary_key=True)
    medical_history_id = db.Column(db.Integer, db.ForeignKey('medical_histories.id'), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50))
    frequency = db.Column(db.String(50))       # e.g., "Once daily", "2x per day"
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    reminder_time = db.Column(db.Time)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Medication {self.name}>"

    @property
    def is_active(self) -> bool:
        """Active if today is within [start_date, end_date] (inclusive).
        If end_date is None, active if today >= start_date.
        If start_date is None, treat as inactive (explicit start is recommended).
        """
        today = date.today()
        if self.start_date and self.end_date:
            return self.start_date <= today <= self.end_date
        if self.start_date and not self.end_date:
            return self.start_date <= today
        return False

    @property
    def status_label(self) -> str:
        return "Active" if self.is_active else "Inactive"
