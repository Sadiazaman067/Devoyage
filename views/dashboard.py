"""
Dashboard screen (Module Contract screen id: "dashboard"), features F3 + F4.

What it shows:
  - the user's roadmap steps, in the order the controller returns them
    (position order -- this file never re-sorts), each with its reasoning
  - the "not now" list, styled to look nothing like a step
  - read-only progress ("2 of 6 done"); checkboxes come in Phase 3 with
    set_step_status, so status is display-only here

Its three states (Phase 2 brief: "loading state while generation runs;
UI must not freeze"):
  1. ROADMAP  -- get_current_roadmap(user_id) returned one: render it.
  2. LOADING  -- it returned None: run generate_roadmap(user_id) on a
                 background thread and show "Building your roadmap".
  3. ERROR    -- generation raised AIServiceError: show the error card
                 with "Try again" and "Edit my intake".

Layout lives in dashboard.kv. This file holds the behaviour; pure data
logic (progress text, dates, layout breakpoint) is in dashboard_helpers.py.
"""
import os
import threading
from functools import partial

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

# ---- Controller calls: the ONE place this screen imports them ---------------
# Today these come from dev_stubs/ (controllers/roadmap.py isn't on main).
# To use Arnav's real controller, flip the import block in
# views/controllers_api.py -- nothing in this file changes.
from views.controllers_api import (
    AIServiceError,
    generate_roadmap,
    get_current_roadmap,
    log_out,
)

from views.dashboard_helpers import (
    DONE,
    eyebrow_text,
    headline,
    next_step_index,
    progress_fraction,
    progress_text,
)

Builder.load_file(os.path.join(os.path.dirname(__file__), "dashboard.kv"))


# ---------------------------------------------------------------------------
# Small widgets. Their look is in dashboard.kv (rules named after each class);
# Python only declares the properties the KV rules read.
# ---------------------------------------------------------------------------

class StepNumber(Widget):
    """The numbered circle: filled with accent when done, outlined otherwise."""

    number = NumericProperty(0)
    done = BooleanProperty(False)
    up_next = BooleanProperty(False)


class StepCard(BoxLayout):
    """One roadmap step. Read-only: no checkbox until Phase 3."""

    position = NumericProperty(0)
    title = StringProperty("")
    description = StringProperty("")
    reasoning = StringProperty("")
    est_time = StringProperty("")
    done = BooleanProperty(False)
    up_next = BooleanProperty(False)  # first pending step gets an accent border + badge


class NotNowCard(BoxLayout):
    """One not-now item: a title and why to skip it for now."""

    title = StringProperty("")
    reasoning = StringProperty("")


class LoadingRing(Widget):
    """A spinning arc. It's animated by Clock on the main thread, so if it keeps
    turning while generate_roadmap sleeps, that proves the UI isn't frozen."""

    angle = NumericProperty(0)
    _event = None

    def start(self):
        if self._event is None:
            # Call _spin about 60 times a second, on the main thread.
            self._event = Clock.schedule_interval(self._spin, 1 / 60)

    def stop(self):
        if self._event is not None:
            self._event.cancel()
            self._event = None

    def _spin(self, dt):
        # dt = seconds since the last call, so the speed doesn't depend on frame rate.
        self.angle = (self.angle + 400 * dt) % 360


# ---------------------------------------------------------------------------
# The three bodies the screen swaps between (top bar stays put above them).
# `stacked` and `side_pad` are computed in dashboard.kv from the view's width.
# ---------------------------------------------------------------------------

class DashboardRoadmapView(ScrollView):
    stacked = BooleanProperty(False)
    side_pad = NumericProperty(0)
    eyebrow = StringProperty("")
    headline_text = StringProperty("")
    progress = NumericProperty(0)
    progress_label = StringProperty("")

    def show(self, roadmap):
        steps = roadmap.get("steps") or []
        not_now_items = roadmap.get("not_now_items") or []

        self.eyebrow = eyebrow_text(roadmap.get("generated_at"))
        self.headline_text = headline(steps)
        self.progress = progress_fraction(steps)
        self.progress_label = progress_text(steps)

        up_next_index = next_step_index(steps)
        steps_box = self.ids.steps_box
        steps_box.clear_widgets()
        # enumerate() walks the list in the order the controller returned it,
        # which is position order. No sorting here, on purpose.
        for index, step in enumerate(steps):
            steps_box.add_widget(StepCard(
                position=step.get("position", index + 1),
                title=step.get("title", ""),
                description=step.get("description", ""),
                reasoning=step.get("reasoning", ""),
                est_time=step.get("est_time") or "",
                done=step.get("status") == DONE,
                up_next=index == up_next_index,
            ))

        items_box = self.ids.notnow_items
        items_box.clear_widgets()
        for item in not_now_items:
            items_box.add_widget(NotNowCard(
                title=item.get("title", ""),
                reasoning=item.get("reasoning", ""),
            ))


class DashboardLoadingView(BoxLayout):
    stacked = BooleanProperty(False)
    side_pad = NumericProperty(0)

    def start(self):
        self.ids.ring.start()

    def stop(self):
        self.ids.ring.stop()


class DashboardErrorView(BoxLayout):
    stacked = BooleanProperty(False)
    side_pad = NumericProperty(0)
    screen = ObjectProperty(None)   # the DashboardScreen, so the buttons can call it
    detail = StringProperty("")     # the exception's human-readable message (spec: "show the message")


# ---------------------------------------------------------------------------
# The screen
# ---------------------------------------------------------------------------

