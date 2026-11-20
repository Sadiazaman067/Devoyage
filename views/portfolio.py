"""
Portfolio Log (Module Contract screen id: "portfolio"), Tier 2 spec 11/17.

    add_portfolio_entry(user_id, entry_data) -> entry_id
    list_portfolio_entries(user_id, entry_type=None) -> list of entries
    update_portfolio_entry(user_id, entry_id, entry_data) -> None
    delete_portfolio_entry(user_id, entry_id) -> None
      entry: id, user_id, entry_type, title, start_date, link, note,
             step_id, created_at

A summary bar (count per type), type filter chips, the entry list with
edit and delete, and an Add/Edit form. "Link to a roadmap step" offers the
steps from get_current_roadmap. No status (11/17 decision).
"""
import os
import webbrowser
from datetime import date

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView

from views.components import AppPage, Card
from views.controllers_api import (
    AuthError,
    ValidationError,
    add_portfolio_entry,
    delete_portfolio_entry,
    get_current_roadmap,
    get_current_user_id,
    list_portfolio_entries,
    update_portfolio_entry,
)
from views.resources import CategoryChip

Builder.load_file(os.path.join(os.path.dirname(__file__), "portfolio.kv"))

# (entry_type, label on one entry, label on the summary tile, icon)
ENTRY_TYPES = [
    ("project", "Project", "Projects", "code"),
    ("course", "Course", "Courses", "book-open"),
    ("hackathon", "Hackathon", "Hackathons", "trophy"),
    ("application", "Application", "Applications", "briefcase"),
    ("other", "Other", "Other", "clipboard"),
]
TYPE_LABEL = {key: one for key, one, _many, _icon in ENTRY_TYPES}
TYPE_ICON = {key: name for key, _one, _many, name in ENTRY_TYPES}


def pretty_date(value):
    """'2026-11-03' -> 'Nov 3, 2026'. Anything else is shown as given."""
    try:
        d = date.fromisoformat(value)
    except (TypeError, ValueError):
        return value or ""
    return f"{d:%b} {d.day}, {d.year}"


def guess_bad_field(message):
    """Which form field to outline in crimson for a controller error."""
    text = message.lower()
    for word, field in (("title", "title"), ("date", "start_date"),
                        ("link", "link"), ("http", "link"), ("note", "note")):
        if word in text:
            return field
    return ""


class SummaryTile(Card):
    count = NumericProperty(0)
    label = StringProperty("")
    icon_name = StringProperty("list")


class EntryCard(Card):
    screen = ObjectProperty(None)
    entry_id = NumericProperty(0)
    title = StringProperty("")
    meta = StringProperty("")
    note = StringProperty("")
    link = StringProperty("")
    link_display = StringProperty("")
    step_title = StringProperty("")
    icon_name = StringProperty("clipboard")

    def open_link(self):
        if self.link:
            webbrowser.open(self.link)


class PortfolioBody(BoxLayout):
    screen = ObjectProperty(None)
    success = StringProperty("")
    error = StringProperty("")


# ---- Add / Edit form ------------------------------------------------------

class StepOption(ButtonBehavior, Label):
    step_id = ObjectProperty(None, allownone=True)
    selected = BooleanProperty(False)


class StepDropDown(DropDown):
    pass


