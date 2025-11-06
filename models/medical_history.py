from extensions import db
from datetime import datetime, date

class MedicalHistory(db.Model):
    __tablename__ = 'medical_histories'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    disease = db.Column(db.String(100), nullable=False)
    doctor = db.Column(db.String(100))
    description = db.Column(db.Text)
    report_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    

    # ✅ Relationship to medications
    medications = db.relationship('Medication', backref='medical_history', cascade='all, delete-orphan')

    @property
    def has_active_medications(self):
        """Return True if at least one related medication is currently active."""
        return any(med.is_active for med in self.medications)

    def __repr__(self):
        return f"<MedicalHistory {self.disease}>"

@property
def has_report(self):
        return bool(self.report_filename)