class DashboardScreen(Screen):
    # Who's signed in. LoginScreen.submit() (and IntakeScreen.submit()) set
    # this, the same way the Phase 1 screens hand identity to each other.
    # PLACEHOLDER: the spec says the controller layer should track the
    # logged-in user_id in one place and views shouldn't pass it around.
    # No such controller exists on main yet, so this follows the existing
    # screens rather than inventing a new mechanism.
    current_user_id = None

    stacked = BooleanProperty(False)       # narrow window -> tighter top bar padding
    has_settings = BooleanProperty(False)  # "Settings" is disabled until a settings screen exists

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._body_view = None
        self._generating = False
        # Bumped every time we start generating or log out. A background result
        # carrying an old number is stale and gets thrown away (see _on_generation_done).
        self._generation_id = 0

    # ---- lifecycle --------------------------------------------------------

    def on_pre_enter(self, *args):
        # on_pre_enter runs BEFORE the slide-in transition starts, so the
        # screen already shows the right state (roadmap or loading) as it
        # slides in. on_enter would run after the slide, showing the previous
        # content (or nothing) during the animation.
        self.has_settings = self.manager.has_screen("settings")
        self.load_roadmap()

    def on_leave(self, *args):
        # Nobody can see the spinner now; stop its 60-per-second Clock callback.
        self._stop_body_animations()

    # ---- state machine ----------------------------------------------------

    def load_roadmap(self):
        if self.current_user_id is None:
            # Nobody signed in. Switching screens in the middle of a transition
            # is unreliable, so ask Clock to do it on the next frame instead.
            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "landing"))
            return

        if self._generating:
            # A generation from earlier is still running; keep waiting for it.
            self.show_loading()
            return

        # A quick database read, fine to do on the main thread.
        roadmap = get_current_roadmap(self.current_user_id)
        if roadmap is None:
            self.start_generation()
        else:
            self.render_roadmap(roadmap)

    def start_generation(self):
        if self._generating:
            return  # double-click on "Try again" shouldn't start two AI calls
        self._generating = True
        self._generation_id += 1
        self.show_loading()

        # generate_roadmap can take up to a minute. If we called it right here,
        # Kivy's main loop would be stuck inside this function: no redraws, no
        # clicks, and the OS would mark the window "Not Responding". So it runs
        # on a separate thread while the main loop keeps drawing and handling
        # input. daemon=True means a still-running worker won't stop the app
        # from quitting.
        worker = threading.Thread(
            target=self._generate_in_background,
            args=(self.current_user_id, self._generation_id),
            daemon=True,
        )
        worker.start()

    def _generate_in_background(self, user_id, generation_id):
        # ------------------------------------------------------------------
        # THIS RUNS ON THE WORKER THREAD.
        # Rule: no widgets, no Kivy properties, no self.ids in here. Kivy's
        # widgets and its OpenGL drawing are only safe on the main thread.
        # The only safe way back is Clock.schedule_once, which queues a
        # function for the main thread to run on its next frame.
        # user_id and generation_id were copied in as arguments, so this
        # function doesn't even read the screen's attributes.
        # ------------------------------------------------------------------
        try:
            roadmap = generate_roadmap(user_id)
        except AIServiceError as error:
            # Expected failure (bad AI response, network, etc.).
            # str(error) is taken NOW: Python deletes `error` when this except
            # block ends, so a lambda that used `error` later would crash.
            Clock.schedule_once(partial(self._on_generation_failed, str(error), generation_id))
        except Exception as error:  # noqa: BLE001 -- see comment
            # Not an expected failure, so it's a bug somewhere. Log it, but still
            # show the error card: a spinner that never stops is worse.
            Logger.exception("Dashboard: unexpected error while generating a roadmap")
            Clock.schedule_once(partial(self._on_generation_failed, f"Unexpected error: {error}", generation_id))
        else:
            Clock.schedule_once(partial(self._on_generation_done, roadmap, generation_id))

    def _on_generation_done(self, roadmap, generation_id, dt):
        # Back on the MAIN thread (Clock called us), so touching widgets is safe.
        # `dt` is the delay Clock passes to every callback; unused here.
        if generation_id != self._generation_id:
            return  # stale: the user logged out (or restarted) while this was running
        self._generating = False
        self.render_roadmap(roadmap)

    def _on_generation_failed(self, message, generation_id, dt):
        if generation_id != self._generation_id:
            return
        self._generating = False
        self.show_error(message)

    # ---- what's on screen -------------------------------------------------

    def render_roadmap(self, roadmap):
        view = DashboardRoadmapView()
        view.show(roadmap)
        self._set_body(view)

    def show_loading(self):
        view = DashboardLoadingView()
        self._set_body(view)
        view.start()

    def show_error(self, message=""):
        self._set_body(DashboardErrorView(screen=self, detail=message))

    def _set_body(self, view):
        self._stop_body_animations()
        body = self.ids.body
        body.clear_widgets()
        body.add_widget(view)
        self._body_view = view

    def _stop_body_animations(self):
        if isinstance(self._body_view, DashboardLoadingView):
            self._body_view.stop()

    # ---- buttons ----------------------------------------------------------

    def edit_intake(self):
        # Same identity handoff the Phase 1 screens use (see current_user_id).
        self.manager.get_screen("intake").set_current_user(self.current_user_id)
        self.manager.current = "intake"

    def go_to_settings(self):
        if self.has_settings:
            self.manager.current = "settings"

    def log_out_user(self):
        log_out()  # controller clears its session state
        self._generation_id += 1  # any generation still running is now stale
        self._generating = False
        self.current_user_id = None
        # The intake screen holds the user id too (Phase 1 design); clear it so
        # the next person can't submit an intake as the previous user.
        if self.manager.has_screen("intake"):
            self.manager.get_screen("intake").set_current_user(None)
        self._stop_body_animations()
        self.ids.body.clear_widgets()  # don't flash this roadmap at the next user
        self._body_view = None
        self.manager.current = "landing"
