# models/profile.py
from extensions import db

class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)

    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    ssn = db.Column(db.String(20))
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))

    medical_histories = db.relationship('MedicalHistory', backref='profile', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Profile {self.full_name}>"
