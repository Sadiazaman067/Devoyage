"""
Career Paths (Module Contract screen id: "career_paths"), Tier 2 spec 11/17.

    list_career_paths() -> list of career paths
      each: id, slug, title, summary, day_to_day, skills (list),
            first_steps (list), position

The four paths are on the left; clicking one shows its details on the right.
"""
import os
import textwrap

from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

from views.components import AppPage, Card, Chip
from views.controllers_api import ValidationError, list_career_paths
from views.theme import C

Builder.load_file(os.path.join(os.path.dirname(__file__), "career_paths.kv"))

# One icon per path slug in the spec.
PATH_ICONS = {
    "software_engineering": "code",
    "data": "database",
    "security": "shield",
    "machine_learning": "cpu",
}


def short_blurb(text, width=50):
    """The list shows the start of each summary, cut at a word, about two lines."""
    return textwrap.shorten((text or "").strip(), width=width, placeholder="...")


class PathItem(ButtonBehavior, Card):
    slug = StringProperty("")
    title = StringProperty("")
    blurb = StringProperty("")
    icon_name = StringProperty("compass")
    selected = BooleanProperty(False)


class FirstStepRow(BoxLayout):
    number = NumericProperty(1)
    text = StringProperty("")


class CareerPathsBody(BoxLayout):
    screen = ObjectProperty(None)
    icon_name = StringProperty("compass")
    title = StringProperty("")
    summary = StringProperty("")
    day_to_day = StringProperty("")


class CareerPathsScreen(AppPage):
    nav_name = "career_paths"
    title = "Career Paths"
    subtitle = "See what each path is like and how to start, written by our team."

    def on_kv_post(self, base_widget):
        self.body = CareerPathsBody(screen=self)
        self.ids.content.add_widget(self.body)
        self.paths = []
        self.selected_slug = None

    def on_pre_enter(self, *args):
        try:
            self.paths = list_career_paths()
        except ValidationError as error:
            self.paths = []
            self.body.ids.error_label.text = str(error)
            return
        self.body.ids.error_label.text = ""
        path_list = self.body.ids.path_list
        path_list.clear_widgets()
        for path in self.paths:
            item = PathItem(
                slug=path["slug"],
                title=path["title"],
                blurb=short_blurb(path["summary"]),
                icon_name=PATH_ICONS.get(path["slug"], "compass"),
            )
            item.bind(on_release=lambda it: self.select(it.slug))
            path_list.add_widget(item)
        path_list.add_widget(BoxLayout())  # spacer keeps the list at the top
        slugs = [p["slug"] for p in self.paths]
        self.select(self.selected_slug if self.selected_slug in slugs else (slugs[0] if slugs else None))

    def select(self, slug):
        self.selected_slug = slug
        for item in self.body.ids.path_list.children:
            if isinstance(item, PathItem):
                item.selected = item.slug == slug
        path = next((p for p in self.paths if p["slug"] == slug), None)
        if path is None:
            return
        body = self.body
        body.icon_name = PATH_ICONS.get(slug, "compass")
        body.title = path["title"]
        body.summary = path["summary"]
        body.day_to_day = path["day_to_day"]
        skills = body.ids.skills_box
        skills.clear_widgets()
        for skill in path["skills"]:
            skills.add_widget(Chip(text=skill, fill=C.blue_tint, color=C.blue))
        steps = body.ids.steps_box
        steps.clear_widgets()
        for number, text in enumerate(path["first_steps"], start=1):
            steps.add_widget(FirstStepRow(number=number, text=text))

    def go_to_resources(self):
        self.manager.current = "resources"
