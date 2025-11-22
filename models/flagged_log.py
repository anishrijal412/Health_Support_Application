from datetime import datetime
from extensions import db

class FlaggedLog(db.Model):
    __tablename__ = 'flagged_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    reason = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    source_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('flagged_logs', lazy=True))