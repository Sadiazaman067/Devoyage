"""
Signed-in pages that exist in the sidebar but aren't built yet: Portfolio Log.

Each one is an AppPage (sidebar + header) with a "coming soon" card, so the
navigation works end to end today. When a page is built, give it its own
views/<page>.py and .kv and remove it from here.
"""
from kivy.metrics import dp

from views.components import AppPage, Card, Icon
from kivy.uix.label import Label
from views.theme import C


class _PlaceholderPage(AppPage):
    icon_name = "sparkles"
    blurb = ""

    def on_kv_post(self, base_widget):
        card = Card(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(520), dp(170)),
            padding=[dp(24), dp(22)],
            spacing=dp(10),
        )
        card.add_widget(Icon(name=self.icon_name, color=C.blue))
        title = Label(
            text="Coming soon",
            bold=True,
            font_size="18sp",
            color=C.ink,
            halign="left",
            size_hint_y=None,
            height=dp(26),
        )
        title.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        body = Label(
            text=self.blurb,
            font_size="15sp",
            color=C.muted,
            halign="left",
            valign="top",
        )
        body.bind(size=lambda inst, size: setattr(inst, "text_size", size))
        card.add_widget(title)
        card.add_widget(body)
        self.ids.content.add_widget(card)
        self.ids.content.add_widget(Label())  # spacer pushes the card up


class PortfolioScreen(_PlaceholderPage):
    nav_name = "portfolio"
    title = "Portfolio Log"
    subtitle = "Keep track of what you've actually done."
    icon_name = "list"
    blurb = "Log your projects, courses, certificates, and hackathons, and link them to the roadmap steps they complete."
