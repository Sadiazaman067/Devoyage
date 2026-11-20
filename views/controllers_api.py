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
# from dev_stubs.controllers_stub import sign_up, log_in, log_out, get_current_user_id, save_intake, has_completed_intake
# from dev_stubs.roadmap_stub import get_current_roadmap, generate_roadmap, set_step_status
# from dev_stubs.settings_stub import (
#     get_settings, update_theme, update_weekly_hours, change_email,
#     change_password, regenerate_roadmap, clear_roadmap_data, make_weekly_focus,
# )
# get_weekly_focus = make_weekly_focus(get_current_roadmap)
# from dev_stubs.content_stub import list_career_paths, list_resources
# from dev_stubs.portfolio_stub import (
#     add_portfolio_entry, list_portfolio_entries,
#     update_portfolio_entry, delete_portfolio_entry,
# )

# ---- B: real controllers (ACTIVE) -------------------------------------------
from controllers.auth import sign_up, log_in, log_out, get_current_user_id
from controllers.intake import save_intake, has_completed_intake
from controllers.roadmap import get_current_roadmap, generate_roadmap, set_step_status

# Settings + Weekly Focus (Arnav, #17)
from controllers.settings import (
    get_settings, update_theme, update_weekly_hours, change_email,
    change_password, regenerate_roadmap, clear_roadmap_data,
)
from controllers.roadmap import get_weekly_focus

# Career Paths + Resources Hub. TEMPORARY try/except: Arnav's
# controllers/content.py isn't on main yet. Until it is, the stand-ins in
# dev_stubs/content_stub.py fill in. After it merges, keep only the import.
try:
    from controllers.content import list_career_paths, list_resources
except ImportError:
    from dev_stubs.content_stub import list_career_paths, list_resources

# Portfolio Log. TEMPORARY try/except, same reason: Arnav's
# controllers/portfolio.py isn't on main yet. After it merges, keep only
# the import.
try:
    from controllers.portfolio import (
        add_portfolio_entry, list_portfolio_entries,
        update_portfolio_entry, delete_portfolio_entry,
    )
except ImportError:
    from dev_stubs.portfolio_stub import (
        add_portfolio_entry, list_portfolio_entries,
        update_portfolio_entry, delete_portfolio_entry,
    )

__all__ = [
    "sign_up",
    "log_in",
    "log_out",
    "get_current_user_id",
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
    "list_career_paths",
    "list_resources",
    "add_portfolio_entry",
    "list_portfolio_entries",
    "update_portfolio_entry",
    "delete_portfolio_entry",
    "AIServiceError",
    "ValidationError",
]
