"""
Stand-ins for controllers/content.py (Arnav, Tier 2 spec 11/17):

    list_career_paths() -> list of career paths
    list_resources(category=None) -> list of resources

Same names, arguments, and dict fields as the spec. The content here is
sample data for building the screens; the real content is Sugam's, in
models/seed_data.py.
"""
from exceptions import ValidationError

CATEGORIES = ("learning", "practice", "tools", "communities", "career")

_CAREER_PATHS = [
    {
        "id": 1, "slug": "software_engineering", "title": "Software Engineering", "position": 1,
        "summary": "Designing, building, and maintaining the apps and systems people use every day.",
        "day_to_day": "Writing and reviewing code, fixing bugs, and planning features with a team. Most of the week is spent in an editor and in short check-ins with teammates.",
        "skills": ["One language in depth (Python, Java, or JavaScript)", "Data structures and algorithms", "Git and code review", "Testing and debugging"],
        "first_steps": ["Finish one multi-file project and put it on GitHub", "Practice 2-3 easy LeetCode problems a week", "Learn Git branches and pull requests"],
    },
    {
        "id": 2, "slug": "data", "title": "Data", "position": 2,
        "summary": "Turning raw data into answers: cleaning it, analyzing it, and showing what it means.",
        "day_to_day": "Writing SQL queries, cleaning data in Python, and building charts or dashboards that help a team decide something.",
        "skills": ["SQL", "Python with pandas", "Statistics basics", "Explaining results clearly"],
        "first_steps": ["Learn SQL with a free course", "Analyze a public dataset you care about", "Make one chart that answers a real question"],
    },
    {
        "id": 3, "slug": "security", "title": "Security", "position": 3,
        "summary": "Protecting systems and data by finding weaknesses before attackers do.",
        "day_to_day": "Reviewing systems for risks, monitoring alerts, and testing defenses. A lot of reading about how attacks work.",
        "skills": ["Networking basics", "Linux command line", "How the web works", "Careful, curious thinking"],
        "first_steps": ["Get comfortable in a Linux terminal", "Try beginner capture-the-flag challenges", "Join a campus security club"],
    },
    {
        "id": 4, "slug": "machine_learning", "title": "Machine Learning", "position": 4,
        "summary": "Building models that learn patterns from data to make predictions or decisions.",
        "day_to_day": "Preparing data, training and testing models, and checking whether results actually hold up.",
        "skills": ["Python", "Linear algebra and probability", "Data handling", "Evaluating models honestly"],
        "first_steps": ["Get solid at Python first", "Take a free intro ML course", "Train one small model on a public dataset"],
    },
]

_RESOURCES = [
    ("freeCodeCamp", "https://www.freecodecamp.org", "learning", "Free, structured courses where every lesson ends with something you build.", 1),
    ("CS50 (Harvard)", "https://cs50.harvard.edu/x/", "learning", "The best free intro to CS if your fundamentals feel shaky.", 1),
    ("The Odin Project", "https://www.theodinproject.com", "learning", "A free web development path built around real projects.", 1),
    ("LeetCode", "https://leetcode.com", "practice", "Interview-style problems. Stick to Easy until Data Structures feels solid.", 1),
    ("NeetCode", "https://neetcode.io", "practice", "Video walkthroughs that explain the patterns behind LeetCode problems.", 1),
    ("Exercism", "https://exercism.org", "practice", "Small exercises in many languages, with optional feedback from mentors.", 1),
    ("GitHub", "https://github.com", "tools", "Where your projects live. Recruiters look here first.", 1),
    ("VS Code", "https://code.visualstudio.com", "tools", "A free editor that works for every language you'll use in class.", 1),
    ("GitHub Student Pack", "https://education.github.com/pack", "tools", "Free tools and credits for students, including hosting for your projects.", 1),
    ("ColorStack", "https://www.colorstack.org", "communities", "A community for Black and Latinx CS students, with internship prep and events.", 1),
    ("Major League Hacking", "https://mlh.io", "communities", "Finds student hackathons, a fast way to get a first team project.", 1),
    ("Girls Who Code", "https://girlswhocode.com", "communities", "Clubs and programs that help women and nonbinary students into tech.", 1),
    ("Simplify Jobs", "https://simplify.jobs", "career", "Tracks internship postings so you don't miss application windows.", 1),
    ("Tech Interview Handbook", "https://www.techinterviewhandbook.org", "career", "Free, practical guides for resumes and technical interviews.", 1),
    ("Handshake", "https://joinhandshake.com", "career", "Your school's job board, with internships aimed at students.", 1),
]


def list_career_paths():
    return [dict(path, skills=list(path["skills"]), first_steps=list(path["first_steps"])) for path in _CAREER_PATHS]


def list_resources(category=None):
    if category is not None and category not in CATEGORIES:
        raise ValidationError("Unknown resource category.")
    resources = [
        {"id": i, "title": t, "url": u, "category": c, "why": w, "is_free": f, "position": i}
        for i, (t, u, c, w, f) in enumerate(_RESOURCES, start=1)
    ]
    return [r for r in resources if category is None or r["category"] == category]
