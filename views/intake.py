"""
Intake screen (Module Contract screen id: "intake"), feature F2.

Milestone 3 design (11/16): six steps with Back and Next instead of one long
form. Same output as before: on the last step the screen builds intake_data,
a plain dict shaped exactly like the controller's input (the IntakeData
fields and values in the Module Contract), and calls

    save_intake(user_id, intake_data) -> intake_id

How this file is organised
--------------------------
- The *_MAP dicts turn what the student sees ("2-3") into the exact enum
  string the spec requires ("2_3"). Renaming a label never changes the
  wire format Sadia, Arnav and Sugam depend on.
- STEPS describes the six steps: title, hint, "Why we ask" text, and the
  questions on each. The screen builds the widgets from it, so changing a
  question is an edit to STEPS, not to the .kv file.
- Answers live in self.answers across all six steps. Each step is checked
  when the student clicks Next; Pydantic validation still happens inside
  the controller call, not here.

The view never touches SQLite and never imports services/ai.py.
"""
import os

from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput

from views import components  # noqa: F401  (Card, OptionButton, ErrorBox used below and in intake.kv)
from views.components import Card, OptionButton
from views.controllers_api import save_intake, ValidationError  # swap point: see views/controllers_api.py
from views.icons import icon
from views.theme import C

Builder.load_file(os.path.join(os.path.dirname(__file__), "intake.kv"))

# ---- Display text -> enum string (Data Models section of the spec) ----------

YEAR_MAP = {"Freshman": "freshman", "Sophomore": "sophomore", "Junior": "junior", "Senior": "senior"}

MAJOR_STATUS_MAP = {
    "Declared CS": "declared",
    "Intending, not declared": "intending",
    "Deciding between majors": "deciding",
}

PIPELINE_MAP = {"Yes": "yes", "No": "no", "Not sure": "unsure"}

COURSEWORK_MAP = {
    "Intro programming": "intro",
    "Second course / OOP": "oop",
    "Data structures": "dsa",
    "None yet": "none",
}

SKILL_LEVEL_MAP = {
    "Class only": "class_only",
    "Small solo projects": "small_solo",
    "Multi-file projects": "multi_file",
}

# Language enum -> how it's shown.
LANGUAGES = {"python": "Python", "cpp": "C++", "java": "Java", "js": "JavaScript", "other": "Other"}

PROJECT_COUNT_MAP = {"0": "0", "1": "1", "2-3": "2_3", "4+": "4_plus"}

BIGGEST_PROJECT_MAP = {
    "Solo": "solo",
    "Team": "team",
    "Tutorial": "tutorial",
    "Mostly AI-generated": "ai_generated",
    "No projects yet": "none",
}

DEPLOYED_MAP = {"Yes": "yes", "No": "no"}

CARRYING_MAP = {
    "Online course (CS50, Coursera)": "online_course",
    "LeetCode / NeetCode": "leetcode",
    "Hackathons": "hackathons",
    "Club leadership": "club_leadership",
    "Research, or looking for it": "research",
    "Certifications": "certifications",
    "Nothing yet": "none",
}

HOURS_MAP = {"Under 5": "under_5", "5-10": "5_10", "10-15": "10_15", "15+": "15_plus"}

CREDITS_MAP = {"12-15": "12_15", "16-18": "16_18", "19+": "19_plus"}

GOAL_MAP = {
    "Get my first internship": "internship",
    "Build my first real project": "first_project",
    "Figure out if CS is for me": "explore_cs",
    "Strengthen my fundamentals": "fundamentals",
}

# ---- The six steps ----------------------------------------------------------
# Question kinds:
#   ("single", field, title, MAP, columns)   pick exactly one
#   ("multi",  field, title, MAP, columns)   pick one or more; "none"-valued
#                                            option can't be combined
#   ("skills",)                              one row per language
#   ("text",   field, title)                 optional free text

