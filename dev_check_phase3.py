"""
Phase 3 / Tier 2 sanity check for the database layer.

Like dev_check_phase2.py, this is NOT Sugam's pytest suite -- it just proves
YOUR part works: clear_roadmap_data, the Portfolio Log model, and the seeded
Career Paths and Resources tables.

Run it from the repo root:

    python dev_check_phase3.py

Uses its own throwaway database file and deletes it when done.
"""

import os
from pathlib import Path

from models import db, users, intakes, roadmaps, portfolio, career_paths, resources

CHECK_DB_PATH = Path(__file__).resolve().parent / "devoyage_phase3_check.db"

INTAKE = {
    "year": "sophomore",
    "major_status": "declared",
    "has_pipeline": "unsure",
    "coursework": ["intro", "oop"],
    "skills": [{"language": "python", "level": "small_solo"}],
    "project_count": "1",
    "biggest_project_type": "solo",
    "deployed": "no",
    "carrying": ["leetcode"],
    "weekly_hours": "5_10",
    "credit_load": "16_18",
    "goal": "internship",
    "free_text": None,
}


def make_steps(prefix, n):
    return [
        {
            "title": f"{prefix} step {i}",
            "description": f"{prefix} description {i}",
            "reasoning": f"{prefix} reasoning {i}",
            "est_time": "1 week",
        }
        for i in range(1, n + 1)
    ]


def entry(**overrides):
    base = {"entry_type": "project", "title": "Personal budget CLI", "start_date": "2026-10-26"}
    base.update(overrides)
    return base


def must_reject(label, user_id, bad_entry, conn):
    try:
        portfolio.add_entry(conn, user_id, bad_entry)
    except ValueError:
        return
    raise SystemExit(f"[FAIL] bad entry was accepted: {label}")


