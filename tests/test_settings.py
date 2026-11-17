import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import controllers.settings as settings

from exceptions import AuthError, ValidationError
from models import db, intakes, users
from controllers.auth import hashPassword, verifyPassword


SAMPLE_INTAKE = {
    "year": "sophomore",
    "major_status": "declared",
    "has_pipeline": "yes",
    "coursework": ["intro", "oop", "dsa"],
    "skills": [
        {
            "language": "python",
            "level": "multi_file",
        }
    ],
    "project_count": "2_3",
    "biggest_project_type": "team",
    "deployed": "no",
    "carrying": ["research", "hackathons"],
    "weekly_hours": "5_10",
    "credit_load": "19_plus",
    "goal": "internship",
    "free_text": "Interested in backend and systems work.",
}


class TestSettingsController(unittest.TestCase):

    def setUp(self):

        # create temporary folder for test database + config.ini
        self.temp_dir = tempfile.TemporaryDirectory()

        self.db_path = os.path.join(
            self.temp_dir.name,
            "test_devoyage.db",
        )

        self.config_path = Path(
            self.temp_dir.name
        ) / "config.ini"

        # save the real function before patching it
        self.real_get_connection = db.get_connection

        # create temporary database
        conn = self.real_get_connection(
            self.db_path
        )

        db.init_db(conn)

        # create a real test user with a real bcrypt hash
        self.original_password = "password123"

        password_hash = hashPassword(
            self.original_password
        )

        self.user_id = users.create_user(
            conn,
            "student@example.com",
            password_hash,
        )

        # give the user an intake
        self.intake_id = intakes.save_intake(
            conn,
            self.user_id,
            SAMPLE_INTAKE,
        )

        conn.close()

        # force settings controller to use test database
        self.connection_patcher = patch(
            "controllers.settings.db.get_connection",
            side_effect=self.get_test_connection,
        )

        self.connection_patcher.start()

        # force config.py to use temporary config.ini
        self.config_patcher = patch(
            "controllers.settings.config.CONFIG_PATH",
            self.config_path,
        )

        self.config_patcher.start()

    def tearDown(self):

        self.config_patcher.stop()
        self.connection_patcher.stop()

        self.temp_dir.cleanup()

    def get_test_connection(self):

        return self.real_get_connection(
            self.db_path
        )

    # ---------------------------------------------------------
    # get_settings
    # ---------------------------------------------------------

    def test_get_settings_returns_theme_and_weekly_hours(self):

        result = settings.get_settings(
            self.user_id
        )

        self.assertEqual(
            result["theme"],
            "light",
        )

        self.assertEqual(
            result["weekly_hours"],
            "5_10",
        )

    # ---------------------------------------------------------
    # update_theme
    # ---------------------------------------------------------

    def test_update_theme_changes_theme(self):

        settings.update_theme(
            self.user_id,
            "dark",
        )

        result = settings.get_settings(
            self.user_id
        )

        self.assertEqual(
            result["theme"],
            "dark",
        )

    def test_update_theme_rejects_invalid_theme(self):

        with self.assertRaises(
            ValidationError
        ):

            settings.update_theme(
                self.user_id,
                "purple",
            )

    # ---------------------------------------------------------
    # update_weekly_hours
    # ---------------------------------------------------------

    def test_update_weekly_hours_changes_latest_intake(self):

        settings.update_weekly_hours(
            self.user_id,
            "10_15",
        )

        conn = self.real_get_connection(
            self.db_path
        )

        latest_intake = intakes.get_latest_intake(
            conn,
            self.user_id,
        )

        conn.close()

        self.assertEqual(
            latest_intake["weekly_hours"],
            "10_15",
        )

    def test_update_weekly_hours_rejects_invalid_value(self):

        with self.assertRaises(
            ValidationError
        ):

            settings.update_weekly_hours(
                self.user_id,
                "100_hours",
            )

    def test_update_weekly_hours_without_intake_raises_error(self):

        conn = self.real_get_connection(
            self.db_path
        )

        password_hash = hashPassword(
            "anotherpassword"
        )

        user_without_intake = users.create_user(
            conn,
            "no-intake@example.com",
            password_hash,
        )

        conn.close()

        with self.assertRaises(
            ValidationError
        ):

            settings.update_weekly_hours(
                user_without_intake,
                "5_10",
            )

    # ---------------------------------------------------------
    # change_email
    # ---------------------------------------------------------

    def test_change_email_updates_and_normalizes_email(self):

        settings.change_email(
            self.user_id,
            "  NEWEMAIL@EXAMPLE.COM  ",
        )

        conn = self.real_get_connection(
            self.db_path
        )

        user = users.get_user_by_id(
            conn,
            self.user_id,
        )

        conn.close()

        self.assertEqual(
            user["email"],
            "newemail@example.com",
        )

    def test_change_email_rejects_invalid_email(self):

        with self.assertRaises(
            ValidationError
        ):

            settings.change_email(
                self.user_id,
                "not-an-email",
            )

    def test_change_email_rejects_duplicate_email(self):

        conn = self.real_get_connection(
            self.db_path
        )

        second_password_hash = hashPassword(
            "secondpassword"
        )

        users.create_user(
            conn,
            "second@example.com",
            second_password_hash,
        )

        conn.close()

        with self.assertRaises(
            AuthError
        ):

            settings.change_email(
                self.user_id,
                "second@example.com",
            )

    # ---------------------------------------------------------
    # change_password
    # ---------------------------------------------------------

    def test_change_password_updates_password_hash(self):

        new_password = "newpassword123"

        settings.change_password(
            self.user_id,
            self.original_password,
            new_password,
        )

        conn = self.real_get_connection(
            self.db_path
        )

        user = users.get_user_by_id(
            conn,
            self.user_id,
        )

        conn.close()

        password_is_correct = verifyPassword(
            new_password,
            user["password_hash"],
        )

        self.assertTrue(
            password_is_correct
        )

    def test_change_password_rejects_wrong_current_password(self):

        with self.assertRaises(
            AuthError
        ):

            settings.change_password(
                self.user_id,
                "wrongpassword",
                "newpassword123",
            )

    def test_change_password_rejects_short_new_password(self):

        with self.assertRaises(
            ValidationError
        ):

            settings.change_password(
                self.user_id,
                self.original_password,
                "short",
            )

    # ---------------------------------------------------------
    # regenerate_roadmap
    # ---------------------------------------------------------

    def test_regenerate_roadmap_calls_generate_roadmap(self):

        fake_roadmap = {
            "id": 10,
            "user_id": self.user_id,
            "steps": [],
            "not_now_items": [],
        }

        with patch(
            "controllers.settings.generate_roadmap",
            return_value=fake_roadmap,
        ) as mock_generate:

            result = settings.regenerate_roadmap(
                self.user_id
            )

        mock_generate.assert_called_once_with(
            self.user_id
        )

        self.assertEqual(
            result,
            fake_roadmap,
        )

    # ---------------------------------------------------------
    # clear_roadmap_data
    # ---------------------------------------------------------

    def test_clear_roadmap_data_calls_model_function(self):

        clear_was_called = {
            "called": False,
            "user_id": None,
        }

        # temporary fake until Sadia's actual function exists
        def fake_clear_roadmap_data(
            conn,
            user_id,
        ):

            clear_was_called["called"] = True
            clear_was_called["user_id"] = user_id

        with patch(
            "controllers.settings.roadmaps.clear_roadmap_data",
            side_effect=fake_clear_roadmap_data,
            create=True,
        ):

            settings.clear_roadmap_data(
                self.user_id
            )

        self.assertTrue(
            clear_was_called["called"]
        )

        self.assertEqual(
            clear_was_called["user_id"],
            self.user_id,
        )


if __name__ == "__main__":
    unittest.main()