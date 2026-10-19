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

from views.controllers_api import log_in, has_completed_intake, AuthError # swap point: see views/controllers_api.py

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

        # Ask the controller, never the database, whether this user has
        # finished intake. No intake yet -> intake screen; otherwise dashboard.
        if has_completed_intake(user_id):
            self.manager.get_screen("dashboard").current_user_id = user_id
            self.manager.current = "dashboard"
        else:
            self.manager.get_screen("intake").set_current_user(user_id)
            self.manager.current = "intake"

    def go_to_signup(self):
        self.manager.current = "signup"
