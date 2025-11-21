import os
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from extensions import db, bcrypt, login_manager, mail
from flask_login import current_user
from datetime import datetime
from sqlalchemy import inspect, text
from sqlalchemy.exc import NoSuchTableError


def create_app():
    # Create app FIRST
    app = Flask(__name__)

    # Base directory
    basedir = os.path.abspath(os.path.dirname(__file__))

    # REAL production DB (never touched by tests)
    real_db_path = os.path.join(basedir, "instance", "mental_health.db")

    # Print for debugging
    print("📌 USING DATABASE FILE:", real_db_path)

    # Flask configurations
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{real_db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Upload folder
    app.config["MEDICAL_REPORT_UPLOAD_FOLDER"] = os.path.join(
        basedir, "instance", "medical_reports"
    )
    app.config["MEDICAL_REPORT_ALLOWED_EXTENSIONS"] = {"pdf"}

    # Email config
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "anishrijal577@gmail.com"
    app.config["MAIL_PASSWORD"] = "YOUR_APP_PASSWORD"  # Use app-password

    # Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # Import Blueprints
    from routes.auth import auth
    from routes.dashboard import dashboard
    from routes.reset_password import reset_bp
    from routes.profile import profile_bp
    from routes.appointments import appointments_bp
    from routes.medications import medications_bp
    from routes.forum import forum
    from routes.api_test import api_test
    from routes.unit_test import unit_test

    # Register Blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(reset_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(medications_bp)
    app.register_blueprint(forum)
    app.register_blueprint(api_test)
    app.register_blueprint(unit_test)

    # Import models before create_all()
    from models.user import User
    from models.profile import Profile
    from models.medical_history import MedicalHistory
    from models.medication import Medication
    from models.appointment import Appointment
    from models.forum import ForumPost, ForumReply

    # Notification injection
    @app.context_processor
    def inject_notifications():
        upcoming_items = []

        if current_user.is_authenticated:
            now = datetime.now()
            today = now.date()
            current_time = now.time()

            user_appointments = (
                Appointment.query.filter_by(user_id=current_user.id)
                .order_by(Appointment.date.asc(), Appointment.time.asc())
                .all()
            )

            for appt in user_appointments:
                if appt.date > today or (appt.date == today and appt.time >= current_time):
                    upcoming_items.append(appt)

        return {
            "notification_items": upcoming_items,
            "notification_count": len(upcoming_items),
        }

    # Ensure folders exist
    os.makedirs(app.config["MEDICAL_REPORT_UPLOAD_FOLDER"], exist_ok=True)

    # Create DB tables & column patches
    with app.app_context():
        inspector = inspect(db.engine)
        try:
            columns = {column["name"] for column in inspector.get_columns("medical_histories")}
        except NoSuchTableError:
            columns = set()

        if columns and "report_filename" not in columns:
            with db.engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE medical_histories ADD COLUMN report_filename VARCHAR(255)")
                )

        # Create all tables safely
        db.create_all()

    return app



if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
