"""
Throwaway local stand-ins for controllers/auth.py and
controllers/intake.py -- matching the Module Contract's function
names and signatures exactly, so the views don't change at all when
you swap the real controllers back in.

Not real: no password hashing, no SQLite, no Pydantic. See this
folder's README.md before using this.
"""


from exceptions import AuthError, ValidationError


_fake_users = {}
_next_id = [1]
_users_with_intake = set()


def sign_up(email, password):
    if not email or "@" not in email:
        raise ValidationError("Please enter a valid email address.")
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")    
    if email in _fake_users:
        raise AuthError("An account with that email already exists.")
    user_id = _next_id[0]
    _next_id[0] += 1
    _fake_users[email] = {"user_id": user_id, "password": password}
    return user_id


def log_in(email, password):
    if not email or not password:
        raise ValidationError("Email and password cannot be empty.")
    record = _fake_users.get(email)
    if record is None or record["password"] != password:
        raise AuthError("Incorrect email or password.")
    return record["user_id"]


def log_out():
    pass


def save_intake(user_id, intake_data):
    for field in ("coursework", "carrying"):
        answers = intake_data.get(field, [])
        if "none" in answers and len(answers) > 1:
            raise ValidationError(f"In {field}, 'none' can't be combined with other answers.")
    # Real save_intake validates intake_data with Pydantic and writes
    # to SQLite via Sadia's models. This stub just proves the view
    # collected something shaped right.
    print(f"[stub] would save_intake for user {user_id}:")
    for key, value in intake_data.items():
        print(f"    {key}: {value!r}")
    _users_with_intake.add(user_id)
    return 1



def has_completed_intake(user_id):
    # Real version (PR #10) checks the database for a saved intake.
    return user_id in _users_with_intake