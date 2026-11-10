"""
dev_stubs/ -- throwaway stand-ins for controllers that aren't on main yet.

NOT production code. Nothing here hashes passwords, validates with
Pydantic, or touches SQLite. It exists only so the Kivy views can be
clicked through before Arnav's real controllers land.

Only one file is allowed to import from this package:
views/controllers_api.py (the single swap point). When the real
controllers are on main and match the Module Contract, flip the import
block in that file and delete this package.

  controllers_stub.py  -- sign_up, log_in, log_out, save_intake, AuthError
  roadmap_stub.py      -- get_current_roadmap, generate_roadmap, AIServiceError
"""
