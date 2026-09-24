"""
roadmaps, roadmap_steps, and not_now_items -- one module because they're
always created and read together (one generation = one roadmap + its steps
+ its not-now list).

create_table() is Phase 1 scope: all five tables need to exist before Sugam's
Phase 1 checklist can run. create_roadmap() / get_current_roadmap() /
set_step_status() are Phase 2+ functions (features F3-F5) -- they're here
now, ready, but don't get wired into a controller until the Phase 1 gate
passes.
"""

CREATE_ROADMAPS_SQL = """
CREATE TABLE IF NOT EXISTS roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    intake_id INTEGER NOT NULL REFERENCES intakes(id),
    generated_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

CREATE_ROADMAP_STEPS_SQL = """
CREATE TABLE IF NOT EXISTS roadmap_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL REFERENCES roadmaps(id),
    position INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    est_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'done'))
)
"""

CREATE_NOT_NOW_ITEMS_SQL = """
CREATE TABLE IF NOT EXISTS not_now_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL REFERENCES roadmaps(id),
    title TEXT NOT NULL,
    reasoning TEXT NOT NULL
)
"""


def create_table(conn):
    conn.execute(CREATE_ROADMAPS_SQL)
    conn.execute(CREATE_ROADMAP_STEPS_SQL)
    conn.execute(CREATE_NOT_NOW_ITEMS_SQL)


# ---------------------------------------------------------------------------
# Phase 2+ functions (F3 roadmap generator, F4 not-now list, F5 progress)
# ---------------------------------------------------------------------------

def create_roadmap(conn, user_id, intake_id, steps, not_now_items):
    """
    steps: list of dicts with title, description, reasoning, est_time
        (already validated against the LLM Output Contract by services/ai.py)
    not_now_items: list of dicts with title, reasoning

    Saves the roadmap and both child lists in a single transaction --
    per the AI rule, we never save a partial roadmap. Returns the new
    roadmap_id.

    Regeneration policy: every call inserts a brand-new roadmap row.
    Old roadmaps are kept (history), and get_current_roadmap() always
    returns the most recent one -- "current" just means latest by
    generated_at for that user.
    """
    try:
        cur = conn.execute(
            "INSERT INTO roadmaps (user_id, intake_id) VALUES (?, ?)",
            (user_id, intake_id),
        )
        roadmap_id = cur.lastrowid

        for position, step in enumerate(steps, start=1):
            conn.execute(
                """
                INSERT INTO roadmap_steps
                    (roadmap_id, position, title, description, reasoning, est_time, status)
                VALUES (?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    roadmap_id,
                    position,
                    step["title"],
                    step["description"],
                    step["reasoning"],
                    step["est_time"],
                ),
            )

        for item in not_now_items:
            conn.execute(
                "INSERT INTO not_now_items (roadmap_id, title, reasoning) VALUES (?, ?, ?)",
                (roadmap_id, item["title"], item["reasoning"]),
            )

        conn.commit()
        return roadmap_id
    except Exception:
        conn.rollback()
        raise


def get_current_roadmap(conn, user_id):
    """
    The dashboard read: latest roadmap + its steps (position order) + its
    not-now items, in one function call -- so the controller doesn't make
    three separate round trips for one screen.
    Returns None if the user has never generated a roadmap.
    """
    roadmap_row = conn.execute(
        """
        SELECT * FROM roadmaps
        WHERE user_id = ?
        ORDER BY generated_at DESC, id DESC
        LIMIT 1
        """,
        (user_id,),
    ).fetchone()
    if roadmap_row is None:
        return None

    roadmap = dict(roadmap_row)

    step_rows = conn.execute(
        "SELECT * FROM roadmap_steps WHERE roadmap_id = ? ORDER BY position ASC",
        (roadmap["id"],),
    ).fetchall()
    roadmap["steps"] = [dict(row) for row in step_rows]

    not_now_rows = conn.execute(
        "SELECT * FROM not_now_items WHERE roadmap_id = ?",
        (roadmap["id"],),
    ).fetchall()
    roadmap["not_now_items"] = [dict(row) for row in not_now_rows]

    return roadmap


def set_step_status(conn, step_id, status):
    """status must be exactly 'pending' or 'done' -- the two Tier 1 strings."""
    if status not in ("pending", "done"):
        raise ValueError(f"status must be 'pending' or 'done', got {status!r}")
    conn.execute(
        "UPDATE roadmap_steps SET status = ? WHERE id = ?",
        (status, step_id),
    )
    conn.commit()
