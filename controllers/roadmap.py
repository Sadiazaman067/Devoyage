from exceptions import AuthError, ValidationError

from models import db, intakes, roadmaps
from services.ai import generate_roadmap_from_intake

from controllers.auth import get_current_user_id

#tuple containing all the fields that a student answers in the intake
#required to filter out the additional fields like id, user_id etc so that sugam only feeds these to the AI
INTAKE_AI_FIELDS= (
    "year",
    "major_status",
    "has_pipeline",
    "coursework",
    "skills",
    "project_count",
    "biggest_project_type",
    "deployed",
    "carrying",
    "weekly_hours",
    "credit_load",
    "goal",
    "free_text",
)

#generate roadmap, save to db, and return the roadmap from db
def generate_roadmap(user_id: int)-> dict:
    conn= db.get_connection()
    try:
        latest_intake=intakes.get_latest_intake(conn, user_id) #get dict of intake field: data
    finally:
        conn.close()

    if latest_intake is None:
        raise ValidationError("Complete the intake first.")

    intake_id=latest_intake["id"]

    #create a new filtered field dict to feed to sugam's ai, 
    intake_data={}
    for field in INTAKE_AI_FIELDS:
        intake_data[field]= latest_intake[field]

    #feed to sugam's ai and get generated data dict
    generated= generate_roadmap_from_intake(intake_data)

    #save generated data to db
    conn=db.get_connection()

    try:
        roadmaps.create_roadmap(conn, user_id, intake_id, generated["steps"], generated["not_now"])

        return roadmaps.get_current_roadmap(conn, user_id)
    
    finally:
        conn.close()

#function for view to fetch current roadmap from db if needed
def get_current_roadmap(user_id: int)-> dict:
    conn=db.get_connection()
    try:
        current_roadmap=roadmaps.get_current_roadmap(conn, user_id)
        return current_roadmap

    finally:
        conn.close()

def set_step_status(step_id, status: str):
    if status not in ("pending", "done"):
        raise ValidationError("Status must be either 'pending' or 'done'.")

    user_id=get_current_user_id()

    if user_id is None:
        raise AuthError("You must be logged in.")

    conn=db.get_connection()

    try:
        updated= roadmaps.set_step_status(conn, step_id, status, user_id)

        if not updated:
            raise ValidationError("Roadmap step wasn't found.")

    finally:
        conn.close()