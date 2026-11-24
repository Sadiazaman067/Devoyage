"""Career Paths model (Tier 2). Seeded once, read-only in the app."""
import json

from models import seed_data


def create_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS career_paths (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            slug        TEXT NOT NULL UNIQUE,
            title       TEXT NOT NULL,
            summary     TEXT NOT NULL,
            day_to_day  TEXT NOT NULL,
            skills      TEXT NOT NULL,
            first_steps TEXT NOT NULL,
            position    INTEGER NOT NULL
        )
        """
    )
    conn.commit()


def _as_json(value):
    """seed_data holds real lists; the database holds JSON strings."""
    return value if isinstance(value, str) else json.dumps(value)


def seed(conn):
    """Load seed_data.CAREER_PATHS, only if the table is empty (safe every start)."""
    if conn.execute("SELECT COUNT(*) FROM career_paths").fetchone()[0] > 0:
        return
    for p in seed_data.CAREER_PATHS:
        conn.execute(
            """
            INSERT INTO career_paths
                (slug, title, summary, day_to_day, skills, first_steps, position)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                p["slug"], p["title"], p["summary"], p["day_to_day"],
                _as_json(p["skills"]), _as_json(p["first_steps"]), p["position"],
            ),
        )
    conn.commit()


def list_career_paths(conn):
    """All career paths in display order, with skills/first_steps as real lists."""
    cur = conn.execute("SELECT * FROM career_paths ORDER BY position, id")
    names = [c[0] for c in cur.description]
    out = []
    for row in cur.fetchall():
        d = dict(zip(names, row))
        d["skills"] = json.loads(d["skills"])
        d["first_steps"] = json.loads(d["first_steps"])
        out.append(d)
    return out
