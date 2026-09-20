# tests/test_auth.py
import unittest
from controllers.auth import (
    sign_up,
    log_in,
    logout,
    getCurrentuser
)
from controllers.exceptions import authError, validationError
from models.fake_models import reset_db

class TestAuthSystem(unittest.TestCase):

    def setUp(self):
        """Runs before every single test to guarantee state isolation."""
        reset_db()
        logout()

    def test_sign_up_success(self):
        user = sign_up("student@example.com", "securePassword123")
        self.assertEqual(user["email"], "student@example.com")
        self.assertTrue(user["password_hash"].startswith("$2b$"))
        self.assertEqual(getCurrentuser(), user)

    def test_duplicate_sign_up_fails(self):
        sign_up("duplicate@example.com", "securePassword123")
        with self.assertRaises(authError):
            sign_up("duplicate@example.com", "differentPassword123")

    def test_invalid_email_fails(self):
        with self.assertRaises(validationError):
            sign_up("notanemail", "securePassword123")

    def test_short_password_fails(self):
        with self.assertRaises(validationError):
            sign_up("valid@example.com", "short")

    def test_log_in_success(self):
        sign_up("user@example.com", "validPass123")
        logout()
        self.assertIsNone(getCurrentuser())

        user = log_in("user@example.com", "validPass123")
        self.assertEqual(user["email"], "user@example.com")
        self.assertEqual(getCurrentuser(), user)

    def test_log_in_wrong_password_fails(self):
        sign_up("user@example.com", "correctPass123")
        with self.assertRaises(authError):
            log_in("user@example.com", "wrongPass999")

    def test_log_in_nonexistent_user_fails(self):
        with self.assertRaises(authError):
            log_in("ghost@example.com", "anyPass123")

    def test_logout(self):
        sign_up("user@example.com", "securePassword123")
        self.assertIsNotNone(getCurrentuser())
        logout()
        self.assertIsNone(getCurrentuser())

if __name__ == "__main__":
    unittest.main()