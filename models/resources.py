"""Resources Hub model (Tier 2). Seeded once, read-only in the app."""
from models import seed_data

CATEGORIES = ("learning", "practice", "tools", "communities", "career")


def create_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS resources (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT NOT NULL,
            url       TEXT NOT NULL CHECK (url LIKE 'https://%'),
            category  TEXT NOT NULL
                      CHECK (category IN ('learning','practice','tools','communities','career')),
            why       TEXT NOT NULL,
            is_free   INTEGER NOT NULL DEFAULT 1 CHECK (is_free IN (0, 1)),
            position  INTEGER NOT NULL
        )
        """
    )
    conn.commit()


def seed(conn):
    """Load seed_data.RESOURCES, only if the table is empty (safe every start)."""
    if conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0] > 0:
        return
    for r in seed_data.RESOURCES:
        conn.execute(
            """
            INSERT INTO resources (title, url, category, why, is_free, position)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (r["title"], r["url"], r["category"], r["why"], int(r["is_free"]), r["position"]),
        )
    conn.commit()


def list_resources(conn, category=None):
    """All resources in display order, or just one category."""
    sql = "SELECT * FROM resources"
    params = []
    if category is not None:
        sql += " WHERE category = ?"
        params.append(category)
    sql += " ORDER BY position, id"
    cur = conn.execute(sql, params)
    names = [c[0] for c in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]
