from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, ValidationError as PydanticValidationError
from exceptions import ValidationError
from models import db, portfolio, roadmaps

validEntryTypes = ("project", "course", "hackathon", "application", "other")


class PortfolioEntryData(BaseModel):
    entry_type: Literal["project", "course", "hackathon", "application", "other"]
    title: str
    start_date: str
    link: Optional[str] = None
    note: Optional[str] = None
    step_id: Optional[int] = None


def validateEntryData(entryData: dict) -> dict:
    if not isinstance(entryData, dict):
        raise ValidationError("Invalid portfolio entry data.")

    if isinstance(entryData.get("step_id"), bool):
        raise ValidationError("Invalid roadmap step.")

    try:
        validated = PortfolioEntryData.model_validate(entryData)
    except PydanticValidationError as e:
        raise ValidationError("Invalid portfolio entry data.") from e

    cleanTitle = validated.title.strip()
    if not cleanTitle:
        raise ValidationError("Title is required.")
    if len(cleanTitle) > 120:
        raise ValidationError("Title must be 120 characters or fewer.")

    cleanDate = validated.start_date.strip()
    try:
        date.fromisoformat(cleanDate)
    except ValueError as e:
        raise ValidationError("Start date must be a valid YYYY-MM-DD date.") from e

    cleanLink = validated.link.strip() if validated.link else None
    if cleanLink and not cleanLink.startswith(("http://", "https://")):
        raise ValidationError("Link must start with http:// or https://.")

    cleanNote = validated.note.strip() if validated.note else None
    if cleanNote and len(cleanNote) > 500:
        raise ValidationError("Note must be 500 characters or fewer.")

    return {
        "entry_type": validated.entry_type,
        "title": cleanTitle,
        "start_date": cleanDate,
        "link": cleanLink,
        "note": cleanNote,
        "step_id": validated.step_id,
    }


def checkStepInRoadmap(conn, userId: int, stepId: Optional[int]) -> None:
    if stepId is None:
        return

    currentRoadmap = roadmaps.get_current_roadmap(conn, userId)
    if currentRoadmap is None:
        raise ValidationError("Selected roadmap step is not in your current roadmap.")

    validStepIds = {step["id"] for step in currentRoadmap.get("steps", [])}
    if stepId not in validStepIds:
        raise ValidationError("Selected roadmap step is not in your current roadmap.")


def add_portfolio_entry(user_id: int, entry_data: dict) -> int:
    cleanedData = validateEntryData(entry_data)

    conn = db.get_connection()
    try:
        checkStepInRoadmap(conn, user_id, cleanedData["step_id"])
        try:
            return portfolio.add_entry(conn, user_id, cleanedData)
        except ValueError as e:
            raise ValidationError(str(e)) from e
    finally:
        conn.close()


def list_portfolio_entries(user_id: int, entry_type: Optional[str] = None) -> list:
    if entry_type is not None and entry_type not in validEntryTypes:
        raise ValidationError("Unknown entry type.")

    conn = db.get_connection()
    try:
        return portfolio.list_entries(conn, user_id, entry_type=entry_type)
    finally:
        conn.close()


def update_portfolio_entry(user_id: int, entry_id: int, entry_data: dict) -> None:
    cleanedData = validateEntryData(entry_data)

    conn = db.get_connection()
    try:
        existingEntries = portfolio.list_entries(conn, user_id)
        existingEntry = next(
            (entry for entry in existingEntries if entry["id"] == entry_id),
            None,
        )

        if existingEntry is None:
            raise ValidationError("Entry not found.")

        if cleanedData["step_id"] != existingEntry["step_id"]:
            checkStepInRoadmap(conn, user_id, cleanedData["step_id"])

        try:
            updated = portfolio.update_entry(conn, user_id, entry_id, cleanedData)
        except ValueError as e:
            raise ValidationError(str(e)) from e

        if not updated:
            raise ValidationError("Entry not found.")
    finally:
        conn.close()


def delete_portfolio_entry(user_id: int, entry_id: int) -> None:
    conn = db.get_connection()
    try:
        deleted = portfolio.delete_entry(conn, user_id, entry_id)

        if not deleted:
            raise ValidationError("Entry not found.")
    finally:
        conn.close()