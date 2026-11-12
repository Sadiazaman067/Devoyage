"""
Devoyage entry point.

Per the working agreement, main.py's only job is app startup and
ScreenManager wiring -- no business logic lives here. That's
controllers/, owned by Arnav (auth, intake, roadmap) and Sugam
(services/ai.py).

DashboardScreen is the real Phase 2 screen (F3/F4) from
views/dashboard.py; it replaced the placeholder class that used to
live here.

11/11 (Milestone 3 redesign): views.components is imported first because it
registers the fonts and the shared widgets (Card, buttons, Sidebar) that
the screens' .kv files use. Signed-in pages all show the same sidebar, so
screens fade instead of sliding (a sliding sidebar looks broken).
"""
from kivy.app import App
from models import db
from kivy.uix.screenmanager import FadeTransition, ScreenManager

import views.components  # noqa: F401  fonts + shared widgets; must load before any screen
from views.landing import LandingScreen
from views.login import LoginScreen
from views.signup import SignUpScreen
from views.intake import IntakeScreen
from views.dashboard import DashboardScreen
from views.placeholder_pages import (
    CareerPathsScreen,
    PortfolioScreen,
    ResourcesScreen,
    SettingsScreen,
)


class DevoyageApp(App):
    
    def build(self):
        # Create the database tables if they don't exist yet (safe on every start).
        # Open one connection just for this, then close it. Controllers open their own.
        conn = db.get_connection()
        try:
            db.init_db(conn)
        finally:
            conn.close()  # "finally" means: close it even if init_db failed

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(LandingScreen(name="landing"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignUpScreen(name="signup"))
        sm.add_widget(IntakeScreen(name="intake"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(CareerPathsScreen(name="career_paths"))
        sm.add_widget(ResourcesScreen(name="resources"))
        sm.add_widget(PortfolioScreen(name="portfolio"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.current = "landing"
        return sm


if __name__ == "__main__":
    DevoyageApp().run()
