import unittest
from app import create_app
from extensions import db, bcrypt
from models.user import User
from models.profile import Profile


class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            password_hash = bcrypt.generate_password_hash("password123").decode("utf-8")
            user = User(username="profileuser", email="profile@example.com", password=password_hash)
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
            data={"email": "profile@example.com", "password": "password123"},
            follow_redirects=True,
        )

    def test_profile_creation(self):
        response = self.client.post(
            "/profile",
            data={
                "full_name": "John Doe",
                "age": "30",
                "gender": "Male",
                "ssn": "123-45-6789",
                "email": "john@example.com",
                "phone_number": "1234567890",
                "address": "123 Street",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            profile = Profile.query.first()
            self.assertIsNotNone(profile)
            self.assertEqual(profile.full_name, "John Doe")
            self.assertEqual(profile.age, 30)

    def test_profile_update(self):
        self.client.post(
            "/profile",
            data={
                "full_name": "John Doe",
                "age": "30",
                "gender": "Male",
                "ssn": "123-45-6789",
                "email": "john@example.com",
                "phone_number": "1234567890",
                "address": "123 Street",
            },
            follow_redirects=True,
        )

        response = self.client.post(
            "/profile",
            data={
                "full_name": "John Doe Updated",
                "age": "31",
                "gender": "Male",
                "ssn": "123-45-6789",
                "email": "john@example.com",
                "phone_number": "9876543210",
                "address": "456 Avenue",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            profile = Profile.query.first()
            self.assertEqual(profile.full_name, "John Doe Updated")
            self.assertEqual(profile.age, 31)
            self.assertEqual(profile.address, "456 Avenue")

    def test_missing_required_fields(self):
        response = self.client.post(
            "/profile",
            data={
                "full_name": "",
                "age": "",
                "gender": "",
                "ssn": "",
                "email": "",
                "phone_number": "",
                "address": "",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            profile = Profile.query.first()
            self.assertIsNotNone(profile)
            self.assertEqual(profile.full_name, "")
            self.assertIsNone(profile.age)


if __name__ == "__main__":
    unittest.main()
