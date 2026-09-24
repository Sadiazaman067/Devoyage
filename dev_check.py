"""
A quick, throwaway sanity check for the database layer -- NOT the Phase 1
test checklist (that's Sugam's pytest suite in tests/). This just proves the
models work end to end before you hand them off to Arnav's controllers.

Run it with:

    python dev_check.py

It uses a separate devoyage_dev_check.db file so it never touches the real
devoyage.db, and deletes itself when done.
"""

import os
from pathlib import Path

from models import db, users, intakes, roadmaps

CHECK_DB_PATH = Path(__file__).resolve().parent / "devoyage_dev_check.db"


def main():
    if CHECK_DB_PATH.exists():
        os.remove(CHECK_DB_PATH)

    conn = db.get_connection(CHECK_DB_PATH)
    db.init_db(conn)

    # --- users: two accounts, each only ever sees its own data ---
    alice_id = users.create_user(conn, "alice@usm.edu", "not-a-real-hash-1")
    bob_id = users.create_user(conn, "bob@usm.edu", "not-a-real-hash-2")
    assert users.get_user_by_email(conn, "alice@usm.edu")["id"] == alice_id
    assert users.get_user_by_id(conn, bob_id)["email"] == "bob@usm.edu"
    print("[ok] users: created + fetched by email and by id")

    # duplicate email must fail, not silently create a second account
    try:
        users.create_user(conn, "alice@usm.edu", "another-hash")
        raise SystemExit("[FAIL] duplicate email was allowed")
    except Exception as e:
        print(f"[ok] duplicate email rejected ({type(e).__name__})")

    # --- intakes: round trip, including the JSON list fields ---
    intake_data = {
        "year": "sophomore",
        "major_status": "declared",
        "has_pipeline": "unsure",
        "coursework": ["intro", "oop", "dsa"],
        "skills": [{"language": "python", "level": "multi_file"}],
        "project_count": "2_3",
        "biggest_project_type": "solo",
        "deployed": "yes",
        "carrying": ["leetcode", "club_leadership"],
        "weekly_hours": "10_15",
        "credit_load": "16_18",
        "goal": "internship",
        "free_text": "targeting a summer 2027 internship",
    }
    intake_id = intakes.save_intake(conn, alice_id, intake_data)
    fetched = intakes.get_latest_intake(conn, alice_id)
    assert fetched["coursework"] == intake_data["coursework"]
    assert fetched["skills"] == intake_data["skills"]
    assert fetched["carrying"] == intake_data["carrying"]
    print("[ok] intakes: saved + reloaded, JSON fields decoded back to lists")

    # --- roadmaps: create with steps + not-now items, read back together ---
    steps = [
        {
            "title": "Build one multi-file Python project",
            "description": "Something with 3+ files that import each other.",
            "reasoning": "Alice has only done solo class projects; multi-file structure is the next skill gap before a team project.",
            "est_time": "2-3 weeks",
        },
        {
            "title": "Start a DSA practice habit",
            "description": "30 minutes, 3x/week, easy-to-medium problems.",
            "reasoning": "She's already doing LeetCode but sporadically; a fixed cadence compounds faster before internship season.",
            "est_time": "ongoing",
        },
    ]
    not_now = [
        {
            "title": "Hackathons",
            "reasoning": "She's already carrying club leadership + LeetCode at 10-15 hrs/week; adding a hackathon now risks burning out before the internship push.",
        },
    ]
    roadmap_id = roadmaps.create_roadmap(conn, alice_id, intake_id, steps, not_now)
    current = roadmaps.get_current_roadmap(conn, alice_id)
    assert current["id"] == roadmap_id
    assert [s["title"] for s in current["steps"]] == [s["title"] for s in steps]
    assert current["not_now_items"][0]["title"] == "Hackathons"
    print("[ok] roadmaps: created with steps + not-now items, fetched together")

    # --- progress tracking ---
    first_step_id = current["steps"][0]["id"]
    roadmaps.set_step_status(conn, first_step_id, "done")
    refreshed = roadmaps.get_current_roadmap(conn, alice_id)
    assert refreshed["steps"][0]["status"] == "done"
    print("[ok] roadmap_steps: status updates and persists")

    # --- no plain-text passwords, anywhere in this table ---
    for row in conn.execute("SELECT password_hash FROM users").fetchall():
        assert row["password_hash"].startswith("not-a-real-hash")  # dev_check only
    print("[ok] password_hash column never held a plain password in this run")

    conn.close()
    os.remove(CHECK_DB_PATH)
    print("\nAll checks passed. Models are ready for Arnav's controllers.")


if __name__ == "__main__":
    main()
