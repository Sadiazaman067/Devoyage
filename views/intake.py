"""
Intake screen (Module Contract screen id: "intake"), feature F2.

This view builds intake_data as a plain dict shaped EXACTLY like the
Data Models section's `intakes` table, then hands it to Sugam's
controller:

    save_intake(user_id, intake_data) -> intake_id

Pydantic validation happens inside that controller call, not here --
this view's job is only to translate Kivy widget state into the
agreed shape. It never touches SQLite and never imports services/ai.py
(that call only happens from controllers/roadmap.py, in Phase 2).

Kivy note: the wireframe used pill-style buttons for single/multi
select. Kivy's native equivalent is Spinner (single-select) and
CheckBox rows (multi-select) -- the Kivy Learning Ladder doc flags
this exact substitution ("not a TextInput... prefer a Spinner or a
row of CheckBox widgets"), so that's what intake.kv uses. Swapping in
custom pill widgets later is a KV-only change; this file doesn't care.
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
import os

from controllers.intake import save_intake
from pydantic import ValidationError

Builder.load_file(os.path.join(os.path.dirname(__file__), "intake.kv"))

# Display text (what the Spinner shows) -> the exact enum string the
# spec's Data Models section requires. Keeping these maps here, next
# to the widgets that use them, means renaming a display label never
# risks touching the wire format Sadia/Arnav/Sugam depend on.

YEAR_MAP = {"Freshman": "freshman", "Sophomore": "sophomore", "Junior": "junior", "Senior": "senior"}

MAJOR_STATUS_MAP = {
    "Declared CS": "declared",
    "Intending, not declared": "intending",
    "Deciding between majors": "deciding",
}

PIPELINE_MAP = {"Yes": "yes", "No": "no", "Not sure": "unsure"}

PROJECT_COUNT_MAP = {"0": "0", "1": "1", "2-3": "2_3", "4+": "4_plus"}

BIGGEST_PROJECT_MAP = {
    "Solo": "solo",
    "Team": "team",
    "Tutorial": "tutorial",
    "Mostly AI-generated": "ai_generated",
    "N/A - no projects": "none",
}

DEPLOYED_MAP = {"Yes": "yes", "No": "no"}

HOURS_MAP = {"Under 5": "under_5", "5-10": "5_10", "10-15": "10_15", "15+": "15_plus"}

CREDITS_MAP = {"12-15": "12_15", "16-18": "16_18", "19+": "19_plus"}

GOAL_MAP = {
    "Get first internship": "internship",
    "Build first real project": "first_project",
    "Figure out if CS is for me": "explore_cs",
    "Strengthen fundamentals": "fundamentals",
}

# "Not used" is deliberately left out of this map: a language left on
# "Not used" is skipped entirely rather than sent with a null level.
SKILL_LEVEL_MAP = {
    "Class only": "class_only",
    "Small, on my own": "small_solo",
    "Multi-file project": "multi_file",
}

LANGUAGES = ["python", "cpp", "java", "js", "other"]

COURSEWORK_CHECKBOXES = {
    "cw_intro": "intro",
    "cw_oop": "oop",
    "cw_dsa": "dsa",
    "cw_none": "none",
}

CARRYING_CHECKBOXES = {
    "ac_online": "online_course",
    "ac_leetcode": "leetcode",
    "ac_hack": "hackathons",
    "ac_club": "club_leadership",
    "ac_research": "research",
    "ac_cert": "certifications",
    "ac_none": "none",
}


class IntakeScreen(Screen):
    current_user_id = None

    def set_current_user(self, user_id):
        self.current_user_id = user_id

    def _checked_values(self, id_to_value):
        return [value for widget_id, value in id_to_value.items() if self.ids[widget_id].active]

    def _collect_skills(self):
        skills = []
        for lang in LANGUAGES:
            chosen_text = self.ids[f"skill_{lang}"].text
            level = SKILL_LEVEL_MAP.get(chosen_text)
            if level is not None:
                skills.append({"language": lang, "level": level})
        return skills

    def _build_intake_data(self):
        return {
            "year": YEAR_MAP[self.ids.year_spinner.text],
            "major_status": MAJOR_STATUS_MAP[self.ids.major_status_spinner.text],
            "has_pipeline": PIPELINE_MAP[self.ids.pipeline_spinner.text],
            "coursework": self._checked_values(COURSEWORK_CHECKBOXES),
            "skills": self._collect_skills(),
            "project_count": PROJECT_COUNT_MAP[self.ids.project_count_spinner.text],
            "biggest_project_type": BIGGEST_PROJECT_MAP[self.ids.biggest_project_spinner.text],
            "deployed": DEPLOYED_MAP[self.ids.deployed_spinner.text],
            "carrying": self._checked_values(CARRYING_CHECKBOXES),
            "weekly_hours": HOURS_MAP[self.ids.hours_spinner.text],
            "credit_load": CREDITS_MAP[self.ids.credits_spinner.text],
            "goal": GOAL_MAP[self.ids.goal_spinner.text],
            "free_text": self.ids.free_text_input.text.strip() or None,
        }

    def submit(self):
        if self.current_user_id is None:
            self.ids.error_label.text = "No signed-in user -- something upstream didn't set one."
            return

        intake_data = self._build_intake_data()

        try:
            save_intake(self.current_user_id, intake_data)
        except ValidationError as e:
            self.ids.error_label.text = "Please check your answers: " + str(e)
            return

        self.ids.error_label.text = ""
        self.manager.current = "dashboard"
