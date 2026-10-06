"""
Throwaway stand-in for controllers/roadmap.py (Module Contract):

    generate_roadmap(user_id) -> roadmap
    get_current_roadmap(user_id) -> roadmap with steps ordered by position + not_now_items

Same names and signatures as the contract, so views don't change when
Arnav's real controller replaces this (flip the block in
views/controllers_api.py).

ASSUMED RETURN SHAPE (not pinned down in the spec yet -- question for
Arnav). Built from the Data Models section and from what
models/roadmaps.get_current_roadmap already returns:

    {
      "id": 1, "user_id": 1, "intake_id": 1,
      "generated_at": "2026-10-06T12:00:00",
      "steps": [ {"id", "roadmap_id", "position", "title", "description",
                  "reasoning", "est_time", "status"}, ... ],   # by position
      "not_now_items": [ {"id", "roadmap_id", "title", "reasoning"}, ... ],
    }

get_current_roadmap returns None when the user has never generated one.

Flip SIMULATE_FAILURE to True to see the dashboard's error state.
"""
import copy
import time
from datetime import datetime

# Set to True to make generate_roadmap raise AIServiceError.
SIMULATE_FAILURE = False

# Pretend the AI call takes this long. Long enough to see the loading state.
GENERATION_DELAY_SECONDS = 3


class AIServiceError(Exception):
    """TEMPORARY. AIServiceError isn't defined anywhere in the codebase yet.

    The spec says controllers/services raise it, but where it lives
    (controllers/exceptions.py? services/ai.py?) is the team's call.
    It's defined here only so the dashboard has something to catch.
    """


# user_id -> latest roadmap. Mirrors the spec's regeneration policy
# ("current = latest"), in memory only, so it resets when the app quits.
_roadmaps_by_user = {}


def get_current_roadmap(user_id):
    roadmap = _roadmaps_by_user.get(user_id)
    # Return a copy so a view can never mutate the "stored" roadmap.
    return copy.deepcopy(roadmap) if roadmap is not None else None


def generate_roadmap(user_id):
    # Blocks like a real network call would. The dashboard runs this on a
    # background thread precisely because of this line.
    time.sleep(GENERATION_DELAY_SECONDS)

    if SIMULATE_FAILURE:
        raise AIServiceError(
            "The roadmap service didn't return a usable answer. (Simulated failure.)"
        )

    roadmap = _build_fake_roadmap(user_id)
    _roadmaps_by_user[user_id] = roadmap
    return copy.deepcopy(roadmap)


# ---------------------------------------------------------------------------
# Fake data: a sophomore, 5-10 hrs/week, 16-18 credits, goal = internship.
# Every reasoning names those intake specifics -- that's the product.
# ---------------------------------------------------------------------------

_FAKE_STEPS = [
    {
        "title": "Turn your team project into a portfolio piece",
        "description": "A README that names your part of the work, two screenshots, and the live link.",
        "reasoning": (
            "You're a sophomore aiming for an internship, and recruiters will look at your "
            "GitHub first. A clear README on a project you've already built is the cheapest "
            "win available on 5–10 hours a week."
        ),
        "est_time": "1 week",
        "status": "done",
    },
    {
        "title": "Register for Data Structures next term",
        "description": "Lock in the seat now; review arrays and linked lists over break.",
        "reasoning": (
            "Internship interviews lean on data structures. Taking DSA as part of your "
            "16–18 credits teaches it without spending your 5–10 free hours on it."
        ),
        "est_time": "This semester",
        "status": "done",
    },
    {
        "title": "Cap LeetCode at 3 problems a week",
        "description": "Arrays and hash maps only, until DSA covers more.",
        "reasoning": (
            "At 5–10 hours a week on 16–18 credits, LeetCode can take your whole budget. "
            "Three focused problems keep the interview habit going for your internship "
            "search and leave room for step 4."
        ),
        "est_time": "Ongoing",
        "status": "pending",
    },
    {
        "title": "Build one solo Python project, start to finish",
        "description": "Small scope, multi-file, deployed, with a README you wrote yourself.",
        "reasoning": (
            "A solo project sized to about four of your 5–10 weekly hours lets you answer "
            "\"what did you build\" in internship interviews without splitting credit. "
            "As a sophomore, one finished project beats three half-done ones."
        ),
        "est_time": "4–6 weeks",
        "status": "pending",
    },
    {
        "title": "Apply to 15–20 sophomore internship programs",
        "description": "Programs aimed at first- and second-years, applied to in one focused push.",
        "reasoning": (
            "Several internship programs are built for sophomores specifically. On 16–18 "
            "credits, one focused 2–3 week push beats trickling applications out all semester."
        ),
        "est_time": "2–3 weeks",
        "status": "pending",
    },
    {
        "title": "One mock interview a month",
        "description": "With a friend, the career center, or a free peer-practice site.",
        "reasoning": (
            "An internship offer usually hinges on the interview. One hour a month fits "
            "inside 5–10 hours a week without crowding out 16–18 credits of coursework."
        ),
        "est_time": "1 hr / month",
        "status": "pending",
    },
]

_FAKE_NOT_NOW = [
    {
        "title": "Certifications",
        "reasoning": (
            "For a sophomore going after internships, certifications rarely move the needle. "
            "Your 5–10 hours buy more as a finished, deployed project."
        ),
    },
    {
        "title": "A fourth language",
        "reasoning": (
            "At 5–10 hours a week, depth in Python beats breadth. Add a language when an "
            "internship posting actually asks for it."
        ),
    },
    {
        "title": "A club leadership role",
        "reasoning": (
            "On 16–18 credits, another weekly commitment would eat the hours step 4 needs. "
            "Revisit it as a junior."
        ),
    },
]


def _build_fake_roadmap(user_id):
    roadmap_id = 1
    return {
        "id": roadmap_id,
        "user_id": user_id,
        "intake_id": 1,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "steps": [
            {"id": index, "roadmap_id": roadmap_id, "position": index, **step}
            for index, step in enumerate(_FAKE_STEPS, start=1)
        ],
        "not_now_items": [
            {"id": index, "roadmap_id": roadmap_id, **item}
            for index, item in enumerate(_FAKE_NOT_NOW, start=1)
        ],
    }
