# **Devoyage: Project Spec (Source of Truth)**

Group 2, CSC 317\. This file lives in the repo root. It is the single source of truth for names, data shapes, interfaces, and responsibilities. If code or research contradicts this file, the code or research is wrong, or the team agrees to change this file first. Nobody changes this file alone: changes are proposed in a meeting or the group chat, then one person commits the edit.

## **The AI rule (why this file exists)**

We all use AI tools to research and build separately. AI output is only consistent if the inputs are consistent. So:

1. Before asking Claude/ChatGPT/anything to help with your component, paste the "Shared Vocabulary," "Data Models," and "Module Contract" sections of this file into the chat and say: "conform to these names and shapes exactly."  
2. If the AI suggests something that requires changing a name, shape, function signature, or responsibility in this file, do not implement it. Bring it to the team first.  
3. If you learn something in research that the team needs (a library choice, a gotcha, a limitation), add it to the Decision Log or your phase notes here, so the next person's AI chat knows it too.  
4. AI can be used to research, prototype, explain, debug, and assist with implementation. Each member must still understand and be able to explain work submitted in their area.

## **Team**

| Person | Role |
| ----- | ----- |
| Tami | Team lead \+ Frontend (Kivy views, Figma design doc) |
| Arnav | Backend Lead (controllers, application logic, backend architecture \+ integration) |
| Sugam | AI Integration / Service — current responsibility: Anthropic integration, prompting, AI-response handling, validation, and AI-service prototyping  |
| Sadia | Database (Models) \+ config/settings file |
| Testing / QA | Owner TBD, decide before the Phase 1 gate is signed off (Activity 4 is a graded deliverable) |

   ### **Ownership boundaries going forward**

These ownership boundaries apply **from the team's approval of this revision forward**.

They do not relabel, reassign, or make claims about who historically implemented work completed under the previous division of responsibilities.

* Tami owns the View layer.  
* Arnav is Backend Lead and owns the Controller/application layer, backend architecture, controller integration, and backend-facing contracts.  
* Sugam owns the AI Service domain: Anthropic-specific research, prototypes, prompting, response handling, AI validation, AI-specific failure handling, and the eventual production AI-service implementation.  
* Sadia owns the Model/database layer and config/settings persistence.  
* Testing / QA remains a separate role and is still unassigned.

Note: Sugam currently owns the AI integration/service work required for the roadmap-generation phase. This assignment applies to the currently defined AI-service work and does not automatically assign future AI-backed features or later-phase backend responsibilities to him. Future responsibilities are decided by the team as those phases are specified. 

## **Decision Log**

Decided:

* Project: CS Roadmap Generator, repo/team name Devoyage (features and tiers per the Feature Document)  
* Tier 1 scope: accounts, structured intake, AI roadmap with reasoning, "not now" list, progress tracking  
* (09/10) LLM provider: Anthropic  
* (09/15) CONFIRMED BY PROFESSOR: Python \+ Kivy is required as the primary language/UI framework. Automatic zero otherwise. This reverses the 09/10 React/FastAPI/Supabase decision.  
* (09/15) CONFIRMED BY PROFESSOR: API calls to an AI agent are permitted, so the Anthropic SDK is approved.  
* (09/15) Stack: one Python application, MVC pattern (course requirement). UI: Kivy \+ KV language, multi-page via ScreenManager. Validation: Pydantic. Database: SQLite via built-in sqlite3. Settings: .ini file via built-in configparser (course requirement). AI: Anthropic Python SDK. Tests: pytest.  
* (09/15) Leadership: Sadia handed team lead to Tami.  
* No hosting/deployment: this is a desktop app, submitted with run instructions per the course outline.  
* (09/28) PROPOSED ROLE UPDATE: Arnav becomes Backend Lead going forward and owns controllers, backend architecture, application orchestration, and final backend integration.  
* (09/28) PROPOSED ROLE UPDATE: Sugam owns the AI Service domain going forward instead of general controller work or project-wide QA.  
* (09/28) Sugam's AI domain includes Anthropic SDK research/integration, prompt development, AI-response parsing and validation, retry/error behavior, AI-specific experiments, and AI-service prototypes.  
* (09/28) Sugam develops AI-service prototypes independently. Arnav reviews the backend-facing interface and integration requirements before the prototype becomes part of the production application.  
* (09/28) Sugam retains implementation ownership of the AI Service after review. Review does not transfer the subsystem to Arnav.  
* (09/28) Sugam's AI work may run ahead of the current implementation phase as research/prototyping so his learning schedule does not block the core MVC implementation.  
* (09/28) Tami's Frontend role and Sadia's Database/Models role remain unchanged.  
* (09/28) The new responsibility boundaries are forward-looking only. They do not reassign credit for work performed before this decision.
* (10/01) Settings Page scope decided: three persistent, per-user settings — theme (light/dark), editable weekly-hours (reuses intakes.weekly_hours), and account management (change password, change email) — persisted in a new settings table plus an update to the user's latest intake row, not config.ini, per the Phase 3 rule that app preferences stay in .ini and user data stays in the DB. Also added two roadmap actions reachable from Settings: Regenerate Roadmap (reuses existing generate_roadmap(user_id) — for when circumstances change) and Clear Roadmap Data (new clear_roadmap_data(user_id) — full reset; does not touch intake history).

