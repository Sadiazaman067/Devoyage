"""
Throwaway local stand-ins for controllers/auth.py and
controllers/intake.py -- matching the Module Contract's function
names and signatures exactly, so the views don't change at all when
you swap the real controllers back in.

Not real: no password hashing, no SQLite, no Pydantic. See this
folder's README.md before using this.
"""


class AuthError(Exception):
    pass


_fake_users = {}
_next_id = [1]


def sign_up(email, password):
    if email in _fake_users:
        raise AuthError("An account with that email already exists.")
    user_id = _next_id[0]
    _next_id[0] += 1
    _fake_users[email] = {"user_id": user_id, "password": password}
    return user_id


def log_in(email, password):
    record = _fake_users.get(email)
    if record is None or record["password"] != password:
        raise AuthError("Incorrect email or password.")
    return record["user_id"]


def log_out():
    pass


def save_intake(user_id, intake_data):
    # Real save_intake validates intake_data with Pydantic and writes
    # to SQLite via Sadia's models. This stub just proves the view
    # collected something shaped right.
    print(f"[stub] would save_intake for user {user_id}:")
    for key, value in intake_data.items():
        print(f"    {key}: {value!r}")
    return 1
