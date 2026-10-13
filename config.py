"""
config.ini read/write, via the built-in configparser (course requirement).

Rule from the spec: app preferences live in .ini, user data lives in the
database, and secrets (the Anthropic API key) NEVER go in config.ini --
config.ini gets committed to git, .env does not.

Usage:

    from config import get_setting, set_setting
    theme = get_setting("app", "theme")          # -> "light" (default) or whatever was saved
    set_setting("app", "theme", "dark")
"""

import configparser
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.ini"

# Defaults written to a fresh config.ini the first time the app runs.
# Extend this as Phase 3 settles what the settings page actually needs.
DEFAULTS = {
    "app": {
        "theme": "light",
        "text_size": "medium",
    },
    "database": {
        "path": "devoyage.db",
    },
}


def _parser_with_defaults():
    parser = configparser.ConfigParser()
    parser.read_dict(DEFAULTS)
    return parser


def load_settings(path=None):
    """
    Return a ConfigParser loaded from config.ini, creating the file with
    defaults on first run so the app never crashes on a missing file.
    """
    config_path = path or CONFIG_PATH
    parser = _parser_with_defaults()
    if config_path.exists():
        parser.read(config_path)
    else:
        save_settings(parser, config_path)
    return parser


def save_settings(parser, path=None):
    config_path = path or CONFIG_PATH
    with open(config_path, "w") as f:
        parser.write(f)


def get_setting(section, key, fallback=None, path=None):
    parser = load_settings(path)
    return parser.get(section, key, fallback=fallback)


def set_setting(section, key, value, path=None):
    parser = load_settings(path)
    if not parser.has_section(section):
        parser.add_section(section)
    parser.set(section, key, str(value))
    save_settings(parser, path)
# ---------------------------------------------------------------------------
# Per-user theme, stored in config.ini (one section per user: [user_3] etc.)
# ---------------------------------------------------------------------------

VALID_THEMES = ("light", "dark")


def get_user_theme(user_id, path=None):
    """
    Theme for one user. Falls back to the app-wide default ([app] theme) if
    this user has never picked one.
    """
    parser = load_settings(path)
    default = parser.get("app", "theme", fallback="light")
    return parser.get(f"user_{user_id}", "theme", fallback=default)


def set_user_theme(user_id, theme, path=None):
    """Save one user's theme. Only 'light' or 'dark' are allowed."""
    if theme not in VALID_THEMES:
        raise ValueError(f"theme must be one of {VALID_THEMES}, got {theme!r}")
    set_setting(f"user_{user_id}", "theme", theme, path=path)
