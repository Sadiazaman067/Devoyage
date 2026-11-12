import sqlite3

import config

from exceptions import AuthError, ValidationError
from models import db, users, intakes, roadmaps

from controllers.auth import hashPassword, verifyPassword
from controllers.roadmap import generate_roadmap


# valid weekly hour values already used by the intake model
VALID_WEEKLY_HOURS = (
    "under_5",
    "5_10",
    "10_15",
    "15_plus",
)


# get the settings that need to be displayed on the Settings page
def get_settings(user_id: int):

    # theme is stored in config.ini
    theme = config.get_user_theme(user_id)

    # weekly hours are stored in the user's latest intake
    conn = db.get_connection()

    try:
        latest_intake = intakes.get_latest_intake(
            conn,
            user_id,
        )

    finally:
        conn.close()

    if latest_intake is None:
        raise ValidationError("Complete the intake first.")

    settings_data = {
        "theme": theme,
        "weekly_hours": latest_intake["weekly_hours"],
    }

    return settings_data


# update the user's light/dark theme
def update_theme(user_id: int, theme: str):

    try:
        config.set_user_theme(
            user_id,
            theme,
        )

    except ValueError as error:
        raise ValidationError(str(error)) from error


# update weekly hours on the user's latest intake
def update_weekly_hours(
    user_id: int,
    weekly_hours: str,
):

    if weekly_hours not in VALID_WEEKLY_HOURS:
        raise ValidationError(
            "Invalid weekly hours."
        )

    conn = db.get_connection()

    try:
        updated = intakes.update_latest_weekly_hours(
            conn,
            user_id,
            weekly_hours,
        )

        if not updated:
            raise ValidationError(
                "Complete the intake first."
            )

    finally:
        conn.close()


# change the email for the user's account
def change_email(
    user_id: int,
    new_email: str,
):

    # same normalization used by sign_up()
    normalized_email = new_email.strip().lower()

    if not normalized_email or "@" not in normalized_email:
        raise ValidationError(
            "Valid email address required."
        )

    conn = db.get_connection()

    try:
        try:
            users.update_email(
                conn,
                user_id,
                normalized_email,
            )

        except sqlite3.IntegrityError as error:
            raise AuthError(
                f"User with email {normalized_email} already exists"
            ) from error

    finally:
        conn.close()


# change the user's password
def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
):

    if not current_password:
        raise ValidationError(
            "Current password required."
        )

    if not new_password or len(new_password) < 8:
        raise ValidationError(
            "Password must be at least 8 characters long."
        )

    conn = db.get_connection()

    try:
        user = users.get_user_by_id(
            conn,
            user_id,
        )

        if user is None:
            raise AuthError(
                "User not found."
            )

        # check that the current password is correct
        password_correct = verifyPassword(
            current_password,
            user["password_hash"],
        )

        if not password_correct:
            raise AuthError(
                "Current password is incorrect."
            )

        # hash the new password before saving it
        new_password_hash = hashPassword(
            new_password
        )

        users.update_password_hash(
            conn,
            user_id,
            new_password_hash,
        )

    finally:
        conn.close()


# regenerate the roadmap using the user's latest intake
def regenerate_roadmap(user_id: int):

    return generate_roadmap(user_id)


# clear all roadmap data while keeping intake data
def clear_roadmap_data(user_id: int):

    conn = db.get_connection()

    try:
        roadmaps.clear_roadmap_data(
            conn,
            user_id,
        )

    finally:
        conn.close()