Open (fill in as decided, with date):

* Testing/QA owner: decide before the Phase 1 gate can be signed off (Activity 4, the Testing & QA plan, is graded)  
* Sadia's model-layer function names: finalize them and add them to the Module Contract  
* Whether the `users` model needs a username or display-name field in addition to the currently specified fields  
* Whether `log_in` needs an intake-completion check before routing the user to the dashboard  
* Which four "additional pages" we declare for Milestone 2 (proposal below)  
* Exact controller-facing function/signature exposed by `services/ai.py`; do not introduce a new shared function name until the team agrees on it

## **Course requirements mapping (from the Semester Project Outline)**

The app must have: a dashboard homepage with 3+ features; 4 additional pages each focused on a feature set; a settings page whose settings persist in a .ini/config file; a local or remote database; MVC architecture; Python/Kivy only.

Proposed mapping (finalize at Milestone 2):

* Dashboard (3+ features): roadmap steps with reasoning, the "not now" list, progress tracking. That is three features on one screen, requirement met by our Tier 1 core.  
* Additional page 1: Intake questionnaire  
* Additional page 2: Career paths breakdown (Tier 2, F6)  
* Additional page 3: Resources hub (Tier 2, F7)  
* Additional page 4: Login/account page, or AI chat (F8) if schedule allows; decide at Milestone 2  
* Settings page: three persistent per-user preferences — theme (light/dark), editable weekly-hours, and account management (change password, change email) — plus two roadmap actions: Regenerate Roadmap (for when life changes and the current plan no longer fits) and Clear Roadmap Data (a full reset to start over). The three preferences persist in the database, not config.ini, since they're user data, not app-wide settings (see 10/01 Decision Log and the Phase 3 rule on app preferences vs. user data). Regenerate reuses the existing generate_roadmap(user_id); Clear is a new function (below).

## **Shared Vocabulary**

Use these words to mean exactly this, in code, docs, and AI chats:

* **Intake**: the structured questionnaire a user fills once (or refills later). NOT called "survey," "quiz," or "onboarding" anywhere in code.  
* **Roadmap**: the generated plan. One active roadmap per user in Tier 1\.  
* **Step**: one item in a roadmap. Has reasoning attached. NOT called "task," "milestone," or "card."  
* **Not-now item**: one item on the not-now list, with reasoning. Part of the same generation as the roadmap.  
* **Status**: a step is either `pending` or `done`. Exactly these two strings in Tier 1\.  
* **Screen**: one Kivy page. Screen names (ScreenManager ids): `landing`, `login`, `signup`, `intake`, `dashboard`, `settings`, plus Tier 2 screens when specced.

## **Architecture (MVC, one Python app)**

* devoyage/  
*   main.py            \# app entry point, ScreenManager setup  
*   config.ini         \# settings (course requirement)  
*   models/            \# Sadia: database access, one module per table group  
*   views/             \# Tami: Kivy screens (.py) \+ layout (.kv files)  
*   controllers/       \# Arnav: application logic between views, services, and models  
*   services/ai.py     \# Sugam: Anthropic SDK calls, prompt, AI-response handling  
    tests/             \# Testing/QA owner TBD: pytest suites \+ manual test scripts

