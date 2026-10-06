"""
Devoyage entry point.

Per the working agreement, main.py's only job is app startup and
ScreenManager wiring -- no business logic lives here. That's
controllers/, owned by Arnav (auth, intake, roadmap) and Sugam
(services/ai.py).

DashboardScreen below is a placeholder: F3/F4 (Phase 2) haven't been
built yet, so this just gives login/intake somewhere real to land
without crashing. Whoever builds the real dashboard screen replaces
this class, not this file's wiring.
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label

from views.landing import LandingScreen
from views.login import LoginScreen
from views.signup import SignUpScreen
from views.intake import IntakeScreen


class DashboardScreen(Screen):
    """Placeholder until Phase 2 (F3/F4) builds the real dashboard."""

    current_user_id = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Dashboard -- coming in Phase 2"))


class DevoyageApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LandingScreen(name="landing"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignUpScreen(name="signup"))
        sm.add_widget(IntakeScreen(name="intake"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.current = "landing"
        return sm


if __name__ == "__main__":
    DevoyageApp().run()
