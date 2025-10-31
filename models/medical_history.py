from extensions import db
from datetime import datetime, date

class MedicalHistory(db.Model):
    __tablename__ = 'medical_histories'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    disease = db.Column(db.String(100), nullable=False)
    doctor = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ✅ Relationship to medications
    medications = db.relationship('Medication', backref='medical_history', cascade='all, delete-orphan')

    @property
    def has_active_medications(self):
        """Return True if at least one medication is active (today is between start and end dates)."""
        today = date.today()
        for med in self.medications:
            if med.start_date and med.end_date and med.start_date <= today <= med.end_date:
                return True
        return False

    def __repr__(self):
        return f"<MedicalHistory {self.disease}>"
