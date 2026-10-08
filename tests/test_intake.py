import pytest
from pydantic import ValidationError

from controllers import intake as intake_controller
from models import db, users, intakes


def valid_intake_data():
    """Return a fresh valid intake payload for each test."""
    return {
        "year": "sophomore",
        "major_status": "declared",
        "has_pipeline": "yes",
        "coursework": ["intro", "oop"],
        "skills": [
            {
                "language": "python",
                "level": "multi_file",
            },
            {
                "language": "cpp",
                "level": "small_solo",
            },
        ],
        "project_count": "2_3",
        "biggest_project_type": "team",
        "deployed": "no",
        "carrying": ["leetcode", "research"],
        "weekly_hours": "5_10",
        "credit_load": "16_18",
        "goal": "internship",
        "free_text": "Interested in backend and systems work.",
    }


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    """
    Create a temporary SQLite database so the tests never touch
    the real devoyage.db.
    """

    database_path = tmp_path / "test_devoyage.db"

    # Save the real function before monkeypatching it.
    real_get_connection = db.get_connection

    # Create only the tables needed for these tests.
    conn = real_get_connection(database_path)

    users.create_table(conn)
    intakes.create_table(conn)
    conn.commit()

    # Create two users for isolation testing.
    user1_id = users.create_user(
        conn,
        email="user1@example.com",
        password_hash="fake_hash_1",
    )

    user2_id = users.create_user(
        conn,
        email="user2@example.com",
        password_hash="fake_hash_2",
    )

    conn.close()

    # When controllers/intake.py calls db.get_connection(),
    # redirect it to our temporary database.
    monkeypatch.setattr(
        intake_controller.db,
        "get_connection",
        lambda: real_get_connection(database_path),
    )

    return {
        "path": database_path,
        "user1_id": user1_id,
        "user2_id": user2_id,
        "get_connection": real_get_connection,
    }


def test_save_valid_intake(test_database):
    """A valid intake should be saved and return an intake ID."""

    user_id = test_database["user1_id"]

    intake_id = intake_controller.save_intake(
        user_id,
        valid_intake_data(),
    )

    assert intake_id is not None
    assert isinstance(intake_id, int)


def test_intake_round_trip(test_database):
    """
    Saving then reading an intake should preserve its values,
    including fields stored as JSON.
    """

    user_id = test_database["user1_id"]
    original_data = valid_intake_data()

    intake_controller.save_intake(
        user_id,
        original_data,
    )

    conn = test_database["get_connection"](test_database["path"])

    try:
        saved_intake = intakes.get_latest_intake(conn, user_id)
    finally:
        conn.close()

    assert saved_intake is not None

    assert saved_intake["year"] == original_data["year"]
    assert saved_intake["major_status"] == original_data["major_status"]
    assert saved_intake["has_pipeline"] == original_data["has_pipeline"]

    assert saved_intake["coursework"] == original_data["coursework"]
    assert saved_intake["skills"] == original_data["skills"]
    assert saved_intake["carrying"] == original_data["carrying"]

    assert saved_intake["project_count"] == original_data["project_count"]
    assert (
        saved_intake["biggest_project_type"]
        == original_data["biggest_project_type"]
    )

    assert saved_intake["deployed"] == original_data["deployed"]
    assert saved_intake["weekly_hours"] == original_data["weekly_hours"]
    assert saved_intake["credit_load"] == original_data["credit_load"]
    assert saved_intake["goal"] == original_data["goal"]
    assert saved_intake["free_text"] == original_data["free_text"]


def test_invalid_intake_is_rejected(test_database):
    """Pydantic should reject values outside the allowed schema."""

    user_id = test_database["user1_id"]

    bad_data = valid_intake_data()

    # Not one of freshman/sophomore/junior/senior.
    bad_data["year"] = "second_year"

    with pytest.raises(ValidationError):
        intake_controller.save_intake(
            user_id,
            bad_data,
        )

    # Verify invalid data was never inserted.
    conn = test_database["get_connection"](test_database["path"])

    try:
        saved_intake = intakes.get_latest_intake(conn, user_id)
    finally:
        conn.close()

    assert saved_intake is None


def test_users_have_separate_intakes(test_database):
    """One user's intake must never be returned for another user."""

    user1_id = test_database["user1_id"]
    user2_id = test_database["user2_id"]

    user1_data = valid_intake_data()
    user1_data["goal"] = "internship"
    user1_data["free_text"] = "User one intake"

    user2_data = valid_intake_data()
    user2_data["goal"] = "fundamentals"
    user2_data["free_text"] = "User two intake"

    intake_controller.save_intake(user1_id, user1_data)
    intake_controller.save_intake(user2_id, user2_data)

    conn = test_database["get_connection"](test_database["path"])

    try:
        user1_intake = intakes.get_latest_intake(conn, user1_id)
        user2_intake = intakes.get_latest_intake(conn, user2_id)
    finally:
        conn.close()

    assert user1_intake["user_id"] == user1_id
    assert user2_intake["user_id"] == user2_id

    assert user1_intake["goal"] == "internship"
    assert user2_intake["goal"] == "fundamentals"

    assert user1_intake["free_text"] == "User one intake"
    assert user2_intake["free_text"] == "User two intake"