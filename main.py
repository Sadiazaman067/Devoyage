"""
Devoyage entry point.

Per the working agreement, main.py's only job is app startup and
ScreenManager wiring -- no business logic lives here. That's
controllers/, owned by Arnav (auth, intake, roadmap) and Sugam
(services/ai.py).

DashboardScreen is the real Phase 2 screen (F3/F4) from
views/dashboard.py; it replaced the placeholder class that used to
live here. The wiring below didn't change.
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from views.landing import LandingScreen
from views.login import LoginScreen
from views.signup import SignUpScreen
from views.intake import IntakeScreen
from views.dashboard import DashboardScreen


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
