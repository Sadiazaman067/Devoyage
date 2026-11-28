import os
import tempfile
import unittest
from unittest.mock import patch
import controllers.portfolio as portfolioController
from exceptions import ValidationError
from models import db, intakes, roadmaps, users


sampleIntake = {
    "year": "sophomore",
    "major_status": "declared",
    "has_pipeline": "yes",
    "coursework": ["intro", "oop"],
    "skills": [{"language": "python", "level": "multi_file"}],
    "project_count": "1",
    "biggest_project_type": "solo",
    "deployed": "no",
    "carrying": ["none"],
    "weekly_hours": "5_10",
    "credit_load": "16_18",
    "goal": "internship",
    "free_text": None,
}

sampleSteps = [
    {
        "title": "Build a CLI tool",
        "description": "Write a small Python CLI.",
        "reasoning": "Matches Python experience.",
        "est_time": "2 weeks",
    },
    {
        "title": "Deploy a web app",
        "description": "Ship a small project.",
        "reasoning": "Addresses no deployed projects.",
        "est_time": "3 weeks",
    },
]

sampleNotNow = [
    {
        "title": "Kubernetes",
        "reasoning": "Too early for current goals.",
    }
]


def makeEntryData(**overrides):
    data = {
        "entry_type": "project",
        "title": "Devoyage",
        "start_date": "2026-11-01",
        "link": "https://github.com/example/devoyage",
        "note": "Built the backend controllers.",
        "step_id": None,
    }
    data.update(overrides)
    return data


