# models/appointment.py
from extensions import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)

    # backref lets you do current_user.appointments
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))

    def __repr__(self):
        return f"<Appointment {self.title}>"
