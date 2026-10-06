"""
Every color the views use, in one place.

Why: the Phase 3 Settings page adds a light/dark theme. If colors are
scattered through .kv files, dark mode means hunting down every literal.
With this file, dark mode is "add PALETTES['dark'] and point COLORS at it".

How screens use it
------------------
.kv files:   #:import theme views.theme      (first line of the file)
             color: theme.C.accent
Python:      from views.theme import C
             label.color = C.text_muted

`C.<name>` gives a Kivy RGBA tuple (four floats, 0-1). The palette itself
stores hex strings because that's how designers and the wireframes write
colors; hex_to_rgba() converts.

This module has no Kivy import, so it can be unit-tested and imported
anywhere.
"""

PALETTES = {
    "light": {
        # ---- Base palette (from the wireframe) --------------------------
        # The wireframe page background is white, so `background` is
        # #FFFFFF rather than the #F6F4EF in the original color table.
        "background": "#FFFFFF",
        "top_bar": "#FBFAF6",
        "surface": "#FFFFFF",
        "border": "#E5E0D3",
        "text": "#201C17",
        "text_body": "#2B2620",
        "text_muted": "#5A5346",
        "text_faint": "#837A6B",
        "accent": "#2F6F62",
        "accent_soft": "#EFF6F3",
        "accent_dark": "#1F4B41",
        "why_bg": "#F7FAF8",
        "notnow_bg": "#FBF5EA",
        "notnow_border": "#C9B48A",
        "notnow_card": "#FFFDF8",
        "notnow_text": "#5C4B2A",
        "error_border": "#D9B8A8",

        # ---- Extra dashboard colors taken from dashboard.html ----------
        "on_accent": "#FFFFFF",          # text/number drawn on an accent fill
        "eyebrow": "#7C6E4B",            # small uppercase labels
        "chip_bg": "#F3F0E8",            # est_time pill
        "why_text": "#33413C",           # reasoning text inside the why box
        "step_outline": "#DBD5C8",       # pending step circle, secondary button outline
        "text_label": "#423C33",         # "2 of 6 done", secondary button text
        "notnow_eyebrow": "#8A6A2E",
        "notnow_heading": "#3D2F14",
        "notnow_subtitle": "#6E5A33",

        # ---- Loading-state skeletons (dashboard_states.html) -----------
        "skeleton_bar": "#ECE8DE",
        "skeleton_why": "#F1F5F3",
        "skeleton_notnow_bar": "#F1E6D0",
        "spinner_track": "#DCE9E4",

        # ---- Phase 1 form screens --------------------------------------
        # login/signup/intake still use Kivy's default dark background.
        # These reproduce the literals they used before centralizing
        # (0.8,0.2,0.2 / 0.45 grey / 0.5 grey / fully transparent), so
        # those screens look the same.
        "form_error": "#CC3333",
        "form_subtitle": "#737373",
        "form_hint": "#808080",
        "clear": "#00000000",
    },
    # "dark": {...}  -- Phase 3 (Settings page). Same keys, different values.
}

COLORS = PALETTES["light"]


def hex_to_rgba(hex_color, alpha=None):
    """'#2F6F62' -> (0.184, 0.435, 0.384, 1.0), Kivy's RGBA format.

    Accepts #RRGGBB or #RRGGBBAA, with or without the '#'.
    `alpha`, if given, overrides the alpha channel.
    """
    value = hex_color.lstrip("#")
    if len(value) not in (6, 8):
        raise ValueError(f"Expected #RRGGBB or #RRGGBBAA, got {hex_color!r}")
    channels = [int(value[i:i + 2], 16) / 255 for i in range(0, len(value), 2)]
    if len(channels) == 3:
        channels.append(1.0)
    if alpha is not None:
        channels[3] = float(alpha)
    return tuple(channels)


def rgba(name, alpha=None):
    """Palette name -> Kivy RGBA tuple. rgba('accent', 0.5) for a faded accent."""
    return hex_to_rgba(COLORS[name], alpha)


class _ColorNamespace:
    """Lets KV write `theme.C.accent` instead of `theme.rgba("accent")`.

    A typo like `theme.C.acent` raises AttributeError naming the bad key,
    instead of silently drawing the wrong color.
    """

    def __getattr__(self, name):
        try:
            return rgba(name)
        except KeyError:
            raise AttributeError(f"No color named {name!r} in views/theme.py") from None


C = _ColorNamespace()