STEPS = [
    {
        "label": "Year & major",
        "question": "Where are you right now?",
        "hint": "Three quick picks about your year and your school.",
        "why": "Your year and major status decide how much time the roadmap assumes you have before internships.",
        "questions": [
            ("single", "year", "Year", YEAR_MAP, 4),
            ("single", "major_status", "Major status", MAJOR_STATUS_MAP, 3),
            ("single", "has_pipeline", "Does your school have a big tech recruiting pipeline?", PIPELINE_MAP, 3),
        ],
    },
    {
        "label": "Classes",
        "question": "Which CS classes have you taken?",
        "hint": "Check everything you've finished or are taking now.",
        "why": "Classes you've taken tell the roadmap what you can build on, so it doesn't send you back to things you already know.",
        "questions": [("multi", "coursework", "Classes", COURSEWORK_MAP, 2)],
    },
    {
        "label": "Languages",
        "question": "How comfortable are you with each language?",
        "hint": "Pick one level for each language you've used. Skip the ones you haven't.",
        "why": "Your roadmap uses your comfort level to decide whether to start with fundamentals or jump into projects.",
        "questions": [("skills",)],
    },
    {
        "label": "Projects",
        "question": "What have you built so far?",
        "hint": "Count anything you wrote outside of class assignments.",
        "why": "Projects are what recruiters look at first. This tells the roadmap whether your next step is starting one or finishing one.",
        "questions": [
            ("single", "project_count", "How many projects?", PROJECT_COUNT_MAP, 4),
            ("single", "biggest_project_type", "Your biggest project was...", BIGGEST_PROJECT_MAP, 3),
            ("single", "deployed", "Is any of it live or deployed?", DEPLOYED_MAP, 2),
        ],
    },
    {
        "label": "What you're doing",
        "question": "What are you already doing?",
        "hint": "Check everything that takes up your time this semester.",
        "why": "This builds your Not Now list. If you're already doing a lot, the roadmap tells you what to skip instead of adding more.",
        "questions": [("multi", "carrying", "Already doing", CARRYING_MAP, 2)],
    },
    {
        "label": "Hours & goal",
        "question": "How much time do you have, and what's the goal?",
        "hint": "Be honest about your hours. A smaller plan you finish beats a big one you don't.",
        "why": "Your weekly hours decide how many steps show up in Weekly Focus, and your goal decides what the roadmap aims for.",
        "questions": [
            ("single", "weekly_hours", "Hours per week you can actually spend", HOURS_MAP, 4),
            ("single", "credit_load", "Credit load this semester", CREDITS_MAP, 3),
            ("single", "goal", "Goal for the next 6 to 12 months", GOAL_MAP, 2),
            ("text", "free_text", "Anything else about your situation? (optional)"),
        ],
    },
]

STEP_COUNT = len(STEPS)


class StepDot(BoxLayout):
    """One circle in the step indicator. state_name: 'done', 'current' or 'todo'."""
    number = NumericProperty(1)
    label = StringProperty("")
    state_name = StringProperty("todo")
    check_char = StringProperty(icon("check"))


