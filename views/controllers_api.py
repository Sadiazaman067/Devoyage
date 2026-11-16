"""
THE controller swap point for every view.

Views import controller functions from HERE and nowhere else. That
keeps the rule "views call only controller functions" in one place you
can check, and it means switching from the dev stubs to Arnav's real
controllers is a change to this file only -- no screen file changes.

Which block is active (switched 11/11, after #10, #14 and #15 merged):
  - B, the real controllers, is ACTIVE. auth, intake, and roadmap are all
    on main and match the contract.
  - A, the dev stubs, stays here commented out. To run the app without
    the AI key or a real database (for example, to work on layout), comment
    out B and uncomment A.
"""

# ---- Errors: the same real classes in both modes, so they sit outside A and B
from exceptions import AuthError, ValidationError, AIServiceError

# ---- A: dev stubs (off) -----------------------------------------------------
# from dev_stubs.controllers_stub import sign_up, log_in, log_out, save_intake, has_completed_intake
# from dev_stubs.roadmap_stub import get_current_roadmap, generate_roadmap, set_step_status
# from dev_stubs.settings_stub import (
#     get_settings, update_theme, update_weekly_hours, change_email,
#     change_password, regenerate_roadmap, clear_roadmap_data, make_weekly_focus,
# )
# get_weekly_focus = make_weekly_focus(get_current_roadmap)

# ---- B: real controllers (ACTIVE) -------------------------------------------
from controllers.auth import sign_up, log_in, log_out
from controllers.intake import save_intake, has_completed_intake
from controllers.roadmap import get_current_roadmap, generate_roadmap, set_step_status

# Settings + Weekly Focus. TEMPORARY try/except: Arnav's controllers/settings.py
# and get_weekly_focus are on feat/settings-weekly-focus, not on main yet.
# Until they're merged, the stand-ins in dev_stubs/settings_stub.py fill in.
# After the merge, delete the `except` part and keep the two real imports.
try:
    from controllers.settings import (
        get_settings, update_theme, update_weekly_hours, change_email,
        change_password, regenerate_roadmap, clear_roadmap_data,
    )
    from controllers.roadmap import get_weekly_focus
except ImportError:
    from dev_stubs.settings_stub import (
        get_settings, update_theme, update_weekly_hours, change_email,
        change_password, regenerate_roadmap, clear_roadmap_data, make_weekly_focus,
    )
    get_weekly_focus = make_weekly_focus(get_current_roadmap)

__all__ = [
    "sign_up",
    "log_in",
    "log_out",
    "save_intake",
    "has_completed_intake",
    "AuthError",
    "get_current_roadmap",
    "generate_roadmap",
    "set_step_status",
    "get_weekly_focus",
    "get_settings",
    "update_theme",
    "update_weekly_hours",
    "change_email",
    "change_password",
    "regenerate_roadmap",
    "clear_roadmap_data",
    "AIServiceError",
    "ValidationError",
]
