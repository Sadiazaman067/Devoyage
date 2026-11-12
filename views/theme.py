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
        # ---- Milestone 3 palette (adopted 11/03, UX/UI Design Document) --
        # These are the names new code should use. Every text color below
        # passes the 4.5:1 contrast check on the background it sits on.
        "ink": "#34113F",           # dark amethyst: headings and body text
        "blue": "#166088",          # primary actions, active nav item, checks
        "mint": "#D4F2D2",          # Weekly Focus panel, "done" chips
        "mint_ink": "#1E5631",      # text on mint
        "crimson": "#931621",       # Not Now, danger actions, errors
        "bg": "#FFFFFF",            # page background
        "sidebar": "#F7F7F9",       # sidebar background
        "line": "#E7E4EA",          # card borders and dividers
        "muted": "#5E5566",         # secondary text
        "blue_tint": "#E8F1F6",     # active nav item, blue chips
        "crimson_tint": "#F8ECEE",  # Not Now panel, error boxes
        "chip_gray": "#F1EFF3",     # neutral chips (time estimates)
        "danger_border": "#E8C9CE", # outline of danger buttons and error boxes
        "checkbox": "#C9C3CF",      # unchecked checkbox outline
        "mint_soft": "#EFF8EE",     # Weekly Focus panel fill
        "mint_line": "#BFE3BC",     # Weekly Focus panel border
        "blue_line": "#A9CBDD",     # border of the expanded roadmap step
        "notnow_divider": "#EBD3D7",# lines between Not Now items

        # ---- Older names, kept so existing screens keep working ----------
        # The dashboard and forms were written against these. They now map
        # onto the Milestone 3 colors above, so every screen recolors from
        # this one file. Rename them in the .kv files as each screen is
        # rebuilt, then delete them here.
        "background": "#FFFFFF",
        "top_bar": "#F7F7F9",
        "surface": "#FFFFFF",
        "border": "#E7E4EA",
        "text": "#34113F",
        "text_body": "#34113F",
        "text_muted": "#5E5566",
        "text_faint": "#6F6776",
        "accent": "#166088",
        "accent_soft": "#E8F1F6",
        "accent_dark": "#0F4A6A",
        "why_bg": "#F7F7F9",
        "notnow_bg": "#F8ECEE",
        "notnow_border": "#E8C9CE",
        "notnow_card": "#FFFFFF",
        "notnow_text": "#5E5566",
        "error_border": "#E8C9CE",
        "on_accent": "#FFFFFF",
        "eyebrow": "#166088",
        "chip_bg": "#F1EFF3",
        "why_text": "#34113F",
        "step_outline": "#C9C3CF",
        "text_label": "#34113F",
        "notnow_eyebrow": "#931621",
        "notnow_heading": "#34113F",
        "notnow_subtitle": "#5E5566",
        "skeleton_bar": "#EEEBF0",
        "skeleton_why": "#F4F2F6",
        "skeleton_notnow_bar": "#F2DDE1",
        "spinner_track": "#D3E3EC",

        # ---- Phase 1 form screens (login, signup, intake) ---------------
        # Unchanged for now: these screens still draw on Kivy's default dark
        # background. They get the new colors when they're rebuilt.
        "form_error": "#CC3333",
        "form_subtitle": "#737373",
        "form_hint": "#808080",
        "clear": "#00000000",
    },
    # "dark": {...}  -- Settings theme switch. Same keys, different values.
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
