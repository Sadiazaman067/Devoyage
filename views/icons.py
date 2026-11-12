"""
Icon names -> characters in the Lucide icon font (assets/fonts/lucide.ttf).

Use the Icon widget from views/components.kv:   Icon: name: "house"
Or any Label:  font_name: "Icons", text: icons.ICONS["house"]

To add an icon: find its name at lucide.dev, look up its code in
lucide-static's font/info.json (same version, 0.460.0), add a line here.
"""

ICONS = {
    "compass": "",
    "house": "",
    "briefcase": "",
    "book-open": "",
    "list": "",
    "settings": "",
    "log-out": "",
    "user": "",
    "target": "",
    "chart-column": "",
    "eye-off": "",
    "eye": "",
    "clock": "",
    "check": "",
    "search": "",
    "plus": "",
    "pencil": "",
    "trash": "",
    "external-link": "",
    "calendar": "",
    "chevron-down": "",
    "chevron-right": "",
    "arrow-right": "",
    "arrow-left": "",
    "sparkles": "",
    "alert": "",
    "lock": "",
    "mail": "",
    "moon": "",
    "sun": "",
    "refresh": "",
    "map": "",
    "lightbulb": "",
    "code": "",
    "trophy": "",
    "shield": "",
    "database": "",
    "cpu": "",
    "globe": "",
    "users": "",
    "wrench": "",
    "play": "",
    "clipboard": "",
    "x": "",
}


def icon(name):
    """ICONS lookup that names the bad key instead of drawing nothing."""
    try:
        return ICONS[name]
    except KeyError:
        raise KeyError(f"No icon named {name!r} in views/icons.py") from None
