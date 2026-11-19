"""
Stand-ins for controllers/content.py (Arnav, Tier 2 spec 11/17):

    list_career_paths() -> list of career paths
    list_resources(category=None) -> list of resources

Same names, arguments, and dict fields as the spec. The content is Sugam's
real seed content (models/seed_data.py, #21); this stub just reads it
straight from that file instead of from the database, until Arnav's
controller and Sadia's tables are in.
"""
from exceptions import ValidationError
from models.seed_data import CAREER_PATHS, RESOURCES

CATEGORIES = ("learning", "practice", "tools", "communities", "career")


def list_career_paths():
    paths = sorted(CAREER_PATHS, key=lambda p: p["position"])
    return [
        dict(path, id=i, skills=list(path["skills"]), first_steps=list(path["first_steps"]))
        for i, path in enumerate(paths, start=1)
    ]


def list_resources(category=None):
    if category is not None and category not in CATEGORIES:
        raise ValidationError("Unknown resource category.")
    resources = sorted(RESOURCES, key=lambda r: r["position"])
    return [
        dict(r, id=i) for i, r in enumerate(resources, start=1)
        if category is None or r["category"] == category
    ]