class TestPortfolioController(unittest.TestCase):

    def setUp(self):
        self.tempDir = tempfile.TemporaryDirectory()
        self.dbPath = os.path.join(self.tempDir.name, "test_devoyage.db")

        self.realGetConnection = db.get_connection

        conn = self.realGetConnection(self.dbPath)
        db.init_db(conn)

        self.user1Id = users.create_user(conn, "user1@example.com", "fake_hash_1")
        self.user2Id = users.create_user(conn, "user2@example.com", "fake_hash_2")

        self.intakeId = intakes.save_intake(conn, self.user1Id, sampleIntake)
        roadmaps.create_roadmap(conn, self.user1Id, self.intakeId, sampleSteps, sampleNotNow)
        roadmap = roadmaps.get_current_roadmap(conn, self.user1Id)
        self.user1StepId = roadmap["steps"][0]["id"]

        conn.close()

        self.connectionPatcher = patch(
            "controllers.portfolio.db.get_connection",
            side_effect=self.getTestConnection,
        )
        self.connectionPatcher.start()

    def tearDown(self):
        self.connectionPatcher.stop()
        self.tempDir.cleanup()

    def getTestConnection(self):
        return self.realGetConnection(self.dbPath)

    def test_add_portfolio_entry_success(self):
        entryId = portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(step_id=self.user1StepId),
        )

        self.assertIsInstance(entryId, int)

        entries = portfolioController.list_portfolio_entries(self.user1Id)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["id"], entryId)
        self.assertEqual(entries[0]["title"], "Devoyage")
        self.assertEqual(entries[0]["step_id"], self.user1StepId)

    def test_add_portfolio_entry_minimal_fields(self):
        entryId = portfolioController.add_portfolio_entry(
            self.user1Id,
            {
                "entry_type": "course",
                "title": "  CSC 317  ",
                "start_date": "2026-08-20",
            },
        )

        self.assertIsInstance(entryId, int)
        entries = portfolioController.list_portfolio_entries(self.user1Id)
        self.assertEqual(entries[0]["title"], "CSC 317")
        self.assertIsNone(entries[0]["link"])
        self.assertIsNone(entries[0]["note"])
        self.assertIsNone(entries[0]["step_id"])

    def test_add_portfolio_entry_rejects_invalid_type(self):
        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(entry_type="blog"),
            )

    def test_add_portfolio_entry_rejects_empty_or_long_title(self):
        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(title="   "),
            )

        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(title="a" * 121),
            )

    def test_add_portfolio_entry_rejects_invalid_date(self):
        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(start_date="11/01/2026"),
            )

        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(start_date="2026-02-30"),
            )

    def test_add_portfolio_entry_rejects_invalid_link(self):
        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(link="github.com/example/repo"),
            )

    def test_add_portfolio_entry_rejects_long_note(self):
        with self.assertRaises(ValidationError) as ctx:
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(note="x" * 501),
            )

        self.assertEqual(str(ctx.exception), "Note must be 500 characters or fewer.")

    def test_add_portfolio_entry_rejects_bool_step_id(self):
        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(step_id=True),
            )

    def test_add_portfolio_entry_rejects_step_not_in_current_roadmap(self):
        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user1Id,
                makeEntryData(step_id=99999),
            )

        with self.assertRaises(ValidationError):
            portfolioController.add_portfolio_entry(
                self.user2Id,
                makeEntryData(step_id=self.user1StepId),
            )

    def test_list_portfolio_entries_orders_by_newest_date_then_id(self):
        portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(title="Older", start_date="2026-01-10"),
        )
        portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(title="Same Day 1", start_date="2026-10-01"),
        )
        portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(title="Same Day 2", start_date="2026-10-01"),
        )

        entries = portfolioController.list_portfolio_entries(self.user1Id)
        titles = [e["title"] for e in entries]

        self.assertEqual(titles, ["Same Day 2", "Same Day 1", "Older"])

    def test_list_portfolio_entries_filters_by_type_and_isolates_users(self):
        portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(entry_type="project", title="User1 Project"),
        )
        portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(entry_type="hackathon", title="User1 Hack"),
        )
        portfolioController.add_portfolio_entry(
            self.user2Id,
            makeEntryData(entry_type="project", title="User2 Project"),
        )

        user1Projects = portfolioController.list_portfolio_entries(self.user1Id, entry_type="project")
        self.assertEqual(len(user1Projects), 1)
        self.assertEqual(user1Projects[0]["title"], "User1 Project")

        user2All = portfolioController.list_portfolio_entries(self.user2Id)
        self.assertEqual(len(user2All), 1)
        self.assertEqual(user2All[0]["title"], "User2 Project")

    def test_list_portfolio_entries_rejects_unknown_type(self):
        with self.assertRaises(ValidationError):
            portfolioController.list_portfolio_entries(self.user1Id, entry_type="unknown")

    def test_update_portfolio_entry_updates_fields(self):
        entryId = portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(title="Original"),
        )

        portfolioController.update_portfolio_entry(
            self.user1Id,
            entryId,
            makeEntryData(
                entry_type="hackathon",
                title="Updated Title",
                start_date="2026-11-15",
                link=None,
                note="Won 1st place.",
                step_id=self.user1StepId,
            ),
        )

        entries = portfolioController.list_portfolio_entries(self.user1Id)
        self.assertEqual(entries[0]["entry_type"], "hackathon")
        self.assertEqual(entries[0]["title"], "Updated Title")
        self.assertEqual(entries[0]["start_date"], "2026-11-15")
        self.assertIsNone(entries[0]["link"])
        self.assertEqual(entries[0]["note"], "Won 1st place.")
        self.assertEqual(entries[0]["step_id"], self.user1StepId)

    def test_update_portfolio_entry_keeps_old_step_after_roadmap_regenerate(self):
        entryId = portfolioController.add_portfolio_entry(
            self.user1Id,
            makeEntryData(title="Before Regenerate", step_id=self.user1StepId),
        )

        conn = self.getTestConnection()
        roadmaps.create_roadmap(conn, self.user1Id, self.intakeId, sampleSteps, sampleNotNow)
        conn.close()

        portfolioController.update_portfolio_entry(
            self.user1Id,
            entryId,
            makeEntryData(title="After Regenerate", step_id=self.user1StepId),
        )

        entries = portfolioController.list_portfolio_entries(self.user1Id)
        self.assertEqual(entries[0]["title"], "After Regenerate")
        self.assertEqual(entries[0]["step_id"], self.user1StepId)

    def test_update_portfolio_entry_not_found_or_wrong_user_raises(self):
        entryId = portfolioController.add_portfolio_entry(self.user1Id, makeEntryData())

        with self.assertRaises(ValidationError):
            portfolioController.update_portfolio_entry(
                self.user2Id,
                entryId,
                makeEntryData(title="Hijack"),
            )

        with self.assertRaises(ValidationError):
            portfolioController.update_portfolio_entry(
                self.user1Id,
                99999,
                makeEntryData(),
            )

    def test_delete_portfolio_entry_removes_entry(self):
        entryId = portfolioController.add_portfolio_entry(self.user1Id, makeEntryData())

        portfolioController.delete_portfolio_entry(self.user1Id, entryId)

        entries = portfolioController.list_portfolio_entries(self.user1Id)
        self.assertEqual(entries, [])

    def test_delete_portfolio_entry_not_found_or_wrong_user_raises(self):
        entryId = portfolioController.add_portfolio_entry(self.user1Id, makeEntryData())

        with self.assertRaises(ValidationError):
            portfolioController.delete_portfolio_entry(self.user2Id, entryId)

        with self.assertRaises(ValidationError):
            portfolioController.delete_portfolio_entry(self.user1Id, 99999)


if __name__ == "__main__":
    unittest.main()