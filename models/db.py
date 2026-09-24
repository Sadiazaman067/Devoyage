"""
Connection + schema setup for the whole app.

Usage from a controller (or dev_check.py):

    from models import db
    conn = db.get_connection()
    db.init_db(conn)          # safe to call every startup -- CREATE TABLE IF NOT EXISTS
    ...
    conn.close()
"""

import sqlite3
from pathlib import Path

# devoyage.db lives at the repo root, next to main.py and config.ini.
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "devoyage.db"


def get_connection(db_path=None):
    """
    Open a sqlite3 connection with the settings every part of this app relies on:
    - foreign_keys ON, so a bad roadmap_id/user_id fails loudly instead of
      leaving orphaned rows.
    - row_factory = sqlite3.Row, so query results can be turned into plain
      dicts with dict(row) instead of index-juggling tuples.
    """
    path = str(db_path or DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    """
    Create every table if it doesn't already exist. Call this once at app
    startup (main.py) before any controller touches the database. Importing
    the sibling modules here (not at the top of the file) avoids a circular
    import, since users/intakes/roadmaps don't need to import db.py at all.
    """
    from models import users, intakes, roadmaps

    users.create_table(conn)
    intakes.create_table(conn)
    roadmaps.create_table(conn)  # also creates roadmap_steps + not_now_items
    conn.commit()
