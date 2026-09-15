# Devoyage: Project Spec (Source of Truth)

Group 2, CSC 317. This file lives in the repo root. It is the single source of truth for names, data shapes, and interfaces. If code or research contradicts this file, the code or research is wrong, or the team agrees to change this file first. Nobody changes this file alone: changes are proposed in a meeting or the group chat, then one person commits the edit.

## The AI rule (why this file exists)

We all use AI tools to research and build separately. AI output is only consistent if the inputs are consistent. So:

1. Before asking Claude/ChatGPT/anything to help with your component, paste the "Shared Vocabulary," "Data Models," and "Module Contract" sections of this file into the chat and say: "conform to these names and shapes exactly."
2. If the AI suggests something that requires changing a name, shape, or function signature in this file, do not implement it. Bring it to the team first.
3. If you learn something in research that the team needs (a library choice, a gotcha, a limitation), add it to the Decision Log or your phase notes here, so the next person's AI chat knows it too.

## Team

| Person | Role |
|---|---|
| Tami | Team lead + Frontend (Kivy views, Figma design doc) |
| Arnav | Backend (controllers + AI service, split with Sugam) |
| Sugam | Backend (controllers + AI service, split with Arnav) |
| Sadia | Database (Models) + config/settings file |
| Testing / QA | Owner TBD, decide by end of Phase 1 (Activity 4 is a graded deliverable) |

## Decision Log

Decided:
- Project: CS Roadmap Generator, repo/team name Devoyage (features and tiers per the Feature Document)
- Tier 1 scope: accounts, structured intake, AI roadmap with reasoning, "not now" list, progress tracking
- (09/10) LLM provider: Anthropic
- (09/15) CONFIRMED BY PROFESSOR: Python + Kivy is required as the primary language/UI framework. Automatic zero otherwise. This reverses the 09/10 React/FastAPI/Supabase decision.
- (09/15) CONFIRMED BY PROFESSOR: API calls to an AI agent are permitted, so the Anthropic SDK is approved.
- (09/15) Stack: one Python application, MVC pattern (course requirement). UI: Kivy + KV language, multi-page via ScreenManager. Validation: Pydantic. Database: SQLite via built-in sqlite3. Settings: .ini file via built-in configparser (course requirement). AI: Anthropic Python SDK. Tests: pytest.
- (09/15) Leadership: Sadia handed team lead to Tami.
- No hosting/deployment: this is a desktop app, submitted with run instructions per the course outline.

Open (fill in as decided, with date):
- [ ] Testing/QA owner: decide by end of Phase 1 (Activity 4, the Testing & QA plan, is graded)
- [ ] How Arnav and Sugam split controllers vs services/ai.py (their call, log it here when made)
- [ ] Which four "additional pages" we declare for Milestone 2 (proposal below)
- [ ] What goes in Settings beyond the required config management (proposal below)
- [ ] (09/15) Sugam's Phase 1 brief: since he moved from QA to backend, he takes the AI-owner research items (Anthropic SDK, prompt design, validation) OR splits Arnav's controller brief; the pytest/test-checklist items in the phase briefs move to whoever takes Testing

## Course requirements mapping (from the Semester Project Outline)

The app must have: a dashboard homepage with 3+ features; 4 additional pages each focused on a feature set; a settings page whose settings persist in a .ini/config file; a local or remote database; MVC architecture; Python/Kivy only.

Proposed mapping (finalize at Milestone 2):
- Dashboard (3+ features): roadmap steps with reasoning, the "not now" list, progress tracking. That is three features on one screen, requirement met by our Tier 1 core.
- Additional page 1: Intake questionnaire
- Additional page 2: Career paths breakdown (Tier 2, F6)
- Additional page 3: Resources hub (Tier 2, F7)
- Additional page 4: Login/account page, or AI chat (F8) if schedule allows; decide at Milestone 2
- Settings page: theme or text size, regenerate/clear roadmap data, manage account. Settings persist to config.ini via configparser.

## Shared Vocabulary

Use these words to mean exactly this, in code, docs, and AI chats:

