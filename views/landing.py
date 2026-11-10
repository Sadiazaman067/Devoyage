"""
Landing screen (Module Contract screen id: "landing").

This is the very first screen a visitor sees. It holds no business
logic at all -- per the working agreement "views never touch the
database directly," a landing screen especially shouldn't, since it
doesn't even need user data. Its only job is routing to signup or
login, matching F1's user flow: "Visitor lands on homepage, signs up
[or logs in]."
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import os

Builder.load_file(os.path.join(os.path.dirname(__file__), "landing.kv"))


class LandingScreen(Screen):
    def go_to_signup(self):
        self.manager.current = "signup"

    def go_to_login(self):
        self.manager.current = "login"
