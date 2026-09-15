# CS Roadmap Generator: Project Spec (Source of Truth)

Group 2, CSC 317. This file lives in the repo root. It is the single source of truth for names, data shapes, and interfaces. If code or research contradicts this file, the code or research is wrong, or the team agrees to change this file first. Nobody changes this file alone: changes are proposed in a meeting or the group chat, then one person commits the edit.

## The AI rule (why this file exists)

We all use AI tools to research and build separately. AI output is only consistent if the inputs are consistent. So:

1. Before asking Claude/ChatGPT/anything to help with your component, paste the "Shared Vocabulary," "Data Models," and "Interface Contract" sections of this file into the chat and say: "conform to these names and shapes exactly."
2. If the AI suggests something that requires changing a name, shape, or endpoint in this file, do not implement it. Bring it to the team first.
3. If you learn something in research that the team needs (a library choice, a gotcha, a limitation), add it to the Decision Log or your phase notes here, so the next person's AI chat knows it too.

## Team

| Person | Role |
|---|---|
| Sadia | Team lead + Database |
| Arnav | Backend |
| Tami | Frontend |
| Sugam | Testing / QA |
| (shared) | AI integration currently unassigned as a solo role; prompt design and validation live in Phase 2 work, owner to be confirmed |

## Decision Log

Decided:
- Project: CS Roadmap Generator (features and tiers per the Feature Document)
- Tier 1 scope: accounts, structured intake, AI roadmap with reasoning, "not now" list, progress tracking
- Roles: as above
- (09/10) Backend: FastAPI + Pydantic (validation) + Anthropic SDK, JSON everywhere
- (09/10) Database + auth platform: Supabase (Postgres)
- (09/10) Frontend: React; Figma for visual design before building
- (09/10) LLM provider: Anthropic (follows from the SDK choice)

Open (fill in as decided, with date):
- [ ] Hosting: ____ (~$5/month tier vs free-with-cold-starts; decide before deployment)
- [ ] Team/project name: ____
- [ ] Architecture question for Arnav + Sadia to settle before backend code: does React talk ONLY to FastAPI (which talks to Supabase), or also directly to Supabase for auth/reads? Recommendation: everything through FastAPI in Tier 1. One path is easier to build, test, and keep consistent with the Interface Contract; direct-to-Supabase (the Crewmate pattern) is powerful but requires learning row-level security properly.

## Shared Vocabulary

Use these words to mean exactly this, in code, docs, and AI chats:

- **Intake**: the structured questionnaire a user fills once (or refills later). NOT called "survey," "quiz," or "onboarding" anywhere in code.
- **Roadmap**: the generated plan. One active roadmap per user in Tier 1.
- **Step**: one item in a roadmap. Has reasoning attached. NOT called "task," "milestone," or "card."
- **Not-now item**: one item on the not-now list, with reasoning. Part of the same generation as the roadmap.
- **Status**: a step is either `pending` or `done`. Exactly these two strings in Tier 1.

## Data Models (Database source of truth)

Sadia owns the implementation; everyone conforms to these names. All names snake_case. Types are conceptual; Sadia maps them to the chosen database.

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

**roadmaps**
- id (primary key)
- user_id (foreign key -> users.id)
- intake_id (foreign key -> intakes.id, the intake it was generated from)
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

## Interface Contract (how frontend, backend, and AI connect)

Arnav owns the implementation; Tami builds against these exact paths and shapes; Sugam tests against them. If Option A (server-rendered) is chosen, some of these become page routes returning HTML instead of JSON, but paths, methods, and field names stay identical.

Auth:
- `POST /auth/signup` body `{ "email": ..., "password": ... }` -> creates user, starts session
- `POST /auth/login` body `{ "email": ..., "password": ... }` -> starts session
- `POST /auth/logout` -> ends session
- All routes below require a logged-in session and only ever touch that user's rows.

