"""
users table.

Password hashing is Arnav's job (passlib/bcrypt, in controllers/auth.py) --
this module only ever stores and reads a hash it's handed. Never call
create_user() with a plain-text password; if a test ever prints a value from
this table and it looks like a real password, that's a Phase 1 gate failure.
"""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
)
"""


def create_table(conn):
    conn.execute(CREATE_TABLE_SQL)


def create_user(conn, email, password_hash):
    """
    Insert a new user. Returns the new user_id.
    Raises sqlite3.IntegrityError if the email is already taken -- let that
    bubble up to the controller, which turns it into AuthError per the spec.
    """
    cur = conn.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, password_hash),
    )
    conn.commit()
    return cur.lastrowid


def get_user_by_email(conn, email):
    row = conn.execute(
        "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    return dict(row) if row else None


def get_user_by_id(conn, user_id):
    row = conn.execute(
        "SELECT id, email, password_hash, created_at FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    return dict(row) if row else None
