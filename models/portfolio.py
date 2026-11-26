"""Portfolio Log model (Tier 2). One row per entry a student records.

All functions take user_id so a student can only ever touch their own entries.
Bad input raises ValueError (same style as set_step_status).
"""
import re
from datetime import datetime

ENTRY_TYPES = ("project", "course", "hackathon", "application", "other")
_FIELDS = ("entry_type", "title", "start_date", "link", "note", "step_id")


def create_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolio_entries (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            entry_type  TEXT NOT NULL
                        CHECK (entry_type IN ('project','course','hackathon','application','other')),
            title       TEXT NOT NULL,
            start_date  TEXT NOT NULL,
            link        TEXT,
            note        TEXT,
            step_id     INTEGER REFERENCES roadmap_steps(id),
            created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()


def _clean(conn, user_id, entry):
    """Validate an entry dict and return the cleaned values."""
    entry_type = entry.get("entry_type")
    if entry_type not in ENTRY_TYPES:
        raise ValueError(f"entry_type must be one of {ENTRY_TYPES}, got {entry_type!r}")

    title = (entry.get("title") or "").strip()
    if not 1 <= len(title) <= 120:
        raise ValueError("title is required and must be 1 to 120 characters")

    start_date = entry.get("start_date") or ""
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date is required and must look like YYYY-MM-DD")

    link = (entry.get("link") or "").strip() or None
    if link is not None and not re.match(r"^https?://", link):
        raise ValueError("link must start with http:// or https://")

    note = (entry.get("note") or "").strip() or None
    if note is not None and len(note) > 500:
        raise ValueError("note must be 500 characters or fewer")

    step_id = entry.get("step_id")
    if step_id is not None:
        owned = conn.execute(
            """
            SELECT 1 FROM roadmap_steps s
            JOIN roadmaps r ON r.id = s.roadmap_id
            WHERE s.id = ? AND r.user_id = ?
            """,
            (step_id, user_id),
        ).fetchone()
        if owned is None:
            raise ValueError("step_id does not belong to this user")

    return entry_type, title, start_date, link, note, step_id


def _rows(cur):
    names = [c[0] for c in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def add_entry(conn, user_id, entry):
    """Insert an entry for this user and return its id."""
    values = _clean(conn, user_id, entry)
    cur = conn.execute(
        """
        INSERT INTO portfolio_entries
            (user_id, entry_type, title, start_date, link, note, step_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, *values),
    )
    conn.commit()
    return cur.lastrowid


def list_entries(conn, user_id, entry_type=None):
    """This user's entries, newest start_date first. Optional type filter."""
    sql = "SELECT * FROM portfolio_entries WHERE user_id = ?"
    params = [user_id]
    if entry_type is not None:
        sql += " AND entry_type = ?"
        params.append(entry_type)
    sql += " ORDER BY start_date DESC, id DESC"
    return _rows(conn.execute(sql, params))


def update_entry(conn, user_id, entry_id, entry):
    """Replace an entry's fields. Returns True if it was this user's entry."""
    values = _clean(conn, user_id, entry)
    cur = conn.execute(
        """
        UPDATE portfolio_entries
        SET entry_type = ?, title = ?, start_date = ?, link = ?, note = ?, step_id = ?
        WHERE id = ? AND user_id = ?
        """,
        (*values, entry_id, user_id),
    )
    conn.commit()
    return cur.rowcount == 1


def delete_entry(conn, user_id, entry_id):
    """Delete one of this user's entries. Returns True if a row was deleted."""
    cur = conn.execute(
        "DELETE FROM portfolio_entries WHERE id = ? AND user_id = ?",
        (entry_id, user_id),
    )
    conn.commit()
    return cur.rowcount == 1
