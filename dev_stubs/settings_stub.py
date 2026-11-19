"""
Stand-ins for controllers/settings.py and controllers.roadmap.get_weekly_focus
(Arnav's feat/settings-weekly-focus branch), with the same names and
signatures. In memory only.

Used two ways (see views/controllers_api.py):
  - in stub mode (block A), always
  - in real mode (block B), only until Arnav's branch is merged into main
"""
from exceptions import AuthError, ValidationError

VALID_WEEKLY_HOURS = ("under_5", "5_10", "10_15", "15_plus")
FOCUS_COUNT = {"under_5": 1, "5_10": 2, "10_15": 3, "15_plus": 3}

_settings = {}  # user_id -> {"theme": ..., "weekly_hours": ...}


def _for(user_id):
    return _settings.setdefault(user_id, {"theme": "light", "weekly_hours": "5_10"})


def get_settings(user_id):
    return dict(_for(user_id))


def update_theme(user_id, theme):
    if theme not in ("light", "dark"):
        raise ValidationError("Theme must be 'light' or 'dark'.")
    _for(user_id)["theme"] = theme


def update_weekly_hours(user_id, weekly_hours):
    if weekly_hours not in VALID_WEEKLY_HOURS:
        raise ValidationError("Invalid weekly hours.")
    _for(user_id)["weekly_hours"] = weekly_hours


def change_email(user_id, new_email):
    if not new_email or "@" not in new_email:
        raise ValidationError("Valid email address required.")


def change_password(user_id, current_password, new_password):
    if not current_password:
        raise ValidationError("Current password required.")
    if not new_password or len(new_password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")


def regenerate_roadmap(user_id):
    from dev_stubs.roadmap_stub import generate_roadmap
    return generate_roadmap(user_id)


def clear_roadmap_data(user_id):
    from dev_stubs import portfolio_stub, roadmap_stub
    roadmap_stub._roadmaps_by_user.pop(user_id, None)
    portfolio_stub.unlink_steps(user_id)  # spec: entries stay, step links go


def make_weekly_focus(get_current_roadmap):
    """Builds get_weekly_focus on top of whichever get_current_roadmap is active."""
    def get_weekly_focus(user_id):
        roadmap = get_current_roadmap(user_id)
        if roadmap is None:
            return []
        pending = [step for step in roadmap["steps"] if step["status"] == "pending"]
        return pending[:FOCUS_COUNT[_for(user_id)["weekly_hours"]]]
    return get_weekly_focus