class EntryForm(ModalView):
    """One form for Add (entry=None) and Edit (entry=the entry dict)."""
    heading = StringProperty("Add an entry")
    save_text = StringProperty("Save entry")
    entry_type = StringProperty("project")
    step_id = ObjectProperty(None, allownone=True)
    step_label = StringProperty("")
    has_steps = BooleanProperty(False)
    error = StringProperty("")
    bad_field = StringProperty("")
    window_height = NumericProperty(Window.height)

    def __init__(self, screen, entry, steps, **kwargs):
        super().__init__(**kwargs)
        self.screen = screen
        self.entry = entry
        self.steps = steps  # [(step_id, "1. Title"), ...] from the current roadmap
        Window.bind(height=self.setter("window_height"))
        self.has_steps = bool(steps)

        chips = self.ids.type_chips
        for key, label, _many, _icon in ENTRY_TYPES:
            chip = CategoryChip(text=label, key=key)
            chip.bind(on_release=lambda c: self.pick_type(c.key))
            chips.add_widget(chip)

        if entry is None:
            self.heading, self.save_text = "Add an entry", "Save entry"
            self.pick_type("project")
            self.ids.date_field.text = date.today().isoformat()
            self.pick_step(None)
        else:
            self.heading, self.save_text = "Edit entry", "Save changes"
            self.pick_type(entry["entry_type"])
            self.ids.title_field.text = entry.get("title") or ""
            self.ids.date_field.text = entry.get("start_date") or ""
            self.ids.link_field.text = entry.get("link") or ""
            self.ids.note_input.text = entry.get("note") or ""
            # A step from an older roadmap can't be linked any more (the
            # controller only accepts steps in the current roadmap).
            current_ids = {step_id for step_id, _ in steps}
            self.pick_step(entry.get("step_id") if entry.get("step_id") in current_ids else None)

        self.ids.step_button.bind(on_touch_down=self._on_step_button_touch)

    def on_dismiss(self):
        Window.unbind(height=self.setter("window_height"))

    def pick_type(self, key):
        self.entry_type = key
        for chip in self.ids.type_chips.children:
            chip.active = chip.key == key

    def pick_step(self, step_id):
        self.step_id = step_id
        if not self.steps:
            self.step_label = "No roadmap yet, so there are no steps to link."
        elif step_id is None:
            self.step_label = "No step"
        else:
            self.step_label = dict(self.steps).get(step_id, "No step")

    def _on_step_button_touch(self, button, touch):
        if not button.collide_point(*touch.pos) or not self.steps:
            return False
        dropdown = StepDropDown(auto_width=False, width=button.width)
        for step_id, label in [(None, "No step")] + self.steps:
            option = StepOption(text=label, step_id=step_id, selected=(step_id == self.step_id))
            option.bind(on_release=lambda opt: (self.pick_step(opt.step_id), dropdown.dismiss()))
            dropdown.add_widget(option)
        dropdown.open(button)
        return True

    def entry_data(self):
        return {
            "entry_type": self.entry_type,
            "title": self.ids.title_field.text.strip(),
            "start_date": self.ids.date_field.text.strip(),
            "link": self.ids.link_field.text.strip() or None,
            "note": self.ids.note_input.text.strip() or None,
            "step_id": self.step_id,
        }

    def save(self):
        self.error, self.bad_field = "", ""
        if not self.ids.title_field.text.strip():
            self.error, self.bad_field = "Give the entry a title.", "title"
            return
        try:
            self.screen.save_entry(None if self.entry is None else self.entry["id"], self.entry_data())
        except (ValidationError, AuthError) as error:
            self.error = str(error)
            self.bad_field = guess_bad_field(self.error)
            return
        self.dismiss()


class ConfirmDeleteEntry(ModalView):
    entry_title = StringProperty("")
    when_confirmed = ObjectProperty(None)

    def confirmed(self):
        self.dismiss()
        if self.when_confirmed:
            self.when_confirmed()


# ---- Screen ---------------------------------------------------------------