def count(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


def main():
    if CHECK_DB_PATH.exists():
        os.remove(CHECK_DB_PATH)

    conn = db.get_connection(CHECK_DB_PATH)
    db.init_db(conn)

    alice = users.create_user(conn, "alice@usm.edu", "hash-a")
    bob = users.create_user(conn, "bob@usm.edu", "hash-b")
    alice_intake = intakes.save_intake(conn, alice, INTAKE)
    bob_intake = intakes.save_intake(conn, bob, INTAKE)

    # 1. Seeds load, and calling init_db again does not duplicate them
    paths_before = len(career_paths.list_career_paths(conn))
    res_before = len(resources.list_resources(conn))
    assert paths_before > 0 and res_before > 0
    db.init_db(conn)
    assert len(career_paths.list_career_paths(conn)) == paths_before
    assert len(resources.list_resources(conn)) == res_before
    print(f"[ok] seeds loaded ({paths_before} career paths, {res_before} resources), init_db twice adds nothing")

    # 2. Career paths come back in order with real lists
    paths = career_paths.list_career_paths(conn)
    assert [p["position"] for p in paths] == sorted(p["position"] for p in paths)
    assert len({p["slug"] for p in paths}) == len(paths)
    for p in paths:
        assert isinstance(p["skills"], list) and p["skills"]
        assert isinstance(p["first_steps"], list) and p["first_steps"]
    print("[ok] career paths: display order, unique slugs, skills/first_steps are lists")

    # 3. Resources: https links, valid categories, category filter works
    allowed = {"learning", "practice", "tools", "communities", "career"}
    items = resources.list_resources(conn)
    assert all(r["url"].startswith("https://") for r in items)
    assert all(r["category"] in allowed for r in items)
    one_cat = items[0]["category"]
    filtered = resources.list_resources(conn, one_cat)
    assert filtered and all(r["category"] == one_cat for r in filtered)
    print("[ok] resources: https links, valid categories, category filter works")

    # 4. Portfolio: add, list (newest first), filter by type
    first = portfolio.add_entry(conn, alice, entry(title="Older", start_date="2026-09-01"))
    second = portfolio.add_entry(
        conn, alice, entry(title="Newer", entry_type="hackathon", start_date="2026-11-02",
                           link="https://example.com", note="48 hours")
    )
    listed = portfolio.list_entries(conn, alice)
    assert [e["id"] for e in listed] == [second, first]
    assert [e["id"] for e in portfolio.list_entries(conn, alice, "hackathon")] == [second]
    print("[ok] portfolio: add, newest first, filter by type")

    # 5. Bad input is rejected
    must_reject("bad type", alice, entry(entry_type="job"), conn)
    must_reject("empty title", alice, entry(title="   "), conn)
    must_reject("title too long", alice, entry(title="x" * 121), conn)
    must_reject("bad date", alice, entry(start_date="11/02/2026"), conn)
    must_reject("bad link", alice, entry(link="ftp://example.com"), conn)
    must_reject("note too long", alice, entry(note="n" * 501), conn)
    print("[ok] portfolio: bad type/title/date/link/note are rejected")

    # 6. Isolation: Bob can't see, change, or delete Alice's entries
    assert portfolio.list_entries(conn, bob) == []
    assert portfolio.update_entry(conn, bob, first, entry(title="hacked")) is False
    assert portfolio.delete_entry(conn, bob, first) is False
    assert len(portfolio.list_entries(conn, alice)) == 2
    assert portfolio.list_entries(conn, alice)[1]["title"] == "Older"
    print("[ok] isolation: Bob can't see, edit, or delete Alice's entries")

    # 7. Update and delete on your own entry
    assert portfolio.update_entry(conn, alice, first, entry(title="Renamed")) is True
    assert any(e["title"] == "Renamed" for e in portfolio.list_entries(conn, alice))
    assert portfolio.delete_entry(conn, alice, second) is True
    assert portfolio.delete_entry(conn, alice, second) is False
    print("[ok] portfolio: update works, delete works (and a second delete returns False)")

    # 8. Linking an entry to a roadmap step: own step ok, someone else's step rejected
    roadmaps.create_roadmap(conn, alice, alice_intake, make_steps("alice", 5),
                            [{"title": "Skip A", "reasoning": "why A"}])
    roadmaps.create_roadmap(conn, bob, bob_intake, make_steps("bob", 5),
                            [{"title": "Skip X", "reasoning": "why X"}])
    alice_step = roadmaps.get_current_roadmap(conn, alice)["steps"][0]["id"]
    bob_step = roadmaps.get_current_roadmap(conn, bob)["steps"][0]["id"]
    linked = portfolio.add_entry(conn, alice, entry(title="Linked", step_id=alice_step))
    must_reject("someone else's step", alice, entry(title="Steal", step_id=bob_step), conn)
    print("[ok] portfolio: can link own roadmap step, can't link someone else's")

    # 9. clear_roadmap_data: wipes only that user's roadmap data
    roadmaps.clear_roadmap_data(conn, alice)
    assert roadmaps.get_current_roadmap(conn, alice) is None
    assert count(conn, "SELECT COUNT(*) FROM roadmaps WHERE user_id = ?", (alice,)) == 0
    assert count(
        conn,
        "SELECT COUNT(*) FROM roadmap_steps WHERE roadmap_id NOT IN (SELECT id FROM roadmaps)",
    ) == 0
    assert count(
        conn,
        "SELECT COUNT(*) FROM not_now_items WHERE roadmap_id NOT IN (SELECT id FROM roadmaps)",
    ) == 0
    print("[ok] clear: Alice's roadmaps, steps and not-now items are gone, nothing orphaned")

    bob_roadmap = roadmaps.get_current_roadmap(conn, bob)
    assert bob_roadmap is not None and len(bob_roadmap["steps"]) == 5
    assert len(bob_roadmap["not_now_items"]) == 1
    print("[ok] clear: Bob's roadmap is untouched")

    assert intakes.get_latest_intake(conn, alice) is not None
    print("[ok] clear: Alice's intake answers are kept")

    kept = [e for e in portfolio.list_entries(conn, alice) if e["id"] == linked]
    assert len(kept) == 1 and kept[0]["step_id"] is None
    print("[ok] clear: portfolio entries are kept, their step link is just removed")

    roadmaps.clear_roadmap_data(conn, alice)  # nothing left to clear: must not crash
    print("[ok] clear: running it with nothing to clear is harmless")

    conn.close()
    os.remove(CHECK_DB_PATH)
    print("\nAll Phase 3 database checks passed.")


if __name__ == "__main__":
    main()