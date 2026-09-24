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
