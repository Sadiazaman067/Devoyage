import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import controllers.auth as auth
from controllers.auth import (
    sign_up,
    log_in,
    log_out,
    getCurrentuser,
)
from controllers.exceptions import AuthError, ValidationError
from models import db, users


class TestAuthSystem(unittest.TestCase):

    def setUp(self):
        """
        Create a fresh temporary SQLite database before every test.

        auth.py normally calls db.get_connection() with the real Devoyage
        database path. During tests, we redirect those calls to this
        temporary database instead.
        """
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_auth.db"

        # Save the real function before patching it.
        self.real_get_connection = db.get_connection

        # Create the users table in the temporary database.
        conn = self.real_get_connection(self.db_path)
        users.create_table(conn)
        conn.commit()
        conn.close()

        # Whenever auth.py asks for a DB connection, give it one to
        # the temporary test database.
        self.connection_patch = patch(
            "controllers.auth.db.get_connection",
            side_effect=lambda: self.real_get_connection(self.db_path),
        )
        self.connection_patch.start()

        # Make sure session state does not leak between tests.
        log_out()

    def tearDown(self):
        """Clean up the patch, session, and temporary database."""
        log_out()
        self.connection_patch.stop()
        self.temp_dir.cleanup()

    def test_sign_up_success(self):
        user_id = sign_up(
            "student@example.com",
            "securePassword123",
        )

        self.assertIsInstance(user_id, int)
        self.assertEqual(getCurrentuser(), user_id)

        conn = self.real_get_connection(self.db_path)
        try:
            user = users.get_user_by_id(conn, user_id)
        finally:
            conn.close()

        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "student@example.com")

    def test_password_is_hashed_in_database(self):
        password = "securePassword123"

        user_id = sign_up(
            "student@example.com",
            password,
        )

        conn = self.real_get_connection(self.db_path)
        try:
            user = users.get_user_by_id(conn, user_id)
        finally:
            conn.close()

        self.assertNotEqual(user["password_hash"], password)
        self.assertTrue(
            auth.verifyPassword(password, user["password_hash"])
        )

    def test_email_is_normalized(self):
        user_id = sign_up(
            "  Student@Example.COM  ",
            "securePassword123",
        )

        conn = self.real_get_connection(self.db_path)
        try:
            user = users.get_user_by_id(conn, user_id)
        finally:
            conn.close()

        self.assertEqual(user["email"], "student@example.com")

    def test_duplicate_sign_up_fails(self):
        sign_up(
            "duplicate@example.com",
            "securePassword123",
        )

        with self.assertRaises(AuthError):
            sign_up(
                "duplicate@example.com",
                "differentPassword123",
            )

    def test_duplicate_email_is_case_insensitive(self):
        sign_up(
            "Student@Example.com",
            "securePassword123",
        )

        with self.assertRaises(AuthError):
            sign_up(
                "student@example.com",
                "differentPassword123",
            )

    def test_invalid_email_fails(self):
        with self.assertRaises(ValidationError):
            sign_up(
                "notanemail",
                "securePassword123",
            )

    def test_short_password_fails(self):
        with self.assertRaises(ValidationError):
            sign_up(
                "valid@example.com",
                "short",
            )

    def test_log_in_success(self):
        original_user_id = sign_up(
            "user@example.com",
            "validPass123",
        )

        log_out()
        self.assertIsNone(getCurrentuser())

        logged_in_user_id = log_in(
            "user@example.com",
            "validPass123",
        )

        self.assertEqual(logged_in_user_id, original_user_id)
        self.assertEqual(getCurrentuser(), original_user_id)

    def test_log_in_normalizes_email(self):
        original_user_id = sign_up(
            "user@example.com",
            "validPass123",
        )

        log_out()

        logged_in_user_id = log_in(
            "  USER@EXAMPLE.COM  ",
            "validPass123",
        )

        self.assertEqual(logged_in_user_id, original_user_id)

    def test_log_in_wrong_password_fails(self):
        sign_up(
            "user@example.com",
            "correctPass123",
        )

        with self.assertRaises(AuthError):
            log_in(
                "user@example.com",
                "wrongPass999",
            )

    def test_log_in_nonexistent_user_fails(self):
        with self.assertRaises(AuthError):
            log_in(
                "ghost@example.com",
                "anyPass123",
            )

    def test_empty_login_fails(self):
        with self.assertRaises(ValidationError):
            log_in("", "")

    def test_log_out_clears_session(self):
        sign_up(
            "user@example.com",
            "securePassword123",
        )

        self.assertIsNotNone(getCurrentuser())

        log_out()

        self.assertIsNone(getCurrentuser())


if __name__ == "__main__":
    unittest.main()