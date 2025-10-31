import os
from flask import Flask
from extensions import db, bcrypt, login_manager, mail   # ✅ include mail

def create_app():
    app = Flask(__name__)

    # ✅ Basic app config
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance', 'mental_health.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ✅ Gmail SMTP config (for password reset)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'anishrijal577@gmail.com'   # your Gmail
    app.config['MAIL_PASSWORD'] = 'YOUR_APP_PASSWORD'        # ⚠️ use App Password

    # ✅ Init extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
   
    # ✅ Import blueprints
    from routes.auth import auth
    from routes.dashboard import dashboard
    from routes.reset_password import reset_bp
    from routes.profile import profile_bp
    from routes.appointments import appointments_bp  
    from routes.medications import medications_bp

    # ✅ Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(reset_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(appointments_bp)  
    app.register_blueprint(medications_bp)


    # ✅ Import models (this MUST happen before db.create_all)
    from models.profile import Profile
    from models.medical_history import MedicalHistory
    from models.medication import Medication   # 👈 NEW
    from models.appointment import Appointment

    # ✅ Create DB tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
