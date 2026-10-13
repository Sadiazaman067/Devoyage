"""
Sign-up screen (Module Contract screen id: "signup").

Per the AI rule, this conforms exactly to the Module Contract:
    sign_up(email, password) -> user_id
raises AuthError on a duplicate email.

The view's only job is: collect the two fields, call the controller,
route on the result. No password handling, hashing, or SQLite ever
happens here -- that's Arnav's controllers/auth.py and Sadia's
models/, per the working agreement that views never touch the
database directly and everything crosses through controllers.
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import os

from views.controllers_api import sign_up, AuthError  # swap point: see views/controllers_api.py

Builder.load_file(os.path.join(os.path.dirname(__file__), "signup.kv"))


class SignUpScreen(Screen):
    def submit(self):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text

        if not email or not password:
            self.ids.error_label.text = "Email and password are both required."
            return

        try:
            user_id = sign_up(email, password)
        except AuthError as e:
            self.ids.error_label.text = str(e)
            return

        self.ids.error_label.text = ""

        # F1 user flow: "Visitor lands on homepage, signs up, is taken to intake."
        self.manager.get_screen("intake").set_current_user(user_id)
        self.manager.current = "intake"

    def go_to_login(self):
        self.manager.current = "login"
