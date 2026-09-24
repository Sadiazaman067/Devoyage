"""
intakes table.

SQLite has no native list/array type, so per the spec's JSON-string pattern:
coursework, skills, and carrying are stored as TEXT columns holding JSON, and
this module is the ONLY place that calls json.dumps/json.loads on them.
Controllers and views always see real Python lists in and out.

save_intake() expects intake_data to already be validated by Pydantic in the
controller layer (controllers/intake.py) -- this module trusts its shape but
does not re-validate enum values itself.
"""

import json

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS intakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    year TEXT NOT NULL,
    major_status TEXT NOT NULL,
    has_pipeline TEXT NOT NULL,
    coursework TEXT NOT NULL,
    skills TEXT NOT NULL,
    project_count TEXT NOT NULL,
    biggest_project_type TEXT NOT NULL,
    deployed TEXT NOT NULL,
    carrying TEXT NOT NULL,
    weekly_hours TEXT NOT NULL,
    credit_load TEXT NOT NULL,
    goal TEXT NOT NULL,
    free_text TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

# Fields that get JSON-encoded on the way in and decoded on the way out.
_JSON_FIELDS = ("coursework", "skills", "carrying")


def create_table(conn):
    conn.execute(CREATE_TABLE_SQL)


def save_intake(conn, user_id, intake_data):
    """
    intake_data: dict with keys matching the intakes shape in the spec exactly
    (year, major_status, has_pipeline, coursework, skills, project_count,
    biggest_project_type, deployed, carrying, weekly_hours, credit_load, goal,
    free_text). Returns the new intake_id.
    """
    cur = conn.execute(
        """
        INSERT INTO intakes (
            user_id, year, major_status, has_pipeline, coursework, skills,
            project_count, biggest_project_type, deployed, carrying,
            weekly_hours, credit_load, goal, free_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            intake_data["year"],
            intake_data["major_status"],
            intake_data["has_pipeline"],
            json.dumps(intake_data["coursework"]),
            json.dumps(intake_data["skills"]),
            intake_data["project_count"],
            intake_data["biggest_project_type"],
            intake_data["deployed"],
            json.dumps(intake_data["carrying"]),
            intake_data["weekly_hours"],
            intake_data["credit_load"],
            intake_data["goal"],
            intake_data.get("free_text"),
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_latest_intake(conn, user_id):
    """Most recent intake for a user, with JSON fields decoded back to lists."""
    row = conn.execute(
        """
        SELECT * FROM intakes
        WHERE user_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    if row is None:
        return None

    intake = dict(row)
    for field in _JSON_FIELDS:
        intake[field] = json.loads(intake[field])
    return intake
