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
  If generation raises ValidationError (the real controller does this when
  the user has no intake yet), the user is sent to the intake screen.

Layout lives in dashboard.kv. This file holds the behaviour; pure data
logic (progress text, dates, layout breakpoint) is in dashboard_helpers.py.
"""
import os
import threading
from functools import partial

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

# ---- Controller calls: the ONE place this screen imports them ---------------
# These are the real controllers as of 11/11. To go back to the stubs, flip
# the import blocks in views/controllers_api.py -- nothing here changes.
from views.controllers_api import (
    AIServiceError,
    AuthError,
    ValidationError,
    generate_roadmap,
    get_current_roadmap,
    log_out,
    set_step_status,
)

from views import components  # noqa: F401  (Card, TickBox, Chip, Sidebar used in dashboard.kv)
from views.dashboard_helpers import (
    DONE,
    focus_step_indices,
    next_step_index,
    progress_fraction,
    progress_markup,
    progress_percent,
    short_time,
    subtitle_text,
)

Builder.load_file(os.path.join(os.path.dirname(__file__), "dashboard.kv"))


# ---------------------------------------------------------------------------
# Reusable pieces with their own properties (look: the matching <Dash...>
# rules in dashboard.kv).
#
# Why these are Python classes and not KV-only `<DashPill@Label>` dynamic
# classes: a property invented inside a dynamic class starts out as None,
# and Kivy builds the canvas BEFORE the rule assigns the real value. So
# `Color: rgba: self.fill` received None and crashed. Declaring the
# property here gives it a type and a safe default from the start; the
# KV rule then sets the real theme color.
# ---------------------------------------------------------------------------

class DashPill(Label):
    fill = ColorProperty((0, 0, 0, 0))
    shown = BooleanProperty(True)  # Kivy has no "hidden": False collapses it to zero width


class DashPillButton(Button):
    fill = ColorProperty((0, 0, 0, 0))
    outline = ColorProperty((0, 0, 0, 0))
    pad_x = NumericProperty(dp(48))  # total horizontal padding around the text


class DashCardFrame(BoxLayout):
    frame_fill = ColorProperty((0, 0, 0, 0))
    frame_line = ColorProperty((0, 0, 0, 0))
    frame_line_width = NumericProperty(1)


class DashSkeletonCard(DashCardFrame):
    title_share = NumericProperty(0.6)  # width of the fake title bar, as a fraction
    line_share = NumericProperty(0.85)


class DashProgressBar(Widget):
    value = NumericProperty(0)  # 0.0 to 1.0


class DashSkeletonBar(Widget):
    fill = ColorProperty((0, 0, 0, 0))


# ---------------------------------------------------------------------------
# Small widgets. Their look is in dashboard.kv (rules named after each class);
# Python only declares the properties the KV rules read.
# ---------------------------------------------------------------------------

class FocusItem(BoxLayout):
    """One step in the Weekly Focus panel."""

    step_id = ObjectProperty(None)
    title = StringProperty("")
    done = BooleanProperty(False)
    screen = ObjectProperty(None)


class StepRow(BoxLayout):
    """One roadmap step. The checkbox marks it done (set_step_status); the
    arrow shows or hides "Why this, why now"."""

    step_id = ObjectProperty(None)
    title = StringProperty("")
    description = StringProperty("")
    reasoning = StringProperty("")
    time_label = StringProperty("")
    done = BooleanProperty(False)
    expanded = BooleanProperty(False)
    screen = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        # ids are weak references: once the box is removed, Kivy would
        # throw it away. `.__self__` keeps a real reference so it can come back.
        self._why = self.ids.why.__self__
        self._show_why()

    def on_expanded(self, *args):
        self._show_why()

    def _show_why(self):
        why = getattr(self, "_why", None)
        if why is None:
            return
        wanted = self.expanded and not self.done and bool(self.reasoning)
        if wanted and why.parent is None:
            self.add_widget(why)
        elif not wanted and why.parent is not None:
            self.remove_widget(why)


class NotNowItem(BoxLayout):
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
    screen = ObjectProperty(None)
    focus_subtitle = StringProperty("")
    progress = NumericProperty(0)
    progress_markup = StringProperty("")
    percent_text = StringProperty("")

    def show(self, roadmap, expanded_ids):
        steps = roadmap.get("steps") or []
        not_now_items = roadmap.get("not_now_items") or []

        self.progress = progress_fraction(steps)
        self.progress_markup = progress_markup(steps)
        self.percent_text = progress_percent(steps)

        # ---- Weekly Focus (TEMPORARY: see focus_step_indices) ----
        focus_box = self.ids.focus_box
        focus_box.clear_widgets()
        focus = focus_step_indices(steps)
        self.focus_subtitle = (
            "Your next steps this week" if focus else "You've finished every step. Nice work."
        )
        for index in focus:
            step = steps[index]
            focus_box.add_widget(FocusItem(
                step_id=step.get("id"),
                title=step.get("title", ""),
                done=False,
                screen=self.screen,
            ))

        # ---- Roadmap steps, in the order the controller returned them ----
        steps_box = self.ids.steps_box
        steps_box.clear_widgets()
        for step in steps:
            steps_box.add_widget(StepRow(
                step_id=step.get("id"),
                title=step.get("title", ""),
                description=step.get("description", ""),
                reasoning=step.get("reasoning", ""),
                time_label=short_time(step.get("est_time")),
                done=step.get("status") == DONE,
                expanded=step.get("id") in expanded_ids,
                screen=self.screen,
            ))

        items_box = self.ids.notnow_items
        items_box.clear_widgets()
        for item in not_now_items:
            items_box.add_widget(NotNowItem(
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

    stacked = BooleanProperty(False)
    has_settings = BooleanProperty(False)
    subtitle = StringProperty("Your personalized roadmap for the semester")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._body_view = None
        self._generating = False
        # Bumped every time we start generating or log out. A background result
        # carrying an old number is stale and gets thrown away (see _on_generation_done).
        self._generation_id = 0
        # Which steps have "Why this, why now" open. Kept here so checking a
        # box (which redraws the list) doesn't close everything.
        self._expanded_ids = set()
        self._roadmap_id = None

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
        except ValidationError:
            # The real controller raises this when the user has no intake yet
            # ("Complete the intake first."). "Try again" can't fix that, so
            # send them to the intake instead of showing the error card.
            Clock.schedule_once(partial(self._on_needs_intake, generation_id))
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

    def _on_needs_intake(self, generation_id, dt):
        if generation_id != self._generation_id:
            return
        self._generating = False
        self.edit_intake()

    # ---- what's on screen -------------------------------------------------

    def render_roadmap(self, roadmap):
        steps = roadmap.get("steps") or []
        if roadmap.get("id") != self._roadmap_id:
            # A new roadmap: open the first unfinished step, like the mockup.
            self._roadmap_id = roadmap.get("id")
            up_next = next_step_index(steps)
            self._expanded_ids = {steps[up_next].get("id")} if up_next is not None else set()
        self.subtitle = subtitle_text(roadmap.get("generated_at"))

        if isinstance(self._body_view, DashboardRoadmapView):
            # Same view already on screen: refresh it in place so the
            # scroll position doesn't jump back to the top.
            self._body_view.show(roadmap, self._expanded_ids)
            return
        view = DashboardRoadmapView(screen=self)
        view.show(roadmap, self._expanded_ids)
        self._set_body(view)

    # ---- step actions (called from StepRow / FocusItem) -------------------

    def toggle_step(self, step_id, done):
        try:
            set_step_status(step_id, DONE if done else "pending")
        except (ValidationError, AuthError) as error:
            Logger.warning(f"Dashboard: couldn't update step {step_id}: {error}")
        # Re-read from the controller either way, so the screen always shows
        # what's actually saved.
        roadmap = get_current_roadmap(self.current_user_id)
        if roadmap is not None:
            self.render_roadmap(roadmap)

    def toggle_expanded(self, step_id):
        if step_id in self._expanded_ids:
            self._expanded_ids.discard(step_id)
        else:
            self._expanded_ids.add(step_id)
        if isinstance(self._body_view, DashboardRoadmapView):
            for row in self._body_view.ids.steps_box.children:
                if row.step_id == step_id:
                    row.expanded = step_id in self._expanded_ids

    def show_loading(self):
        self.subtitle = "Building your roadmap..."
        view = DashboardLoadingView()
        self._set_body(view)
        view.start()

    def show_error(self, message=""):
        self.subtitle = "Your roadmap couldn't be built"
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
        self._roadmap_id = None
        self._expanded_ids = set()
        self.manager.current = "landing"
