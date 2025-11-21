import unittest
from datetime import datetime, timedelta
from app import create_app
from extensions import db, bcrypt
from models.user import User
from models.appointment import Appointment


class AppointmentTestCase(unittest.TestCase):
    def setUp(self):
        # Test-safe create_app
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            password_hash = bcrypt.generate_password_hash("password123").decode("utf-8")
            user = User(username="apptuser", email="appt@example.com", password=password_hash)
            db.session.add(user)
            db.session.commit()

        self.login()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        return self.client.post(
            "/login",
            data={"email": "appt@example.com", "password": "password123"},
            follow_redirects=True,
        )

    def test_create_appointment(self):
        future_date = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        response = self.client.post(
            "/appointments/new",
            data={
                "title": "Therapy Session",
                "date": future_date,
                "time": "10:30",
                "description": "Discuss progress",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            appt = Appointment.query.first()
            self.assertIsNotNone(appt)
            self.assertEqual(appt.title, "Therapy Session")

    def test_upcoming_appointments_visible(self):
        future_date = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")
        self.client.post(
            "/appointments/new",
            data={
                "title": "Checkup",
                "date": future_date,
                "time": "09:00",
                "description": "General checkup",
            },
            follow_redirects=True,
        )
        response = self.client.get("/appointments")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Checkup", response.data)

    def test_missing_required_fields(self):
        response = self.client.post(
            "/appointments/new",
            data={"title": "", "date": "", "time": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(Appointment.query.count(), 0)

    def test_invalid_date_time(self):
        response = self.client.post(
            "/appointments/new",
            data={
                "title": "Invalid Date",
                "date": "2023-13-40",
                "time": "25:61",
                "description": "Bad time",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(Appointment.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