Views never touch the database directly, and models never import Kivy. Everything crosses through controllers. That separation IS the MVC requirement being graded.

The AI service is a backend subsystem behind the controller layer. Views do not call `services/ai.py` directly.

### **Layer ownership going forward**

**Tami — Views**

* user  
*   ↓  
* Kivy views  
*   ↓  
  controller calls

**Arnav — Controllers / Backend integration**

* views  
*   ↓  
* controllers  
*   ↓  
  AI service and/or models

**Sugam — AI Service**

* structured intake supplied by controller  
*   ↓  
* prompt construction  
*   ↓  
* Anthropic  
*   ↓  
* response parsing  
*   ↓  
* AI-output validation  
*   ↓  
  validated result or AIServiceError

**Sadia — Models**

* controller  
*   ↓  
* models  
*   ↓  
  SQLite / config

The normal roadmap-generation path is:

* Tami View  
*     ↓  
* Arnav Controller  
*     ↓  
* Sugam AI Service  
*     ↓  
* Arnav Controller  
*     ↓  
* Sadia Model  
*     ↓  
  SQLite

The AI service never writes directly to the database.

## **Data Models (Database source of truth)**

Sadia owns the implementation in SQLite; everyone conforms to these names. All names snake\_case.

**users**

* id (primary key)  
* email (unique, required)  
* password\_hash (required; NEVER a plain password anywhere, including logs)  
* created\_at

> Open question: whether a username or display-name field should be added. Until the team decides and updates this section, the model remains exactly as listed above.

**intakes**

* id (primary key)  
* user\_id (foreign key \-\> users.id)  
* year: one of `freshman | sophomore | junior | senior`  
* major\_status: `declared | intending | deciding`  
* has\_pipeline: `yes | no | unsure`  
* coursework: list from `intro | oop | dsa | none`  
* skills: list of objects `{ language: python|cpp|java|js|other, level: class_only|small_solo|multi_file }`  
* project\_count: `0 | 1 | 2_3 | 4_plus`  
* biggest\_project\_type: `solo | team | tutorial | ai_generated | none`  
* deployed: `yes | no`  
* carrying: list from `online_course | leetcode | hackathons | club_leadership | research | certifications | none`  
* weekly\_hours: `under_5 | 5_10 | 10_15 | 15_plus`  
* credit\_load: `12_15 | 16_18 | 19_plus`  
* goal: `internship | first_project | explore_cs | fundamentals`  
* free\_text (optional, max \~500 chars)  
* created\_at

(List/object fields are stored as JSON strings in SQLite; models handle the json.dumps/loads so nobody else does.)

**roadmaps**

* id (primary key)  
* user\_id (foreign key \-\> users.id)  
* intake\_id (foreign key \-\> intakes.id)  
* generated\_at

**roadmap\_steps**

* id (primary key)  
* roadmap\_id (foreign key \-\> roadmaps.id)  
* position (integer, display order)  
* title  
* description (what it is)  
* reasoning (why this, why now, for this user)  
* est\_time (human string, e.g. "2-3 weeks")  
* status: `pending | done`

**not\_now\_items**

* id (primary key)  
* roadmap\_id (foreign key \-\> roadmaps.id)  
* title  
* reasoning (why to skip it for now)

**settings**

* user\_id (primary key, foreign key \-\> users.id) — one row per user, created at sign\_up with theme `light`  
* theme: `light | dark`  
* updated\_at

(weekly_hours is not duplicated here — it's updated in place on the user's latest intakes row. Email/password are updated in place on users.)

Tier 2 tables (resources, career paths, chat) get added here before anyone builds them.

## **Module Contract (how views, controllers, services, and models connect)**

Replaces the old HTTP endpoint contract: same names and shapes, now Python function signatures.

These ownership labels are forward-looking and do not make claims about who originally implemented existing code.

Tami's views call ONLY controller functions.

Arnav owns controller/application orchestration going forward.

Sadia owns model/database functions.

Sugam's AI service is called through the controller layer.

### **Auth (controllers/auth.py)**

Forward owner: Arnav.

* `sign_up(email, password) -> user_id` (hashes password, creates user, raises on duplicate email)  
* `log_in(email, password) -> user_id` (raises on bad credentials)  
* `log_out()` (clears current session state)  
* Session: the controller layer tracks the logged-in user\_id in one place; views never pass identity around themselves.

