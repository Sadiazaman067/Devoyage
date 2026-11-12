"""
Registers the app's fonts with Kivy. Imported once, by main.py, before any
screen loads.

After this runs:
  - every Label uses Inter by default (no font_name needed)
  - font_name: "InterSemiBold" for semibold text (bold: True gives Inter Bold)
  - font_name: "Lora" for the serif headlines; italic: True gives Lora italic
  - font_name: "Icons" draws Lucide icons (see views/icons.py)

The font files are in assets/fonts/ (licenses are next to them).
"""
import os

from kivy.core.text import DEFAULT_FONT, LabelBase

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")


def _path(filename):
    return os.path.join(FONT_DIR, filename)


def register_fonts():
    # Replacing DEFAULT_FONT makes Inter the font for every label in the app,
    # including the screens that haven't been rebuilt yet.
    LabelBase.register(
        DEFAULT_FONT,
        fn_regular=_path("Inter-Regular.ttf"),
        fn_bold=_path("Inter-Bold.ttf"),
    )
    LabelBase.register("Inter", fn_regular=_path("Inter-Regular.ttf"), fn_bold=_path("Inter-Bold.ttf"))
    LabelBase.register("InterSemiBold", fn_regular=_path("Inter-SemiBold.ttf"), fn_bold=_path("Inter-Bold.ttf"))
    LabelBase.register(
        "Lora",
        fn_regular=_path("Lora-SemiBold.ttf"),
        fn_italic=_path("Lora-SemiBoldItalic.ttf"),
    )
    LabelBase.register("Icons", fn_regular=_path("lucide.ttf"))


register_fonts()