- **Intake**: the structured questionnaire a user fills once (or refills later). NOT called "survey," "quiz," or "onboarding" anywhere in code.
- **Roadmap**: the generated plan. One active roadmap per user in Tier 1.
- **Step**: one item in a roadmap. Has reasoning attached. NOT called "task," "milestone," or "card."
- **Not-now item**: one item on the not-now list, with reasoning. Part of the same generation as the roadmap.
- **Status**: a step is either `pending` or `done`. Exactly these two strings in Tier 1.
- **Screen**: one Kivy page. Screen names (ScreenManager ids): `landing`, `login`, `signup`, `intake`, `dashboard`, `settings`, plus Tier 2 screens when specced.

## Architecture (MVC, one Python app)

```
devoyage/
  main.py            # app entry point, ScreenManager setup
  config.ini         # settings (course requirement)
  models/            # Sadia: database access, one module per table group
  views/             # Tami: Kivy screens (.py) + layout (.kv files)
  controllers/       # Arnav: logic between views and models
  services/ai.py     # AI owner: Anthropic SDK calls, prompt, validation
  tests/             # Sugam: pytest suites + manual test scripts
```

Views never touch the database directly, and models never import Kivy. Everything crosses through controllers. That separation IS the MVC requirement being graded.

## Data Models (Database source of truth)

Sadia owns the implementation in SQLite; everyone conforms to these names. All names snake_case.

**users**
- id (primary key)
- email (unique, required)
- password_hash (required; NEVER a plain password anywhere, including logs)
- created_at

**intakes**
- id (primary key)
- user_id (foreign key -> users.id)
- year: one of `freshman | sophomore | junior | senior`
- major_status: `declared | intending | deciding`
- has_pipeline: `yes | no | unsure`
- coursework: list from `intro | oop | dsa | none`
- skills: list of objects `{ language: python|cpp|java|js|other, level: class_only|small_solo|multi_file }`
- project_count: `0 | 1 | 2_3 | 4_plus`
- biggest_project_type: `solo | team | tutorial | ai_generated | none`
- deployed: `yes | no`
- carrying: list from `online_course | leetcode | hackathons | club_leadership | research | certifications | none`
- weekly_hours: `under_5 | 5_10 | 10_15 | 15_plus`
- credit_load: `12_15 | 16_18 | 19_plus`
- goal: `internship | first_project | explore_cs | fundamentals`
- free_text (optional, max ~500 chars)
- created_at

(List/object fields are stored as JSON strings in SQLite; models handle the json.dumps/loads so nobody else does.)

**roadmaps**
- id (primary key)
- user_id (foreign key -> users.id)
- intake_id (foreign key -> intakes.id)
- generated_at

**roadmap_steps**
- id (primary key)
- roadmap_id (foreign key -> roadmaps.id)
- position (integer, display order)
- title
- description (what it is)
- reasoning (why this, why now, for this user)
- est_time (human string, e.g. "2-3 weeks")
- status: `pending | done`

**not_now_items**
- id (primary key)
- roadmap_id (foreign key -> roadmaps.id)
- title
- reasoning (why to skip it for now)

Tier 2 tables (resources, career paths, chat) get added here before anyone builds them.

## Module Contract (how views, controllers, and models connect)

Replaces the old HTTP endpoint contract: same names and shapes, now Python function signatures. Arnav owns controllers; Tami's views call ONLY these functions; Sugam tests against them.

Auth (controllers/auth.py):
- `sign_up(email, password) -> user_id` (hashes password, creates user, raises on duplicate email)
- `log_in(email, password) -> user_id` (raises on bad credentials)
- `log_out()` (clears current session state)
- Session: the controller layer tracks the logged-in user_id in one place; views never pass identity around themselves.

Intake and roadmap (controllers/intake.py, controllers/roadmap.py):
- `save_intake(user_id, intake_data) -> intake_id` (intake_data validated by Pydantic against the intakes shape)
- `generate_roadmap(user_id) -> roadmap` (builds prompt from latest intake, calls services/ai.py, validates, saves, returns)
- `get_current_roadmap(user_id) -> roadmap with steps ordered by position + not_now_items`
- `set_step_status(step_id, status) -> None` (status must be `pending` or `done`)

Errors: controllers raise our own exception types (e.g. `AuthError`, `ValidationError`, `AIServiceError`) with a human-readable message. Views catch them and show the message; views never crash on an expected failure.

## LLM Output Contract (AI integration source of truth)

The generation prompt must instruct the model to return ONLY this JSON, no prose, no markdown fences:

