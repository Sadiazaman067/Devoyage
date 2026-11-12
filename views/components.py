"""
Reusable widgets for the Milestone 3 design. Layout and drawing are in
components.kv; this file only declares the classes and their properties.

  Card          white box, 16dp corners, 1dp border (Kivy has no shadows,
                so the border does that job)
  Icon          one Lucide icon:   Icon: name: "house"
  Chip          small rounded label ("2-3 weeks", "Done")
  PrimaryButton / GhostButton / DangerButton
                the three button styles; optional icon on the left
  TextField     bordered text input with an icon on the left
  Sidebar       the left navigation on every signed-in page
  AppPage       base Screen for signed-in pages: sidebar + page header

Import this module once (main.py does) before any screen's .kv loads, so
the rules below exist when the screens use them.
"""
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

from views import fonts  # noqa: F401  (registers fonts before the .kv uses them)
from views.icons import icon
from views.theme import C


class Card(BoxLayout):
    bg_color = ColorProperty(C.bg)
    border_color = ColorProperty(C.line)
    radius = NumericProperty(16)
    border_width = NumericProperty(1)


class Icon(Label):
    name = StringProperty("")

    def on_name(self, _instance, value):
        self.text = icon(value) if value else ""


class Chip(Label):
    fill = ColorProperty(C.blue_tint)
    icon_name = StringProperty("")


class BaseButton(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    icon_name = StringProperty("")
    fill = ColorProperty(C.blue)
    fill_down = ColorProperty(C.accent_dark)
    outline = ColorProperty((0, 0, 0, 0))
    text_color = ColorProperty(C.bg)


class PrimaryButton(BaseButton):
    pass


class GhostButton(BaseButton):
    pass


class DangerButton(BaseButton):
    pass


class TextField(Card):
    icon_name = StringProperty("")
    hint_text = StringProperty("")
    password = BooleanProperty(False)


class NavItem(ButtonBehavior, BoxLayout):
    text = StringProperty("")
    icon_name = StringProperty("")
    target = StringProperty("")
    active = BooleanProperty(False)


# Sidebar entries: (screen name, label, icon). Order = order on screen.
NAV_ITEMS = [
    ("dashboard", "Dashboard", "house"),
    ("career_paths", "Career Paths", "briefcase"),
    ("resources", "Resources Hub", "book-open"),
    ("portfolio", "Portfolio Log", "list"),
    ("settings", "Settings", "settings"),
]


class Sidebar(BoxLayout):
    active = StringProperty("dashboard")
    nav_items = ListProperty(NAV_ITEMS)

    def go_to(self, screen_name):
        manager = App.get_running_app().root
        if manager.has_screen(screen_name) and manager.current != screen_name:
            manager.current = screen_name

    def log_out(self):
        # The dashboard already knows how to log out cleanly (clears the
        # session, stops a running generation, forgets the user on the
        # intake screen), so every page's Log out goes through it.
        manager = App.get_running_app().root
        manager.get_screen("dashboard").log_out_user()


class AppPage(Screen):
    """Base for signed-in pages. Subclasses set nav_name, title, subtitle,
    and put their content in the `content` box (see components.kv)."""
    nav_name = StringProperty("")
    title = StringProperty("")
    subtitle = StringProperty("")


Builder.load_file(os.path.join(os.path.dirname(__file__), "components.kv"))