Intake and roadmap:
- `POST /intake` body: exactly the intakes fields above (minus id/user_id/created_at) -> saves intake
- `POST /roadmaps/generate` -> builds prompt from latest intake, calls LLM, validates, saves, returns the roadmap
- `GET /roadmaps/current` -> the user's latest roadmap with steps (ordered by position) and not_now_items
- `PATCH /steps/{id}` body `{ "status": "done" }` or `{ "status": "pending" }` -> updates one step

Error shape (every endpoint, every error): `{ "error": { "code": ..., "message": ... } }` with proper HTTP status codes. No endpoint ever returns a raw crash.

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
- Backend validates every required field exists before saving. Malformed response: strip markdown fences if present, retry once, then return the standard error shape. Never save a partial roadmap.
- reasoning fields must reference the user's actual intake (their hours, their carrying list, their level), not generic advice. This is the product's whole identity; Sugam tests for it.

## Phase plan and research briefs (what each person figures out, per time)

Phases are sequential gates: a phase is open for building only when the previous one passes its gate. Research for a later phase can start anytime.

### Phase 1: Skeleton (Accounts + Intake, features F1 + F2)

- Sadia: how to set up the chosen database and create the five tables above; how migrations/changes will be handled when the schema evolves; how the team shares one dev database (or copies).
- Arnav: chosen framework's project structure; how sessions/auth work in it (password hashing with bcrypt-class library, session cookies); how form/JSON data is received and validated; implement `/auth/*` and `POST /intake`.
- Tami: HTML/CSS fundamentals; forms (inputs, select, checkbox, POST); build signup, login, and the full intake form matching the intakes model exactly; how the chosen frontend approach talks to the endpoints.
- Sugam: how to test APIs by hand (the framework's docs UI, or Postman/curl); write the Phase 1 test checklist: two users see only their own data; every intake field round-trips; password appears nowhere in plain text; under-5-minute intake completion.
- Gate to Phase 2: Sugam's checklist passes.

### Phase 2: The Brain (Roadmap + Not-now, features F3 + F4)

- AI integration owner (confirm who): prompt design that produces the LLM Output Contract; how to call the chosen LLM API from Python; API key handling via environment variables (.env, never committed); validation and the retry-once rule.
- Arnav: `POST /roadmaps/generate` and `GET /roadmaps/current`; saving validated output into roadmaps/roadmap_steps/not_now_items.
- Sadia: efficient reads for the dashboard (roadmap + steps + not-now in one fetch); what happens to old roadmaps when a user regenerates (proposal: keep history, `current` = latest).
- Tami: dashboard page rendering steps in position order with reasoning visible; not-now list styled distinctly (it is the signature feature).
- Sugam: build two standing test intake profiles, "Overloaded" (19+ credits, carrying 5 things, under 10 hours) and "Brand New" (deciding major, nothing yet). Test: visibly different roadmaps, reasoning references intake specifics, malformed-response path fails cleanly.
- Gate to Phase 3: both test profiles pass.

### Phase 3: Alive (Progress tracking + Deploy, feature F5)

- Tami: checkbox interaction calling `PATCH /steps/{id}`; loading and error states on every fetch/submit (budget real time, this always takes longer than expected).
- Arnav: the PATCH endpoint; deployment of the backend, env vars on the host.
- Sadia: production database setup and backup story.
- Sugam: cross-browser persistence test; the full end-to-end run (signup -> intake -> roadmap -> check steps -> logout -> login) on the live URL; regression check of Phases 1-2.
- Gate: the end-to-end run passes on the deployed URL.

### Phase 4+: Tier 2 features (career paths, resources hub, chat)

Specced here before building, same pattern: model additions -> contract additions -> per-role briefs.

## Working agreements

- Git: `main` is always working. Branch per feature (`feat/intake-form`), pull request before merge, at least one other person approves. Nobody commits secrets; `.env` is in `.gitignore` from commit one.
- Each member can explain their own component's code. If an AI wrote a chunk you cannot explain, you are not done with that chunk.
- This file changes only by team agreement. The Decision Log gets a dated line every time something is decided, including in group chat.
- Stuck for more than an hour: post in the group chat with what you tried. Do not silently rewrite someone else's area to unblock yourself.