```json
{
  "steps": [
    { "title": "...", "description": "...", "reasoning": "...", "est_time": "..." }
  ],
  "not_now": [
    { "title": "...", "reasoning": "..." }
  ]
}
```

Rules:
- 5 to 9 steps, 2 to 5 not_now items.
- services/ai.py validates every required field exists before anything is saved. Malformed response: strip markdown fences if present, retry once, then raise AIServiceError. Never save a partial roadmap.
- The API key lives in a .env file (gitignored) or environment variable, NEVER in code, NEVER in config.ini (config.ini is committed; the key is a secret).
- reasoning fields must reference the user's actual intake (their hours, their carrying list, their level), not generic advice. This is the product's whole identity; Sugam tests for it.

## Phase plan and research briefs

Phases are sequential gates: a phase is open for building only when the previous one passes its gate. Research for a later phase can start anytime.

### Phase 1: Skeleton (Accounts + Intake, features F1 + F2)

- Tami: Kivy fundamentals (App, widgets, layouts), ScreenManager navigation, KV language basics; build landing, signup, login, and intake screens matching the Figma designs and the intakes field names exactly.
- Arnav: password hashing (passlib/bcrypt) in plain Python; the session-state pattern; Pydantic models for intake validation; implement auth and save_intake against Sadia's models.
- Sadia: sqlite3 module, creating the five tables, parameterized queries (non-negotiable, SQL injection is a graded-project-ending bug), the JSON-string pattern for list fields; plus config.ini read/write via configparser.
- Sugam: pytest basics; write the Phase 1 test checklist: two users see only their own data; every intake field round-trips; password appears nowhere in plain text; under-5-minute intake completion.
- Gate to Phase 2: Sugam's checklist passes.

### Phase 2: The Brain (Roadmap + Not-now, features F3 + F4)

- AI owner: Anthropic Python SDK; prompt design producing the LLM Output Contract; validation and the retry-once rule; .env key handling.
- Arnav: generate_roadmap and get_current_roadmap wired end to end; saving validated output into roadmaps/roadmap_steps/not_now_items via Sadia's models.
- Sadia: the dashboard read (roadmap + steps + not-now in one call); regeneration policy (keep history, current = latest).
- Tami: dashboard screen rendering steps in position order with reasoning visible; not-now list styled unmistakably distinct (it is the signature feature); loading state while generation runs (it takes seconds, the UI must not freeze: research Kivy Clock or threading for this one thing).
- Sugam: two standing test intake profiles, "Overloaded" (19+ credits, carrying 5 things, under 10 hours) and "Brand New" (deciding major, nothing yet). Test: visibly different roadmaps, reasoning references intake specifics, malformed-response path fails cleanly.
- Gate to Phase 3: both test profiles pass.

### Phase 3: Alive (Progress + Settings, feature F5 + course-required settings page)

- Tami: checkboxes calling set_step_status; the settings screen.
- Arnav: settings read/write through a controller to configparser; set_step_status.
- Sadia: any settings that live in the DB vs the .ini (rule: app preferences in .ini, user data in DB).
- Sugam: persistence test (check steps, close app, reopen, still checked); full end-to-end run; regression of Phases 1-2.
- Gate: the end-to-end run passes on a fresh clone using only the README run instructions.

### Phase 4+: Tier 2 pages (career paths, resources, chat)

Specced here before building, same pattern: model additions -> contract additions -> per-role briefs. These fill the "4 additional pages" course requirement per the mapping above.

## Working agreements

- Git: `main` is always working. Branch per feature (`feat/intake-screen`), pull request before merge, at least one other person approves. Nobody commits secrets; `.env` is in `.gitignore` from commit one; config.ini contains no secrets.
- Each member can explain their own component's code. If an AI wrote a chunk you cannot explain, you are not done with that chunk.
- This file changes only by team agreement. The Decision Log gets a dated line every time something is decided, including in group chat.
- Stuck for more than an hour: post in the group chat with what you tried. Do not silently rewrite someone else's area to unblock yourself.
- Grade-driven discipline (documentation and process are over half the rubric): meeting minutes for EVERY meeting, submitted every 2 weeks (15% of grade, lead tracks this); individual journals updated at every milestone (graded separately); the Figma design document is worth 20% and gets real time, not leftovers.