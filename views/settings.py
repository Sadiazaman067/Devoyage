"""
Settings page (Module Contract screen id: "settings"), the course-required
settings page.

Three saved settings plus two roadmap actions, all through Arnav's Settings
controller (via views/controllers_api.py):

    get_settings(user_id) -> {"theme": ..., "weekly_hours": ...}
    update_theme(user_id, theme)               theme is per user, in config.ini
    update_weekly_hours(user_id, weekly_hours) edits the latest intake
    change_email(user_id, new_email)
    change_password(user_id, current_password, new_password)
    clear_roadmap_data(user_id)                keeps intake answers

Regenerate reuses the dashboard's generation (background thread + loading
state), which calls generate_roadmap -- the same thing regenerate_roadmap does.
"""
import os

from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView

from views.components import AppPage
from views.controllers_api import (
    AuthError,
    ValidationError,
    change_email,
    change_password,
    clear_roadmap_data,
    get_current_user_id,
    get_settings,
    update_theme,
    update_weekly_hours,
)

Builder.load_file(os.path.join(os.path.dirname(__file__), "settings.kv"))

HOURS_TEXT = {"under_5": "under 5", "5_10": "5-10", "10_15": "10-15", "15_plus": "15+"}


class SettingsBody(ScrollView):
    screen = ObjectProperty(None)
    theme_name = StringProperty("light")
    weekly_hours = StringProperty("")
    left_error = StringProperty("")
    left_success = StringProperty("")
    account_error = StringProperty("")
    account_success = StringProperty("")


class ConfirmClear(ModalView):
    on_yes = ObjectProperty(None)

    def confirmed(self):
        self.dismiss()
        if self.on_yes:
            self.on_yes()


class SettingsScreen(AppPage):
    nav_name = "settings"
    title = "Settings"
    subtitle = "Changes save right away and load next time you log in."

    def on_kv_post(self, base_widget):
        self.body = SettingsBody(screen=self)
        self.ids.content.add_widget(self.body)

    # ---- helpers ------------------------------------------------------------

    @property
    def user_id(self):
        return get_current_user_id()

    def _left(self, success="", error=""):
        self.body.left_success, self.body.left_error = success, error

    def _account(self, success="", error=""):
        self.body.account_success, self.body.account_error = success, error

    def on_pre_enter(self, *args):
        self._left()
        self._account()
        try:
            settings = get_settings(self.user_id)
        except (ValidationError, AuthError) as error:
            self._left(error=str(error))
            return
        self.body.theme_name = settings.get("theme") or "light"
        self.body.weekly_hours = settings.get("weekly_hours") or ""

    # ---- the three settings ---------------------------------------------------

    def set_theme(self, theme_name):
        if theme_name == self.body.theme_name:
            return
        try:
            update_theme(self.user_id, theme_name)
        except (ValidationError, AuthError) as error:
            self._left(error=str(error))
            return
        # Rebuilds every screen in the new colors and comes back here.
        App.get_running_app().apply_theme(theme_name, screen="settings")

    def set_hours(self, weekly_hours):
        if weekly_hours == self.body.weekly_hours:
            return
        try:
            update_weekly_hours(self.user_id, weekly_hours)
        except (ValidationError, AuthError) as error:
            self._left(error=str(error))
            return
        self.body.weekly_hours = weekly_hours
        self._left(success=f"Weekly hours updated to {HOURS_TEXT[weekly_hours]} a week.")

    def save_email(self):
        field = self.body.ids.email_field
        try:
            change_email(self.user_id, field.text)
        except (ValidationError, AuthError) as error:
            field.invalid = True
            self._account(error=str(error))
            return
        field.invalid = False
        field.text = ""
        self._account(success="Email updated. Use it next time you log in.")

    def update_password(self):
        current = self.body.ids.current_password_field
        new = self.body.ids.new_password_field
        try:
            change_password(self.user_id, current.text, new.text)
        except (ValidationError, AuthError) as error:
            self._account(error=str(error))
            return
        for field in (current, new):
            field.text = ""
            field.revealed = False
        self._account(success="Password updated.")

    # ---- roadmap actions ------------------------------------------------------

    def regenerate(self):
        dashboard = self.manager.get_screen("dashboard")
        dashboard.start_generation()  # shows the loading state right away
        self.manager.current = "dashboard"

    def confirm_clear(self):
        ConfirmClear(on_yes=self._clear).open()

    def _clear(self):
        try:
            clear_roadmap_data(self.user_id)
        except (ValidationError, AuthError) as error:
            self._left(error=str(error))
            return
        except Exception as error:  # noqa: BLE001
            # e.g. the model function isn't on main yet. Log it, tell the user.
            Logger.exception("Settings: clear_roadmap_data failed")
            self._left(error=f"Couldn't clear your roadmap: {error}")
            return
        self.manager.get_screen("dashboard").forget_roadmap()
        self._left(success="Roadmap cleared. Your intake answers are kept.")
