import os
import tempfile
import unittest
from unittest.mock import patch

import controllers.roadmap as roadmap_controller
from exceptions import AIServiceError, ValidationError
from models import db, intakes, roadmaps, users


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


SAMPLE_AI_RESULT = {
    "steps": [
        {
            "title": "Strengthen data structures",
            "description": "Practice core DSA patterns.",
            "reasoning": "The student is targeting internships.",
            "est_time": "2 weeks",
        },
        {
            "title": "Build a backend project",
            "description": "Create a multi-file backend project.",
            "reasoning": "The student already has multi-file Python experience.",
            "est_time": "3 weeks",
        },
        {
            "title": "Improve project documentation",
            "description": "Write clear READMEs and architecture notes.",
            "reasoning": "The student already has multiple projects.",
            "est_time": "1 week",
        },
        {
            "title": "Prepare for technical interviews",
            "description": "Practice timed coding problems.",
            "reasoning": "The student's goal is an internship.",
            "est_time": "3 weeks",
        },
        {
            "title": "Apply selectively",
            "description": "Apply to roles that match current skills.",
            "reasoning": "The student has limited weekly hours and a 19+ credit load.",
            "est_time": "ongoing",
        },
    ],
    "not_now": [
        {
            "title": "Learn another frontend framework",
            "reasoning": "It does not directly support the current internship goal.",
        },
        {
            "title": "Add many new certifications",
            "reasoning": "Project and interview work is a higher priority right now.",
        },
    ],
}


class TestRoadmapController(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(
            self.temp_dir.name,
            "test_devoyage.db",
        )

        self.real_get_connection = db.get_connection

        conn = self.real_get_connection(self.db_path)
        db.init_db(conn)

        self.user_id = users.create_user(
            conn,
            "student@example.com",
            "fake_hash_for_test",
        )

        self.intake_id = intakes.save_intake(
            conn,
            self.user_id,
            SAMPLE_INTAKE,
        )

        conn.close()

        self.connection_patcher = patch(
            "controllers.roadmap.db.get_connection",
            side_effect=self.get_test_connection,
        )
        self.connection_patcher.start()

    def tearDown(self):
        self.connection_patcher.stop()
        self.temp_dir.cleanup()

    def get_test_connection(self):
        return self.real_get_connection(self.db_path)

    def test_generate_roadmap_saves_and_returns_full_roadmap(self):
        received_intake = {}

        def fake_generate_roadmap_from_intake(intake_data):
            received_intake.update(intake_data)
            return SAMPLE_AI_RESULT

        with patch(
            "controllers.roadmap.generate_roadmap_from_intake",
            side_effect=fake_generate_roadmap_from_intake,
        ):
            result = roadmap_controller.generate_roadmap(self.user_id)

        self.assertEqual(received_intake, SAMPLE_INTAKE)
        self.assertNotIn("id", received_intake)
        self.assertNotIn("user_id", received_intake)
        self.assertNotIn("created_at", received_intake)

        self.assertEqual(result["user_id"], self.user_id)
        self.assertEqual(result["intake_id"], self.intake_id)
        self.assertEqual(len(result["steps"]), 5)
        self.assertEqual(len(result["not_now_items"]), 2)

        self.assertEqual(result["steps"][0]["position"], 1)
        self.assertEqual(result["steps"][1]["position"], 2)

        for step in result["steps"]:
            self.assertEqual(step["status"], "pending")

        conn = self.real_get_connection(self.db_path)

        stored = roadmaps.get_current_roadmap(
            conn,
            self.user_id,
        )

        conn.close()

        self.assertEqual(stored["id"], result["id"])
        self.assertEqual(stored["user_id"], self.user_id)

    def test_generate_roadmap_uses_latest_intake(self):
        newer_intake = SAMPLE_INTAKE.copy()
        newer_intake["weekly_hours"] = "under_5"
        newer_intake["goal"] = "fundamentals"

        conn = self.real_get_connection(self.db_path)

        newer_intake_id = intakes.save_intake(
            conn,
            self.user_id,
            newer_intake,
        )

        conn.close()

        received_intake = {}

        def fake_generate_roadmap_from_intake(intake_data):
            received_intake.update(intake_data)
            return SAMPLE_AI_RESULT

        with patch(
            "controllers.roadmap.generate_roadmap_from_intake",
            side_effect=fake_generate_roadmap_from_intake,
        ):
            result = roadmap_controller.generate_roadmap(self.user_id)

        self.assertEqual(received_intake["weekly_hours"], "under_5")
        self.assertEqual(received_intake["goal"], "fundamentals")
        self.assertEqual(result["intake_id"], newer_intake_id)

    def test_generate_roadmap_without_intake_raises_validation_error(self):
        conn = self.real_get_connection(self.db_path)

        user_without_intake = users.create_user(
            conn,
            "no-intake@example.com",
            "fake_hash_for_test",
        )

        conn.close()

        with patch(
            "controllers.roadmap.generate_roadmap_from_intake"
        ) as mock_ai:
            with self.assertRaises(ValidationError):
                roadmap_controller.generate_roadmap(
                    user_without_intake
                )

        mock_ai.assert_not_called()

        conn = self.real_get_connection(self.db_path)

        stored = roadmaps.get_current_roadmap(
            conn,
            user_without_intake,
        )

        conn.close()

        self.assertIsNone(stored)

    def test_ai_service_error_does_not_save_roadmap(self):
        with patch(
            "controllers.roadmap.generate_roadmap_from_intake",
            side_effect=AIServiceError("AI service failed"),
        ):
            with self.assertRaises(AIServiceError):
                roadmap_controller.generate_roadmap(
                    self.user_id
                )

        conn = self.real_get_connection(self.db_path)

        stored = roadmaps.get_current_roadmap(
            conn,
            self.user_id,
        )

        conn.close()

        self.assertIsNone(stored)

    def test_get_current_roadmap_returns_saved_roadmap(self):
        conn = self.real_get_connection(self.db_path)

        roadmaps.create_roadmap(
            conn,
            self.user_id,
            self.intake_id,
            SAMPLE_AI_RESULT["steps"],
            SAMPLE_AI_RESULT["not_now"],
        )

        conn.close()

        result = roadmap_controller.get_current_roadmap(
            self.user_id
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["user_id"], self.user_id)
        self.assertEqual(result["intake_id"], self.intake_id)
        self.assertEqual(len(result["steps"]), 5)
        self.assertEqual(len(result["not_now_items"]), 2)
        self.assertEqual(result["steps"][0]["position"], 1)


if __name__ == "__main__":
    unittest.main()
