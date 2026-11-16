"""
Sign-up screen (Module Contract screen id: "signup").

Per the AI rule, this conforms exactly to the Module Contract:
    sign_up(email, password) -> user_id
raises AuthError on a duplicate email.

The Confirm password field (Milestone 3 design) is checked here, on the
screen, before sign_up is called.

The view's only job is: collect the two fields, call the controller,
route on the result. No password handling, hashing, or SQLite ever
happens here -- that's Arnav's controllers/auth.py and Sadia's
models/, per the working agreement that views never touch the
database directly and everything crosses through controllers.
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import os

from views.controllers_api import sign_up, AuthError, ValidationError  # swap point: see views/controllers_api.py

Builder.load_file(os.path.join(os.path.dirname(__file__), "signup.kv"))


class SignUpScreen(Screen):
    def submit(self):
        email = self.ids.email_field.text.strip()
        password = self.ids.password_field.text
        confirm = self.ids.confirm_field.text

        if not email or not password:
            self._show_error("Email and password are both required.")
            return

        # Screen-only check (Milestone 3 design): the controller contract
        # doesn't change, sign_up still gets one password.
        if password != confirm:
            self._show_error("The passwords don't match.", field=self.ids.confirm_field)
            return

        try:
            user_id = sign_up(email, password)
        except (AuthError, ValidationError) as e:
            self._show_error(str(e))
            return

        self._clear_form()

        # F1 user flow: "Visitor lands on homepage, signs up, is taken to intake."
        self.manager.get_screen("intake").set_current_user(user_id)
        self.manager.current = "intake"

    def _show_error(self, message, field=None):
        self.ids.error_box.message = message
        for each in (self.ids.password_field, self.ids.confirm_field):
            each.invalid = each is field

    def _clear_form(self):
        self.ids.error_box.message = ""
        for each in (self.ids.password_field, self.ids.confirm_field):
            each.invalid = False
            each.text = ""
            each.revealed = False

    def go_to_login(self):
        self._clear_form()
        self.manager.current = "login"
