"""
Resources Hub (Module Contract screen id: "resources"), Tier 2 spec 11/17.

    list_resources(category=None) -> list of resources
      each: id, title, url, category, why, is_free, position

Category chips ask the controller for that category. The search box only
filters what's already on screen (title and "why"), so typing never calls
the controller. Open launches the url in the browser.
"""
import os
import webbrowser

from kivy.lang import Builder
from kivy.properties import BooleanProperty, ColorProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from views.components import AppPage, Card
from views.controllers_api import ValidationError, list_resources
from views.theme import C

Builder.load_file(os.path.join(os.path.dirname(__file__), "resources.kv"))

# Chip label and colors for each category in the spec.
CATEGORY_LABELS = {
    "learning": "Learning",
    "practice": "Practice",
    "tools": "Tools",
    "communities": "Communities",
    "career": "Career",
}


def _category_colors(category):
    return {
        "learning": (C.blue_tint, C.blue),
        "practice": (C.mint, C.mint_ink),
        "tools": (C.chip_gray, C.muted),
        "communities": (C.crimson_tint, C.crimson),
        "career": (C.sidebar, C.ink),
    }.get(category, (C.chip_gray, C.muted))


def initials(title):
    """Two or three letters for the badge on each card.

    'Major League Hacking' -> 'MLH', 'GitHub' -> 'GH', 'freeCodeCamp' -> 'FC',
    'CS50 (Harvard)' -> 'CS', 'VS Code' -> 'VS'.
    """
    words = title.replace("(", " ").replace(")", " ").split()
    first = words[0]
    letters_only = "".join(ch for ch in first if ch.isalpha())
    if letters_only.isupper() and len(letters_only) >= 2:
        return letters_only[:3]  # an acronym already: CS50, VS, MLH
    if len(words) >= 2:
        return "".join(w[0] for w in words[:3] if w[0].isalnum()).upper()
    # One word: first letter plus the next capital (freeCodeCamp -> FC).
    rest = [ch for ch in first[1:] if ch.isupper()]
    return (first[0] + (rest[0] if rest else first[1:2])).upper()


class CategoryChip(ButtonBehavior, Label):
    key = StringProperty("")  # "" means All
    active = BooleanProperty(False)


class ResourceCard(Card):
    title = StringProperty("")
    url = StringProperty("")
    why = StringProperty("")
    category_label = StringProperty("")
    initials = StringProperty("")
    is_free = BooleanProperty(False)
    chip_fill = ColorProperty((0, 0, 0, 0))
    chip_text = ColorProperty((0, 0, 0, 1))

    def open_link(self):
        webbrowser.open(self.url)


class ResourcesBody(BoxLayout):
    screen = ObjectProperty(None)


class ResourcesScreen(AppPage):
    nav_name = "resources"
    title = "Resources Hub"
    subtitle = "Tools, courses, and communities our team picked, with one reason for each."

    def on_kv_post(self, base_widget):
        self.body = ResourcesBody(screen=self)
        self.ids.content.add_widget(self.body)
        self.category = None
        self.resources = []
        chips = self.body.ids.chips
        for key, label in [("", "All")] + list(CATEGORY_LABELS.items()):
            chip = CategoryChip(text=label, key=key, active=(key == ""))
            chip.bind(on_release=lambda c: self.pick_category(c.key or None))
            chips.add_widget(chip)
        self.body.ids.search_field.ids.input.bind(text=lambda *_: self._show())

    def on_pre_enter(self, *args):
        self.pick_category(self.category)

    def pick_category(self, category):
        self.category = category
        for chip in self.body.ids.chips.children:
            chip.active = (chip.key or None) == category
        try:
            self.resources = list_resources(category)
        except ValidationError as error:
            self.resources = []
            self.body.ids.empty_label.text = str(error)
            return
        self._show()

    def _show(self):
        query = self.body.ids.search_field.text.strip().lower()
        shown = [
            r for r in self.resources
            if not query or query in r["title"].lower() or query in r["why"].lower()
        ]
        grid = self.body.ids.grid
        grid.clear_widgets()
        for r in shown:
            fill, text = _category_colors(r["category"])
            grid.add_widget(ResourceCard(
                title=r["title"], url=r["url"], why=r["why"],
                category_label=CATEGORY_LABELS.get(r["category"], r["category"]),
                initials=initials(r["title"]), is_free=bool(r.get("is_free")),
                chip_fill=fill, chip_text=text,
            ))
        self.body.ids.empty_label.text = "" if shown else "No resources match that search."
