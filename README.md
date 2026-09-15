# Devoyage

**A personalized roadmap generator for CS freshman.**

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

Built by CS students, for the freshmen we used to be.

## Status

🚧 **In active development** (CSC 317 group project, Fall 2026). Currently building
Tier 1: accounts, intake, roadmap generation, progress tracking.

## Tech Stack

React · FastAPI (Python) · Supabase (Postgres) · Anthropic Claude

## Team

| | |
|---|---|
| Sadia Zaman | Team lead · Database |
| Arnav Karn | Backend |
| Oluwatamilore Bamidele-Sanni | Frontend |
| Sugam Parajuli | Testing / QA |

## Contributing (team)

**Read [PROJECT_SPEC.md](PROJECT_SPEC.md) before writing any code or asking any AI
tool for help.** It is the source of truth for names, data shapes, and interfaces.
`main` is always working; branch per feature, PR before merge.