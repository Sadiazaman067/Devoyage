from typing import Literal, Optional
from pydantic import BaseModel, Field
from models.intakes import save_intake as db_save_intake, get_latest_intake
from models import db

class SkillData(BaseModel):
    language: Literal["python", "cpp", "java", "js", "other"]
    level: Literal["class_only", "small_solo", "multi_file"]


class IntakeData(BaseModel):
    year: Literal["freshman", "sophomore", "junior", "senior"]
    major_status: Literal["declared", "intending", "deciding"]
    has_pipeline: Literal["yes", "no", "unsure"]

    coursework: list[Literal["intro", "oop", "dsa", "none"]]

    skills: list[SkillData]

    project_count: Literal["0", "1", "2_3", "4_plus"]
    biggest_project_type: Literal[
        "solo", "team", "tutorial", "ai_generated", "none"
    ]

    deployed: Literal["yes", "no"]

    carrying: list[
        Literal[
            "online_course",
            "leetcode",
            "hackathons",
            "club_leadership",
            "research",
            "certifications",
            "none",
        ]
    ]

    weekly_hours: Literal["under_5", "5_10", "10_15", "15_plus"]
    credit_load: Literal["12_15", "16_18", "19_plus"]
    goal: Literal[
        "internship",
        "first_project",
        "explore_cs",
        "fundamentals",
    ]

    free_text: Optional[str] = Field(default=None, max_length=500)

#function that returns a bool that says if the user has completed intake or not. if not, prompt again, if yes, not necessary.
#checks via sadia's model since the db already stores table of user's intakes with completion dates. 
#so if table==none for user id, false
def has_completed_intake(user_id):
    conn=db.get_connection()
    try:
        intake=get_latest_intake(conn, user_id)
        return intake is not None #return true if intake is not None, else false
    finally:
        conn.close()

#function called by view so that the view will save the users latest intake in db, link between View->Model through controller
#will validate the intake data to JSON to be stored in db
def save_intake(user_id, intake_data):
    conn=db.get_connection()
    try:
        validated = IntakeData.model_validate(intake_data) 

        return db_save_intake(conn, user_id, validated.model_dump())
    finally:
        conn.close()