"""
Login screen (Module Contract screen id: "login").

    log_in(email, password) -> user_id
raises AuthError on bad credentials.

After a successful log_in, the screen asks the controller
has_completed_intake(user_id) -> bool (decided 10/13) and routes to
"intake" if the user hasn't saved one yet, otherwise to "dashboard".
The screen never checks the database itself.
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import os

from kivy.app import App

from views.controllers_api import log_in, has_completed_intake, get_settings, AuthError, ValidationError  # swap point: see views/controllers_api.py

Builder.load_file(os.path.join(os.path.dirname(__file__), "login.kv"))


class LoginScreen(Screen):
    def submit(self):
        email_field = self.ids.email_field
        password_field = self.ids.password_field
        email = email_field.text.strip()
        password = password_field.text

        try:
            user_id = log_in(email, password)
        except (AuthError, ValidationError) as e:
            self._show_error(str(e))
            return

        self._clear_form()

        # Ask the controller, never the database, whether this user has
        # finished intake. No intake yet -> intake screen; otherwise dashboard.
        target = "dashboard" if has_completed_intake(user_id) else "intake"

        # Switch to the user's saved theme (Settings) BEFORE moving on: the
        # switch rebuilds every screen, so it has to happen while we're
        # still on this one. After it, self.manager is the old set of
        # screens, so use the app's current root from here on.
        App.get_running_app().apply_theme(self._saved_theme(user_id))
        App.get_running_app().root.current = target

    def _saved_theme(self, user_id):
        try:
            return get_settings(user_id).get("theme") or "light"
        except (ValidationError, AuthError):
            return "light"  # no intake yet, so no settings yet

    def _show_error(self, message):
        self.ids.error_box.message = message
        self.ids.password_field.invalid = True

    def _clear_form(self):
        # Don't leave the password sitting in the form for the next person.
        self.ids.error_box.message = ""
        self.ids.password_field.invalid = False
        self.ids.password_field.text = ""
        self.ids.password_field.revealed = False

    def go_to_signup(self):
        self._clear_form()
        self.manager.current = "signup"