class IntakeScreen(Screen):
    current_user_id = None

    step_index = NumericProperty(0)
    eyebrow = StringProperty("")
    question = StringProperty("")
    hint = StringProperty("")
    why_text = StringProperty("")
    so_far_text = StringProperty("")
    clock_char = StringProperty(icon("clock"))

    def __init__(self, **kwargs):
        self._reset_answers()
        self._option_widgets = {}
        self._dots = []
        self._lines = []
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self._build_steps_bar()
        self._show_step()

    # ---- identity (same handoff the other screens use) ----------------------

    def set_current_user(self, user_id):
        if user_id != self.current_user_id:
            # A different person: never show the previous person's answers.
            self._reset_answers()
            self.step_index = 0
            if self._dots:
                self._show_step()
        self.current_user_id = user_id

    def _reset_answers(self):
        self.answers = {"coursework": [], "carrying": [], "skills": {}, "free_text": ""}

    # ---- navigation ---------------------------------------------------------

    def go_next(self):
        problem = self._check_step(self.step_index)
        if problem:
            self.ids.error_box.message = problem
            return
        if self.step_index == STEP_COUNT - 1:
            self.submit()
            return
        self.step_index += 1
        self._show_step()

    def go_back(self):
        if self.step_index > 0:
            self.step_index -= 1
            self._show_step()

    def _check_step(self, index):
        for spec in STEPS[index]["questions"]:
            kind = spec[0]
            if kind == "single" and spec[1] not in self.answers:
                return f"Pick an answer for \"{spec[2]}\"."
            if kind == "multi" and not self.answers[spec[1]]:
                return "Pick at least one. If none apply, pick the last option."
        return ""

    # ---- building a step ----------------------------------------------------

    def _build_steps_bar(self):
        from kivy.factory import Factory
        bar = self.ids.steps_bar
        bar.clear_widgets()
        self._dots, self._lines = [], []
        for number, step in enumerate(STEPS, start=1):
            if number > 1:
                line = Factory.StepLine()
                bar.add_widget(line)
                self._lines.append(line)
            dot = StepDot(number=number, label=step["label"])
            bar.add_widget(dot)
            self._dots.append(dot)

    def _show_step(self):
        step = STEPS[self.step_index]
        self.eyebrow = f"STEP {self.step_index + 1} OF {STEP_COUNT}"
        self.question = step["question"]
        self.hint = step["hint"]
        self.why_text = step["why"]
        self.ids.error_box.message = ""

        for i, dot in enumerate(self._dots):
            dot.state_name = "done" if i < self.step_index else ("current" if i == self.step_index else "todo")
        for i, line in enumerate(self._lines):
            line.done = i < self.step_index

        body = self.ids.step_body
        body.clear_widgets()
        self._option_widgets = {}
        for spec in step["questions"]:
            kind = spec[0]
            if kind in ("single", "multi"):
                self._add_choice_question(body, *spec)
            elif kind == "skills":
                self._add_skills(body)
            elif kind == "text":
                self._add_text(body, spec[1], spec[2])
        self._update_so_far()

    def _add_title(self, body, text):
        title = Label(
            text=text, font_name="InterSemiBold", font_size="16sp", color=C.ink,
            size_hint_y=None, halign="left", valign="bottom",
        )
        title.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        title.bind(texture_size=lambda inst, ts: setattr(inst, "height", ts[1] + dp(6)))
        body.add_widget(title)

    def _add_choice_question(self, body, kind, field, title, mapping, columns):
        if len(STEPS[self.step_index]["questions"]) > 1:
            self._add_title(body, title)
        grid = GridLayout(
            cols=columns, spacing=dp(12), size_hint_y=None,
            row_force_default=True, row_default_height=dp(48),
        )
        grid.bind(minimum_height=grid.setter("height"))
        for display in mapping:
            button = OptionButton(text=display, multi=(kind == "multi"))
            button.bind(on_release=lambda btn, k=kind, f=field, d=display: self._pick(k, f, d))
            grid.add_widget(button)
            self._option_widgets[(field, display)] = button
        body.add_widget(grid)
        self._refresh_options(field, mapping)

    def _add_skills(self, body):
        for lang, shown in LANGUAGES.items():
            row = Card(size_hint_y=None, height=dp(68), padding=[dp(18), dp(10)], spacing=dp(12), radius=12)
            name = Label(
                text=shown, font_name="InterSemiBold", font_size="16sp", color=C.ink,
                size_hint_x=None, width=dp(110), halign="left", valign="middle",
            )
            name.bind(size=lambda inst, size: setattr(inst, "text_size", size))
            row.add_widget(name)
            for display in SKILL_LEVEL_MAP:
                button = OptionButton(text=display)
                button.bind(on_release=lambda btn, l=lang, d=display: self._pick_skill(l, d))
                row.add_widget(button)
                self._option_widgets[("skill_" + lang, display)] = button
            body.add_widget(row)
        self._refresh_skills()

    def _add_text(self, body, field, title):
        self._add_title(body, title)
        box = Card(size_hint_y=None, height=dp(96), padding=[dp(14), dp(8)], radius=10)
        text_input = TextInput(
            text=self.answers.get(field, ""),
            hint_text="For example: I work 20 hours a week, or I'm switching from biology.",
            font_size="15sp", foreground_color=C.ink, hint_text_color=C.text_faint,
            cursor_color=C.blue, background_normal="", background_active="",
            background_color=(0, 0, 0, 0),
        )
        text_input.bind(text=lambda inst, value: self.answers.__setitem__(field, value))
        box.add_widget(text_input)
        body.add_widget(box)

    # ---- answering ------------------------------------------------------------

    def _pick(self, kind, field, display):
        self.ids.error_box.message = ""
        if kind == "single":
            self.answers[field] = display
        else:
            chosen = self.answers[field]
            mapping = COURSEWORK_MAP if field == "coursework" else CARRYING_MAP
            is_none = mapping[display] == "none"
            if display in chosen:
                chosen.remove(display)
            elif is_none:
                chosen[:] = [display]  # "None yet" clears everything else
            else:
                chosen[:] = [d for d in chosen if mapping[d] != "none"] + [display]
        mapping = self._mapping_for(field)
        self._refresh_options(field, mapping)
        self._update_so_far()

    def _pick_skill(self, lang, display):
        skills = self.answers["skills"]
        if skills.get(lang) == display:
            del skills[lang]  # clicking the chosen level again clears it
        else:
            skills[lang] = display
        self._refresh_skills()
        self._update_so_far()

    def _mapping_for(self, field):
        for step in STEPS:
            for spec in step["questions"]:
                if spec[0] in ("single", "multi") and spec[1] == field:
                    return spec[3]
        return {}

    def _refresh_options(self, field, mapping):
        answer = self.answers.get(field)
        for display in mapping:
            button = self._option_widgets.get((field, display))
            if button is not None:
                button.selected = (display in answer) if isinstance(answer, list) else (display == answer)

    def _refresh_skills(self):
        for lang in LANGUAGES:
            for display in SKILL_LEVEL_MAP:
                button = self._option_widgets.get(("skill_" + lang, display))
                if button is not None:
                    button.selected = self.answers["skills"].get(lang) == display

    def _update_so_far(self):
        a = self.answers
        lines = []
        first = " · ".join(a[k] for k in ("year", "major_status") if k in a)
        if first:
            lines.append(first)
        if a["coursework"]:
            lines.append(", ".join(a["coursework"]))
        if a["skills"]:
            lines.append(", ".join(LANGUAGES[lang] for lang in LANGUAGES if lang in a["skills"]))
        if "project_count" in a:
            lines.append(f"{a['project_count']} project(s)")
        if a["carrying"]:
            lines.append(", ".join(a["carrying"]))
        if "weekly_hours" in a:
            lines.append(f"{a['weekly_hours']} hours a week")
        self.so_far_text = "\n".join(lines)

    # ---- submitting ---------------------------------------------------------

    def _build_intake_data(self):
        a = self.answers
        return {
            "year": YEAR_MAP[a["year"]],
            "major_status": MAJOR_STATUS_MAP[a["major_status"]],
            "has_pipeline": PIPELINE_MAP[a["has_pipeline"]],
            "coursework": [COURSEWORK_MAP[d] for d in a["coursework"]],
            "skills": [
                {"language": lang, "level": SKILL_LEVEL_MAP[a["skills"][lang]]}
                for lang in LANGUAGES if lang in a["skills"]
            ],
            "project_count": PROJECT_COUNT_MAP[a["project_count"]],
            "biggest_project_type": BIGGEST_PROJECT_MAP[a["biggest_project_type"]],
            "deployed": DEPLOYED_MAP[a["deployed"]],
            "carrying": [CARRYING_MAP[d] for d in a["carrying"]],
            "weekly_hours": HOURS_MAP[a["weekly_hours"]],
            "credit_load": CREDITS_MAP[a["credit_load"]],
            "goal": GOAL_MAP[a["goal"]],
            "free_text": a.get("free_text", "").strip() or None,
        }

    def submit(self):
        if self.current_user_id is None:
            self.ids.error_box.message = "No one is signed in. Log in again."
            return

        try:
            save_intake(self.current_user_id, self._build_intake_data())
        except ValidationError as e:
            self.ids.error_box.message = "Please check your answers: " + str(e)
            return

        user_id = self.current_user_id
        self._reset_answers()
        self.step_index = 0
        self._show_step()
        self.manager.get_screen("dashboard").current_user_id = user_id
        self.manager.current = "dashboard"