class PortfolioScreen(AppPage):
    nav_name = "portfolio"
    title = "Portfolio Log"
    subtitle = "Keep track of what you build, take, and apply to."

    def on_kv_post(self, base_widget):
        self.body = PortfolioBody(screen=self)
        self.ids.content.add_widget(self.body)
        self.entry_type = None  # the filter; None = All
        self.entries = []       # what's on screen now
        # Strong reference: ids are weak proxies, and _show takes this label
        # out of the list's children check, so it must never be collected.
        self.empty_label = self.body.ids.empty_label.__self__
        self.tiles = {}
        for key, _one, many, icon_name in ENTRY_TYPES:
            tile = SummaryTile(label=many, icon_name=icon_name)
            self.tiles[key] = tile
            self.body.ids.summary.add_widget(tile)
        chips = self.body.ids.chips
        for key, label in [("", "All")] + [(k, many) for k, _one, many, _i in ENTRY_TYPES]:
            chip = CategoryChip(text=label, key=key, active=(key == ""))
            chip.bind(on_release=lambda c: self.pick_type(c.key or None))
            chips.add_widget(chip)

    @property
    def user_id(self):
        return get_current_user_id()

    def on_pre_enter(self, *args):
        self.body.success = ""
        self.body.error = ""
        self.refresh()

    # ---- loading ------------------------------------------------------------

    def _step_titles(self):
        """step_id -> "1. Title" for the current roadmap (empty if none)."""
        try:
            roadmap = get_current_roadmap(self.user_id)
        except (ValidationError, AuthError):
            return {}
        if not roadmap:
            return {}
        return {
            step["id"]: f'{step["position"]}. {step["title"]}'
            for step in sorted(roadmap.get("steps", []), key=lambda s: s["position"])
        }

    def pick_type(self, entry_type):
        self.entry_type = entry_type
        for chip in self.body.ids.chips.children:
            chip.active = (chip.key or None) == entry_type
        self.refresh()

    def refresh(self):
        user_id = self.user_id
        try:
            everything = list_portfolio_entries(user_id)
            self.entries = (
                everything if self.entry_type is None
                else list_portfolio_entries(user_id, self.entry_type)
            )
        except (ValidationError, AuthError) as error:
            self.entries = []
            self.body.error = f"Couldn't load your entries: {error}"
            self._show({})
            return
        for key, tile in self.tiles.items():
            tile.count = sum(1 for e in everything if e["entry_type"] == key)
        self._show(self._step_titles())

    def _show(self, step_titles):
        box = self.body.ids.entry_list
        empty = self.empty_label
        for child in list(box.children):
            if child is not empty:
                box.remove_widget(child)
        for e in self.entries:
            link = e.get("link") or ""
            box.add_widget(EntryCard(
                screen=self,
                entry_id=e["id"],
                title=e["title"],
                meta=f'{TYPE_LABEL.get(e["entry_type"], "Other")}  ·  Started {pretty_date(e["start_date"])}',
                note=e.get("note") or "",
                link=link,
                link_display=link.split("://", 1)[-1].rstrip("/"),
                step_title=step_titles.get(e.get("step_id"), ""),
                icon_name=TYPE_ICON.get(e["entry_type"], "clipboard"),
            ))
        if self.entries:
            empty.text = ""
        elif self.entry_type is None:
            empty.text = ("Nothing logged yet. Add a project, course, hackathon, "
                          "or application you've worked on.")
        else:
            empty.text = "No entries of this type yet."

    # ---- add / edit / delete ----------------------------------------------

    def _entry(self, entry_id):
        return next((e for e in self.entries if e["id"] == entry_id), None)

    def open_form(self, entry_id):
        self.body.success = ""
        self.body.error = ""
        steps = list(self._step_titles().items())
        EntryForm(screen=self, entry=self._entry(entry_id) if entry_id else None, steps=steps).open()

    def save_entry(self, entry_id, entry_data):
        """Called by EntryForm. Raises ValidationError so the form can show it."""
        if entry_id is None:
            add_portfolio_entry(self.user_id, entry_data)
            self.body.success = "Entry added."
        else:
            update_portfolio_entry(self.user_id, entry_id, entry_data)
            self.body.success = "Entry updated."
        self.refresh()

    def confirm_delete(self, entry_id):
        entry = self._entry(entry_id)
        if entry is None:
            return
        ConfirmDeleteEntry(entry_title=entry["title"], when_confirmed=lambda: self._delete(entry_id)).open()

    def _delete(self, entry_id):
        self.body.success = ""
        try:
            delete_portfolio_entry(self.user_id, entry_id)
        except (ValidationError, AuthError) as error:
            self.body.error = str(error)
            return
        self.body.success = "Entry deleted."
        self.refresh()
