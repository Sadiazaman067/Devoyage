"""
Login screen (Module Contract screen id: "login").

    log_in(email, password) -> user_id
raises AuthError on bad credentials.

Open item from the spec: whether log_in should also route through an
intake-completion check (straight to "intake" vs "dashboard"). That's
still undecided, so this view does the one thing that IS decided --
route to "dashboard" -- and is written so that swapping in the check
later is a one-line change in submit(), not a rewrite.
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import os

from views.controllers_api import log_in, AuthError  # swap point: see views/controllers_api.py

Builder.load_file(os.path.join(os.path.dirname(__file__), "login.kv"))


class LoginScreen(Screen):
    def submit(self):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text

        try:
            user_id = log_in(email, password)
        except AuthError as e:
            self.ids.error_label.text = str(e)
            return

        self.ids.error_label.text = ""

        # TODO(open item): once the team decides, an intake-completion
        # check belongs here -- e.g. route to "intake" instead of
        # "dashboard" when the user has no saved intake yet.
        dashboard = self.manager.get_screen("dashboard")
        dashboard.current_user_id = user_id
        self.manager.current = "dashboard"

    def go_to_signup(self):
        self.manager.current = "signup"
