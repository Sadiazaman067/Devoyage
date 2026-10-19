"""
THE controller swap point for every view.

Views import controller functions from HERE and nowhere else. That
keeps the rule "views call only controller functions" in one place you
can check, and it means switching from the dev stubs to Arnav's real
controllers is a change to this file only -- no screen file changes.

Why the stubs are active right now (checked on main, 10/06):
  - controllers/auth.py does not exist on main (the auth branch was
    merged and then reverted).
  - controllers/roadmap.py does not exist on main.
  - controllers/intake.py: fixed in PR #10 (save_intake(user_id, intake_data),
    controller owns the connection). Switch it together with auth: the real
    intake saves to the real database, which needs a real user from real login.
To switch: comment out block A and uncomment block B.
"""

# ---- A: dev stubs (ACTIVE) -------------------------------------------------
from dev_stubs.controllers_stub import sign_up, log_in, log_out, save_intake, has_completed_intake, AuthError
from dev_stubs.roadmap_stub import get_current_roadmap, generate_roadmap, AIServiceError

# ---- B: real controllers (use once they're on main and match the contract) --
# from controllers.auth import sign_up, log_in, log_out
# from controllers.intake import save_intake, has_completed_intake
# from controllers.roadmap import get_current_roadmap, generate_roadmap
# from controllers.exceptions import AuthError, AIServiceError  # TODO(team): confirm where these live

__all__ = [
    "sign_up",
    "log_in",
    "log_out",
    "save_intake",
    "has_completed_intake",
    "AuthError",
    "get_current_roadmap",
    "generate_roadmap",
    "AIServiceError",
]
