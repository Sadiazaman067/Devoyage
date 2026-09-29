from typing import Literal, Optional
from pydantic import BaseModel, Field


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

def save_intake(conn, user_id, intake_data):
    validated = IntakeData.model_validate(intake_data)

    from intakes import save_intake as db_save_intake

    return db_save_intake(
        conn,
        user_id,
        validated.model_dump()
    )