import unittest
from unittest.mock import patch
from app import create_app
from extensions import db, bcrypt
from models.user import User
from models.forum import ForumPost, ForumReply


class ForumTestCase(unittest.TestCase):
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
            user = User(username="forumuser", email="forum@example.com", password=password_hash)
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
            data={"email": "forum@example.com", "password": "password123"},
            follow_redirects=True,
        )

    @patch("routes.forum.is_safe_content_ai", return_value=(True, "Clean"))
    def test_safe_post_persists(self, mock_moderation):
        response = self.client.post(
            "/forum/new",
            data={"title": "Hello", "content": "This is safe content."},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_moderation.called)

        with self.app.app_context():
            post = ForumPost.query.first()
            self.assertIsNotNone(post)
            self.assertEqual(post.title, "Hello")
            self.assertEqual(post.content, "This is safe content.")

    @patch("routes.forum.is_safe_content_ai", return_value=(False, "Contains harmful language"))
    def test_unsafe_post_blocked(self, mock_moderation):
        response = self.client.post(
            "/forum/new",
            data={"title": "Alert", "content": "I want to commit suicide"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_moderation.called)

        with self.app.app_context():
            self.assertEqual(ForumPost.query.count(), 0)

    @patch("routes.forum.is_safe_content_ai", return_value=(True, "Clean"))
    def test_reply_creation(self, mock_moderation):
        # Create initial post
        self.client.post(
            "/forum/new",
            data={"title": "Question", "content": "Need advice"},
            follow_redirects=True,
        )
        with self.app.app_context():
            post_id = ForumPost.query.first().id

        response = self.client.post(
            f"/forum/{post_id}/reply",
            data={"content": "Here is a helpful reply"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_moderation.called)

        with self.app.app_context():
            reply = ForumReply.query.first()
            self.assertIsNotNone(reply)
            self.assertEqual(reply.post_id, post_id)
            self.assertEqual(reply.content, "Here is a helpful reply")

    @patch("routes.forum.is_safe_content_ai", return_value=(False, "Contains harmful language"))
    def test_reply_blocked(self, mock_moderation):
        # Create safe post first
        with patch("routes.forum.is_safe_content_ai", return_value=(True, "Clean")):
            self.client.post(
                "/forum/new",
                data={"title": "Topic", "content": "A safe topic"},
                follow_redirects=True,
            )

        with self.app.app_context():
            post_id = ForumPost.query.first().id

        response = self.client.post(
            f"/forum/{post_id}/reply",
            data={"content": "This mentions suicide"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_moderation.called)

        with self.app.app_context():
            self.assertEqual(ForumReply.query.count(), 0)


if __name__ == "__main__":
    unittest.main()
