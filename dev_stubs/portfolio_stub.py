"""
Stand-ins for controllers/portfolio.py (Arnav, Tier 2 spec 11/17):

    add_portfolio_entry(user_id, entry_data) -> entry_id
    list_portfolio_entries(user_id, entry_type=None) -> list of entries
    update_portfolio_entry(user_id, entry_id, entry_data) -> None
    delete_portfolio_entry(user_id, entry_id) -> None

entry_data: entry_type, title, start_date, and optionally link, note,
step_id. Same names, arguments, rules, and dict fields as the spec.

In memory only, so entries are gone when the app quits. Arnav's real
controller also checks that step_id is a step in the user's current
roadmap; this stub only checks it's a whole number (the screen only offers
current steps anyway).
"""
from datetime import date, datetime

from exceptions import ValidationError

ENTRY_TYPES = ("project", "course", "hackathon", "application", "other")

_entries = {}  # entry_id -> entry dict
_next_id = 1


def _clean(entry_data):
    entry_type = entry_data.get("entry_type")
    if entry_type not in ENTRY_TYPES:
        raise ValidationError("Pick a type: project, course, hackathon, application, or other.")

    title = (entry_data.get("title") or "").strip()
    if not title:
        raise ValidationError("Give the entry a title.")
    if len(title) > 120:
        raise ValidationError("Keep the title under 120 characters.")

    start_date = (entry_data.get("start_date") or "").strip()
    try:
        date.fromisoformat(start_date)
    except ValueError:
        raise ValidationError("Start date must be a real date written as YYYY-MM-DD.") from None

    link = (entry_data.get("link") or "").strip() or None
    if link and not link.startswith(("http://", "https://")):
        raise ValidationError("Links must start with http:// or https://.")

    note = (entry_data.get("note") or "").strip() or None
    if note and len(note) > 500:
        raise ValidationError("Keep the note under 500 characters.")

    step_id = entry_data.get("step_id")
    if step_id is not None and (isinstance(step_id, bool) or not isinstance(step_id, int)):
        raise ValidationError("That roadmap step isn't valid.")

    return {
        "entry_type": entry_type, "title": title, "start_date": start_date,
        "link": link, "note": note, "step_id": step_id,
    }


def _owned(user_id, entry_id):
    entry = _entries.get(entry_id)
    if entry is None or entry["user_id"] != user_id:
        raise ValidationError("Entry not found.")
    return entry


def add_portfolio_entry(user_id, entry_data):
    global _next_id
    entry_id = _next_id
    _next_id += 1
    _entries[entry_id] = {
        "id": entry_id, "user_id": user_id, **_clean(entry_data),
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    return entry_id


def list_portfolio_entries(user_id, entry_type=None):
    if entry_type is not None and entry_type not in ENTRY_TYPES:
        raise ValidationError("Unknown entry type.")
    mine = [
        dict(e) for e in _entries.values()
        if e["user_id"] == user_id and (entry_type is None or e["entry_type"] == entry_type)
    ]
    # Newest start_date first, then newest id (same order as the spec).
    return sorted(mine, key=lambda e: (e["start_date"], e["id"]), reverse=True)


def update_portfolio_entry(user_id, entry_id, entry_data):
    _owned(user_id, entry_id).update(_clean(entry_data))


def delete_portfolio_entry(user_id, entry_id):
    _owned(user_id, entry_id)
    del _entries[entry_id]


def unlink_steps(user_id):
    """Stub-only helper for settings_stub.clear_roadmap_data: the spec says
    clearing the roadmap sets step_id to NULL on that user's entries."""
    for entry in _entries.values():
        if entry["user_id"] == user_id:
            entry["step_id"] = None