> Open question: whether successful `log_in` also needs an intake-completion check before the application decides whether to route to `intake` or `dashboard`. Until decided, do not silently change the existing `log_in` contract.

### **Intake and roadmap (controllers/intake.py, controllers/roadmap.py)**

Forward owner: Arnav.

This is an ownership boundary going forward. It does **not** reassign credit for code already contributed under the previous responsibility split.

Existing controller contract:

* `save_intake(user_id, intake_data) -> intake_id` (intake\_data validated by Pydantic against the intakes shape)  
* `generate_roadmap(user_id) -> roadmap` (gets the latest intake, uses the AI service, validates the application flow, saves through Sadia's models, returns)  
* `get_current_roadmap(user_id) -> roadmap with steps ordered by position + not_now_items`  
* `set_step_status(step_id, status) -> None` (status must be `pending` or `done`)
* `clear_roadmap_data(user_id) -> None` (deletes all of the user's roadmaps, including history, along with their steps and not-now items, for a full reset; does not touch intake history, so the user can regenerate from their existing intake or redo intake first)

### **Settings (controllers/settings.py)**

Forward owner: Arnav.

* `get_settings(user_id) -> settings_data` (combines theme from the settings table with weekly_hours from the user's latest intake, for the Settings screen to display)
* `update_theme(user_id, theme) -> None`
* `update_weekly_hours(user_id, weekly_hours) -> None` (updates weekly_hours on the user's latest intake row; does not create a new intake)
* `change_password(user_id, current_password, new_password) -> None` (raises AuthError if current_password is wrong; reuses the hashing logic from sign_up)
* `change_email(user_id, new_email) -> None` (raises on duplicate email, same as sign_up)

### **Model-layer contract**

Owner: Sadia.

The model-layer function names still need to be finalized and recorded here.

Until that decision is made:

* controllers use the agreed model interfaces already present in the codebase;  
* this document does not invent new model function names;  
* once the team agrees on the model API, the exact function signatures are added here.

### **AI-service contract**

Owner: Sugam.

The service is responsible for:

* Anthropic SDK interaction;  
* prompt construction;  
* raw AI response handling;  
* JSON parsing;  
* AI-output validation;  
* retry-once behavior;  
* AI-specific failure handling;  
* environment/API-key handling.

The service receives the structured information needed for generation from the controller and returns either:

* a validated result conforming to the LLM Output Contract; or  
* `AIServiceError`.

**The exact shared Python function name/signature between `controllers/roadmap.py` and `services/ai.py` is still open and must be agreed on before being added to this Module Contract.**

Do not invent a permanent service function name in individual code or AI chats before that agreement.

The AI service does NOT:

* query SQLite;  
* save roadmap rows;  
* access Kivy views;  
* manage session state;  
* decide which user's intake should be used;  
* decide persistence policy.

### **Errors**

Controllers/services raise our own exception types (e.g. `AuthError`, `ValidationError`, `AIServiceError`) with a human-readable message.

Views catch them and show the message; views never crash on an expected failure.

## **LLM Output Contract (AI integration source of truth)**

The generation prompt must instruct the model to return ONLY this JSON, no prose, no markdown fences:

* {  
*   "steps": \[  
*     { "title": "...", "description": "...", "reasoning": "...", "est\_time": "..." }  
*   \],  
*   "not\_now": \[  
*     { "title": "...", "reasoning": "..." }  
*   \]  
  }

Rules:

* 5 to 9 steps, 2 to 5 not\_now items.  
* `services/ai.py` validates every required field exists before anything is returned to the controller.  
* Malformed response: strip markdown fences if present, retry once, then raise `AIServiceError`.  
* Never save a partial roadmap.  
* The API key lives in a .env file (gitignored) or environment variable, NEVER in code, NEVER in config.ini (config.ini is committed; the key is a secret).  
* reasoning fields must reference the user's actual intake (their hours, their carrying list, their level), not generic advice. This is the product's whole identity.

## **AI-service development rule**

Sugam owns the AI-service domain, but development is prototype-first.

His AI work may run ahead of the core phase implementation because research for later phases can start anytime.

Expected workflow:

* research / learning  
*         ↓  
* standalone experiment  
*         ↓  
* working prototype  
*         ↓  
* Sugam explains design and implementation  
*         ↓  
* Arnav reviews backend interface \+ integration  
*         ↓  
* Sugam addresses required changes  
*         ↓  
* production services/ai.py  
*         ↓  
  controller integration

Arnav's review covers:

* compatibility with the agreed backend contract;  
* application architecture;  
* error propagation;  
* integration;  
* whether shared interfaces need team approval.

Sugam remains responsible for the implementation of his AI-service domain.

Prototype code does not become production code automatically.

## **Phase plan and research briefs**

Phases are sequential gates: a phase is open for building only when the previous one passes its gate.

Research for a later phase can start anytime.

The role changes in this proposal are forward-looking. This phase plan does not attempt to rewrite historical contribution or declare Phase 1 complete before the team confirms that status.

### **Phase 1: Skeleton (Accounts \+ Intake, features F1 \+ F2)**

Phase 1 completion status: **pending team confirmation**.

The implementation responsibilities for Phase 1 were carried out under the responsibility structure that existed at the time. This revised spec does not reassign credit for that work.

Going forward:

* Tami owns the relevant Kivy views and frontend behavior.  
* Arnav owns the relevant controller/application behavior.  
* Sadia owns database/model/config behavior.  
* Sugam begins his AI-service research/prototype track in preparation for Phase 2\.

  #### **Sugam — AI foundation / pre-Phase-2 research**

Research/learn:

* Python functions;  
* dictionaries and lists;  
* loops and conditionals;  
* imports;  
* `try/except`;  
* JSON;  
* environment variables;  
* basic API concepts;  
* Anthropic Python SDK basics;  
* the Devoyage intake structure;  
* the LLM Output Contract.

Research should produce useful artifacts, such as:

* notes;  
* code experiments;  
* example API responses;  
* prompt experiments;  
* questions/limitations discovered.

First bounded prototype:

Build a standalone Anthropic experiment that sends a basic prompt and receives a response.

This prototype is independent of the production MVC application.

#### **Phase 1 test checklist**

The Phase 1 gate remains concrete even though the formal Testing/QA owner is still TBD.

The person assigned by the team to perform/sign off the Phase 1 checklist must verify:

* two users see only their own data;  
* every intake field round-trips;  
* password appears nowhere in plain text;  
* under-5-minute intake completion.

  ### **Gate to Phase 2**

Phase 2 opens only when:

1. the team confirms the Phase 1 implementation is ready for gate testing;  
2. the Phase 1 checklist above passes;  
3. blocking failures discovered by the checklist are resolved;  
4. the team records who performed the QA sign-off.

The permanent Testing/QA owner can still remain an open organizational item, but the Phase 1 gate cannot be waived because the role is unresolved.

### **Phase 2: The Brain (Roadmap \+ Not-now, features F3 \+ F4)**

#### **Tami — Frontend**

* dashboard screen rendering steps in position order with reasoning visible;  
* not-now list styled unmistakably distinct;  
* loading state while generation runs;  
* UI must not freeze while generation is running;  
* views call controller functions only.

  #### **Arnav — Backend Lead / Controllers**

* finalize the controller-to-AI-service contract with Sugam and record the exact shared signature in the Module Contract before production integration;  
* implement and own `generate_roadmap`;  
* implement and own `get_current_roadmap`;  
* retrieve the user's latest intake through Sadia's model layer;  
* pass the agreed structured data to the AI-service interface;  
* receive the validated AI-service result;  
* save validated roadmap data through Sadia's model layer;  
* maintain application-level errors and orchestration;  
* review AI-service integration before merge;  
* use a stub/mock AI-service implementation if necessary so core MVC development is not blocked by the prototype schedule.

Arnav owns the integration boundary, not Sugam's internal AI implementation.

#### **Sadia — Models / Database**

* roadmap persistence;  
* roadmap\_steps persistence;  
* not\_now\_items persistence;  
* dashboard/current-roadmap read;  
* regeneration policy (keep history, current \= latest);  
* user/data isolation;  
* finalize required model-layer function names with the team and add them to the Module Contract.

  #### **Sugam — AI Service**

Sugam works through research/prototype cycles rather than being given one large production deadline.

##### **Cycle 1 — Anthropic \+ Prompt Prototype**

Research:

* Anthropic Python SDK;  
* request/response behavior;  
* prompt construction;  
* structured-output prompting;  
* how intake information should be represented in prompts;  
* how to reduce generic roadmap responses.

Completion task:

Create a standalone prototype:

* sample intake  
*     ↓  
* prompt  
*     ↓  
* Anthropic  
*     ↓  
  roadmap response

  ##### **Cycle 2 — Prompt Evaluation**

Maintain at least two standing AI-evaluation profiles:

**Overloaded**

* 19+ credits;  
* multiple competing commitments;  
* limited weekly hours.

**Brand New**

* deciding major;  
* little prior experience;  
* few current commitments.

Research/test:

* whether generated roadmaps are meaningfully different;  
* whether reasoning references intake specifics;  
* whether workload recommendations respect available time;  
* whether not-now items are genuinely specific.

Completion task:

Produce an improved prompt plus evidence from the test profiles.

##### **Cycle 3 — Response Parsing**

Research:

* JSON;  
* `json.loads`;  
* dictionaries/lists;  
* malformed JSON;  
* markdown fences;  
* response cleanup.

Completion task:

Build a parser prototype that turns the raw model output into the expected Python structure or fails predictably.

##### **Cycle 4 — AI-output validation**

Research:

* required fields;  
* count validation;  
* defensive programming;  
* exceptions.

Completion task:

Validate:

* `steps` exists;  
* `not_now` exists;  
* required fields exist;  
* 5 to 9 steps;  
* 2 to 5 not-now items.

  ##### **Cycle 5 — Failure handling**

Research:

* Anthropic/API exceptions;  
* malformed responses;  
* retry behavior;  
* API-key/environment handling;  
* service-level failure handling.

Completion task:

Produce an integrated AI-service prototype that:

1. accepts the agreed structured controller input;  
2. constructs the prompt;  
3. calls Anthropic;  
4. parses the result;  
5. validates the LLM Output Contract;  
6. retries once after malformed output;  
7. raises `AIServiceError` when a valid response still cannot be produced;  
8. returns the validated result.

   ##### **Production integration review**

When Sugam's prototype is ready:

1. Sugam demonstrates and explains it.  
2. Arnav reviews the backend-facing interface and integration behavior.  
3. Any change to a shared function signature or data shape goes to the team before implementation.  
4. Sugam makes the required AI-service revisions.  
5. The team records the approved service function signature in the Module Contract.  
6. The service is integrated into `controllers/roadmap.py`.  
7. Sugam continues owning the AI-service implementation.

   #### **Gate to Phase 3**

The gate remains testable:

* both standing AI profiles generate valid roadmaps;  
* outputs are meaningfully different where the intake differs;  
* reasoning references intake specifics;  
* malformed-response behavior fails cleanly;  
* invalid/partial roadmaps are never persisted;  
* roadmap generation/persistence works end to end;  
* View \-\> Controller \-\> AI Service \-\> Model boundaries are preserved;  
* blocking Phase 1/2 regression failures are resolved.

The formal Testing/QA owner, once assigned, coordinates the cross-system gate. Component owners still test their own areas.

### **Phase 3: Alive (Progress \+ Settings, feature F5 \+ course-required settings page)**

#### **Tami — Frontend**

* checkboxes calling `set_step_status`;  
* settings screen;  
* frontend rendering/state behavior.

  #### **Arnav — Backend Lead**

* settings read/write through the controller layer;  
* `set_step_status`;  
* backend/application orchestration;  
* backend regression fixes;  
* maintain controller/service/model boundaries.

  #### **Sadia — Models / Database**

* persistence required for step status;  
* settings that belong in the DB vs `.ini`;  
* (resolved 10/01: settings table holds theme; weekly_hours stays on intakes; config.ini remains app-level only — see Decision Log)  
* rule: app preferences in `.ini`, user data in DB;  
* model/config helpers required by the controller.

  #### **Sugam — AI Service**

Phase 3 does not move Sugam into unrelated settings/progress implementation.

He continues developing and maintaining the AI subsystem.

Research/possible completion work:

* API failure cases;  
* prompt regressions;  
* unusual intake combinations;  
* response consistency;  
* AI-output validation tests;  
* AI-specific automated tests;  
* identified AI-service bugs;  
* prompt improvements based on observed failure cases.

  #### **Gate**

* step status persists after closing/reopening;  
* settings persist correctly;  
* Phase 1 functionality still works;  
* Phase 2 roadmap generation still works;  
* AI-service errors still fail cleanly;  
* full end-to-end run passes on a fresh clone using only README run instructions.

  ### **Phase 4+: Tier 2 pages (career paths, resources, chat)**

Specced here before building, same pattern:

* model additions  
*     ↓  
* contract additions  
*     ↓  
  per-role briefs

The fixed forward ownership continues.

**Tami**

* new Kivy screens;  
* frontend interaction;  
* navigation;  
* visual integration.

**Arnav**

* controllers;  
* backend architecture;  
* application orchestration;  
* service/model integration.

**Sadia**

* new tables;  
* model functions;  
* persistence;  
* config/database behavior.

**Sugam**

* AI research/prototyping;  
* prompts;  
* AI-service implementation for AI-backed features;  
* AI-specific evaluation and failure handling.

If AI chat becomes a Tier 2 feature, it naturally falls inside Sugam's AI-service domain, subject to the same prototype \-\> review \-\> integration workflow.

## **Backend \+ AI collaboration rules**

Arnav and Sugam own different levels of the backend.

Arnav defines/owns:

* controller behavior;  
* application orchestration;  
* backend architecture;  
* the service boundary;  
* integration with Sadia's models;  
* final backend integration.

Sugam owns:

* Anthropic-specific implementation;  
* prompt construction;  
* AI response processing;  
* AI-output validation;  
* retry/error handling inside the AI service;  
* AI-service research and prototypes.

Arnav's controller should not depend on:

* Anthropic request syntax;  
* prompt internals;  
* raw model response formats.

Sugam's service should not depend on:

* Kivy;  
* session-state ownership;  
* SQLite;  
* model persistence policy;  
* view routing.

If either side needs a shared contract changed, the change is proposed to the team and recorded here before production implementation.

## **Prototype rule**

A prototype is a learning and proof-of-concept environment.

Prototype code may be rough while a concept is being learned.

Production code may not.

Before prototype code enters `services/ai.py`:

* Sugam can explain the implementation;  
* the behavior conforms to the LLM Output Contract;  
* secrets are handled correctly;  
* expected errors are controlled;  
* the shared interface has been agreed;  
* Arnav has reviewed the backend integration boundary;  
* unnecessary prototype-only code is removed.

## **Testing / QA**

Testing remains required even while the formal Testing/QA owner is TBD.

Each component owner is responsible for basic testing of their own area:

* Tami: frontend behavior;  
* Arnav: controllers/backend orchestration;  
* Sadia: models/database/config;  
* Sugam: AI-service behavior.

The formal Testing/QA owner, once selected, coordinates:

* phase checklists;  
* cross-component tests;  
* regression testing;  
* QA documentation;  
* graded Activity 4 work;  
* gate sign-off.

Until that person is selected, the team must still explicitly assign someone to execute and record each required gate checklist. An unassigned QA role does not remove the gate.

## **Working agreements**

* Git: `main` is always working.  
* Branch per feature (`feat/intake-screen`, `feat/ai-prototype`, etc.).  
* Pull request before merge.  
* At least one other person approves.  
* Nobody commits secrets.  
* `.env` is in `.gitignore` from commit one.  
* config.ini contains no secrets.  
* Each member can explain their own component's code.  
* If an AI wrote a chunk you cannot explain, you are not done with that chunk.  
* Prototype-first development is allowed for new subsystems.  
* Prototype code does not automatically become production code.  
* Arnav reviews changes to backend integration/contracts.  
* Sugam owns AI-service implementation after the service boundary is agreed.  
* Tami retains Frontend ownership.  
* Sadia retains Model/database ownership.  
* This file changes only by team agreement.  
* The Decision Log gets a dated line every time something is decided, including in group chat.  
* Stuck for more than an hour: post in the group chat with what you tried. Do not silently rewrite someone else's area to unblock yourself.  
* Grade-driven discipline (documentation and process are over half the rubric): meeting minutes for EVERY meeting, submitted every 2 weeks (15% of grade, lead tracks this); individual journals updated at every milestone (graded separately); the Figma design document is worth 20% and gets real time, not leftovers.  
*