from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError
from exceptions import ValidationError
from models import db, portfolio, roadmaps

#valid portfolio entry types from spec
validEntryTypes=("project", "course", "hackathon", "application", "other")


#pydantic model to check incoming portfolio entry shape
class PortfolioEntryData(BaseModel):
    entry_type: Literal["project", "course", "hackathon", "application", "other"]
    title: str
    start_date: str
    link: Optional[str]=None
    note: Optional[str]=Field(default=None, max_length=500)
    step_id: Optional[int]=None


#validate and clean entry_data dict before saving to db
def validateEntryData(entryData:dict)->dict:
    if not isinstance(entryData, dict):
        raise ValidationError("Invalid portfolio entry data.")

    #reject bools before pydantic converts True/False to 1/0
    if isinstance(entryData.get("step_id"), bool):
        raise ValidationError("Invalid roadmap step.")

    try:
        validated=PortfolioEntryData.model_validate(entryData)
    except PydanticValidationError as e:
        raise ValidationError("Invalid portfolio entry data.") from e

    #strip title and check length
    cleanTitle=validated.title.strip()
    if not cleanTitle:
        raise ValidationError("Title is required.")
    if len(cleanTitle)>120:
        raise ValidationError("Title must be 120 characters or fewer.")

    #verify start_date is a real YYYY-MM-DD date
    cleanDate=validated.start_date.strip()
    try:
        date.fromisoformat(cleanDate)
    except ValueError as e:
        raise ValidationError("Start date must be a valid YYYY-MM-DD date.") from e

    #optional link must start with http:// or https://
    cleanLink=validated.link.strip() if validated.link else None
    if cleanLink and not cleanLink.startswith(("http://", "https://")):
        raise ValidationError("Link must start with http:// or https://.")

    #optional note max 500 chars
    cleanNote=validated.note.strip() if validated.note else None
    if cleanNote and len(cleanNote)>500:
        raise ValidationError("Note must be 500 characters or fewer.")

    return {
        "entry_type": validated.entry_type,
        "title": cleanTitle,
        "start_date": cleanDate,
        "link": cleanLink,
        "note": cleanNote,
        "step_id": validated.step_id,
    }


#check that step_id belongs to the user's current roadmap
def checkStepInRoadmap(conn, userId:int, stepId:Optional[int])->None:
    if stepId is None:
        return

    currentRoadmap=roadmaps.get_current_roadmap(conn, userId)
    if currentRoadmap is None:
        raise ValidationError("Selected roadmap step is not in your current roadmap.")

    validStepIds={step["id"] for step in currentRoadmap.get("steps", [])}
    if stepId not in validStepIds:
        raise ValidationError("Selected roadmap step is not in your current roadmap.")


#add a new portfolio entry for the user
def add_portfolio_entry(user_id:int, entry_data:dict)->int:
    cleanedData=validateEntryData(entry_data)

    conn=db.get_connection()#get connection from sqlite
    try:
        checkStepInRoadmap(conn, user_id, cleanedData["step_id"])
        return portfolio.add_entry(conn, user_id, cleanedData)
    finally:#close connection even if error is raised
        conn.close()


#list portfolio entries for user, filter by entry_type if given
def list_portfolio_entries(user_id:int, entry_type:Optional[str]=None)->list:
    if entry_type is not None and entry_type not in validEntryTypes:
        raise ValidationError("Unknown entry type.")

    conn=db.get_connection()
    try:
        return portfolio.list_entries(conn, user_id, entry_type=entry_type)
    finally:
        conn.close()


#update an existing portfolio entry owned by the user
def update_portfolio_entry(user_id:int, entry_id:int, entry_data:dict)->None:
    cleanedData=validateEntryData(entry_data)

    conn=db.get_connection()
    try:
        checkStepInRoadmap(conn, user_id, cleanedData["step_id"])
        updated=portfolio.update_entry(conn, user_id, entry_id, cleanedData)

        if not updated:
            raise ValidationError("Entry not found.")
    finally:
        conn.close()


#delete a portfolio entry owned by the user
def delete_portfolio_entry(user_id:int, entry_id:int)->None:
    conn=db.get_connection()
    try:
        deleted=portfolio.delete_entry(conn, user_id, entry_id)

        if not deleted:
            raise ValidationError("Entry not found.")
    finally:
        conn.close()