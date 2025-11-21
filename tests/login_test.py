import unittest
from app import create_app
from extensions import db, bcrypt
from models.user import User


class LoginTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
            WTF_CSRF_ENABLED=False,
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            password_hash = bcrypt.generate_password_hash("password123").decode("utf-8")
            user = User(username="tester", email="tester@example.com", password=password_hash)
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self, email, password):
        return self.client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def test_login_page_loads(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"login", response.data.lower())

    def test_successful_login(self):
        response = self.login("tester@example.com", "password123")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"logged in successfully", response.data.lower())

    def test_wrong_password_fails(self):
        response = self.login("tester@example.com", "wrongpass")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid credentials", response.data.lower())

    def test_missing_username_fails(self):
        response = self.login("", "password123")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid credentials", response.data.lower())

    def test_missing_password_fails(self):
        response = self.login("tester@example.com", "")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"invalid credentials", response.data.lower())

    def test_logout(self):
        self.login("tester@example.com", "password123")
        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"you have been logged out", response.data.lower())


if __name__ == "__main__":
    unittest.main()