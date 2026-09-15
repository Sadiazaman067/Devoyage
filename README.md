# Devoyage

**A personalized roadmap generator for CS freshmen students — Built by CS students, for the freshmen we used to be.**

CS freshmen trying to break into tech face a flood of contradictory guidance: grind
LeetCode, get certifications, build projects, do research, use AI, avoid AI. There's
no way to tell what's true, what applies to them, or why. The problem isn't a lack
of information. It's the lack of trustworthy, personalized structure.

Devoyage turns that noise into a sequenced, semester-scale plan. A student answers a
short structured intake (under 5 minutes), and gets:

- **A roadmap** where every step carries plain-language reasoning: what it is, why it
  comes next *for them*, and roughly how long it takes
- **A "not now" list**: things this specific student should deliberately ignore for
  the moment, and why. Nobody online tells students what to drop. We do.
- **Progress tracking** across the semester



## Status

🚧 **In active development** (CSC 317 group project, Fall 2026). Currently in Phase 1:
accounts, intake, and the database layer.

## Tech

Python · Kivy (UI) · SQLite · Pydantic · Anthropic Claude · pytest

Desktop application, MVC architecture. Run instructions will land here once Phase 1 integrates.

## Team

| | |
|---|---|
| Oluwatamilore (Tami) Bamidele-Sanni | Team lead · Frontend (Kivy views, Figma) |
| Arnav Karn | Backend (controllers + AI service) |
| Sugam Parajuli | Backend (controllers + AI service) |
| Sadia Zaman | Database (models) · Config |

## Repository layout
main.py # app entry point (ScreenManager)
config.ini # app settings (configparser)
models/ # database access — Sadia
views/ # Kivy screens + .kv layouts — Tami
controllers/ # logic between views and models — Arnav + Sugam
services/ # AI generation (Anthropic SDK) — Arnav + Sugam
tests/ # p


## Contributing (team)

**Read [PROJECT_SPEC.md](PROJECT_SPEC.md) before writing any code or asking any AI
tool for help.** It is the source of truth for names, data shapes, and function
signatures. `main` is always working; branch per feature, PR before merge; `.env`
is never committed.
