# BuildCalcAi Backend — Technical Roadmap and Current State

This document describes the **current state** of the BuildCalcAi FastAPI backend (as present in this repository), a **target architecture**, and a phased **development plan**. Facts about existing code cite concrete modules and behaviors; roadmap sections describe intended direction.

---

## Current Project Structure

```
repair-ai-backend/
├── README.md                 # Short product description
├── requirements.txt           # Python dependencies (pinned versions)
├── pytest.ini                # pytest: pythonpath=., testpaths=tests
├── .gitignore                # Ignores .env, venv, etc.
├── alembic.ini               # Alembic configuration
├── alembic/
│   ├── README                # Alembic readme
│   ├── env.py                # Migration env; imports SQLAlchemy models for metadata
│   ├── script.py.mako        # Migration script template
│   └── versions/             # Sequential PostgreSQL migrations
├── app/
│   ├── main.py               # FastAPI app, routers, Base.metadata.create_all
│   ├── config.py             # Pydantic Settings from environment / .env
│   ├── database.py           # SQLAlchemy engine, SessionLocal, get_db
│   ├── oauth2.py             # JWT create/verify; get_current_user dependency
│   ├── models/               # SQLAlchemy ORM models (users, rooms, calculations, ai_request_logs)
│   ├── routes/               # FastAPI routers (calculation, auth, user, room, ai)
│   ├── schemas/              # Pydantic request/response models
│   ├── services/             # Business logic (room calc, OpenAI, prompts, strip foundation stub)
│   └── utils/utils.py       # bcrypt hash / verify helpers
└── tests/
    ├── test_calculation_service.py
    └── test_calculation_service_perimeter.py
```

| Area | Purpose |
|------|---------|
| **app/main.py** | Application entry: registers routers for calculation, auth, users, rooms, AI; calls `Base.metadata.create_all(bind=engine)` on startup. |
| **app/config.py** | Loads DB credentials, JWT settings, and `openai_api_key` via `pydantic-settings` (`BaseSettings`, `.env`). |
| **app/database.py** | PostgreSQL connection string, `create_engine`, `sessionmaker`, `get_db` generator, declarative `Base`. |
| **app/models/** | Persistence: `Users`, `Room`, `Calculation`, `AIRequestLog`. |
| **app/routes/** | HTTP API surface grouped by concern. |
| **app/schemas/** | API and service I/O typing (`CalculationInput`/`CalculationResponse`, room/user/AI schemas, `StripFoundation*` stubs). |
| **app/services/** | Deterministic calculators (`calculation_service`, `StripFoundation`) and AI helpers (`openai_service`, `ai_prompt_service`). |
| **app/utils/** | Password hashing with passlib bcrypt. |
| **alembic/** | Schema migrations for users, rooms, calculations, hashed_password column, room dimensions fields, `ai_request_logs`. |
| **tests/** | Unit tests targeting `calculate_room` only (partial coverage). |

**Note:** There is no `pyproject.toml`, `poetry.lock`, or `uv.lock` in this repository; dependency management is via `requirements.txt` only.

---

## What Is Already Implemented

### FastAPI routes and endpoints

| Method / path | Auth | Module | Behavior |
|---------------|------|--------|----------|
| `GET /` | No | `app/main.py` | Health-style message `{"message": "API is running"}`. |
| `POST /login` | No | `app/routes/auth.py` | OAuth2 password form; returns JWT bearer token via `oauth2.create_acces_token`. |
| `POST /users/` | No | `app/routes/user.py` | Registers user (email, name, hashed password); `UserResponse` (note: duplicate-email check logic is buggy—see risks). |
| `GET /calculations/history` | Bearer | `app/routes/calculation.py` | Lists `Calculation` rows for current user. |
| `POST /calculate` | Bearer | `app/routes/calculation.py` | Validates openings vs wall area; runs `calculate_room`; persists calculation JSON. |
| `POST /rooms/` | Bearer | `app/routes/room.py` | Creates `Room`. |
| `GET /rooms/` | Bearer | `app/routes/room.py` | Lists user rooms. |
| `GET /rooms/{room_id}` | Bearer | `app/routes/room.py` | Single room. |
| `PATCH /rooms/{room_id}` | Bearer | `app/routes/room.py` | Partial update. |
| `DELETE /rooms/{room_id}` | Bearer | `app/routes/room.py` | Delete room (204). |
| `POST /rooms/{room_id}/calculate` | Bearer | `app/routes/room.py` | Builds `CalculationInput` from room; `calculate_room`; saves with `room_project_id`. |
| `GET /rooms/{room_id}/calculations` | Bearer | `app/routes/room.py` | Calculations filtered by room. |
| `POST /ai/explain-calculation/{calculation_id}` | Bearer | `app/routes/ai.py` | Builds prompt from stored input/result; OpenAI explanation; writes `AIRequestLog`. |
| `GET /ai/logs` | Bearer | `app/routes/ai.py` | User’s AI logs, newest first. |
| `GET /ai/logs/{log_id}` | Bearer | `app/routes/ai.py` | Single log. |

There is **no HTTP route** for strip foundation calculation; `calculate_strip_foundation` exists only as a Python function.

**Production readiness:** Routing is straightforward and uses dependency injection for DB and user. Improvements: consistent error models, OpenAPI tagging/prefix conventions, rate limits, request IDs, and fixing the user registration query bug.

### Calculator services (deterministic)

1. **`app/services/calculation_service.py`** — Primary implemented calculator:
   - `floor`, `ceiling`, `perimeter`, `walls`, `tile_required_sqm`, `calculate_room`.
   - **Outputs:** floor area, ceiling area, net wall area, wall area with 10% reserve, paint liters (wall_area_with_reserve / 9), floor tile area with 10% reserve multiplier.
   - **Validation:** Openings cannot exceed perimeter×height (`ValueError` in service; HTTP 400 in route).
   - **Assessment:** Deterministic and simple; formulas are fixed assumptions (e.g. 9 m²/L paint coverage, 10% reserves). Not production-ready for diverse real-world specs without documented assumptions/warnings and configurable norms.

2. **`app/services/StripFoundation.py`** — Strip foundation concrete volume:
   - Inputs: outer `length`, `width`, `foundation_width`, `foundation_depth`, `reserve_percent` (default 10).
   - Output: perimeter, raw volume, volume with reserve.
   - **Not exposed via API.** Schemas exist in `app/schemas/StripFoundation.py` with minimal Field validation (`length`/`width`/`foundation_width`/`foundation_depth` lack `gt=0` in schema).
   - **Assessment:** Early stub; integrate route + validation + tests when prioritizing foundations.

### Schemas (`app/schemas/`)

- **`calculation.py`:** `CalculationInput`, `CalculationResponse`, `CalculationHistoryResponse` (history omits `user_id`, `room_project_id` from the model—the API still returns ORM instances filtered by shape of response_model).
- **`Room.py`:** `RoomCreate`, `RoomUpdate`, `RoomResponse`.
- **`User.py`:** `UserCreate`, `UserResponse`.
- **`ai.py`:** `AIExplanationResponse`, `AIRequestLogResponse`.
- **`token.py`:** `TokenData` for JWT payload decoding.
- **`StripFoundation.py`:** input/output models for unfinished foundation feature.

### Database and migrations

- **Engine:** PostgreSQL via `psycopg2-binary` connection string (`app/database.py`).
- **ORM:** SQLAlchemy 2.x declarative models.
- **Alembic:** Present; linear chain `929fadc57d61 → 2db5b4d0398c → 7d50aebd5c20 → e09463912808` creates/extends users, rooms, calculations, adds `hashed_password`, room dimension columns, `ai_request_logs`.
- **Startup:** `main.py` also runs `Base.metadata.create_all(bind=engine)`, which can **overlap or conflict** with Alembic if models diverge—operational risk.
- **Production readiness:** Migrations exist; dual schema management (`create_all` + Alembic) should be unified. No explicit transaction wrappers around multi-step writes beyond default session commit patterns.

### AI integration

- **`app/services/openai_service.py`:** Instantiates `OpenAI(api_key=settings.openai_api_key)`. Uses `client.responses.create(model="gpt-4.1-mini", input=prompt)` and returns `output_text`.
- **`app/services/ai_prompt_service.py`:** `build_calculation_explanation_prompt` instructs Ukrainian explanation, **not to change numbers**, not invent measurements; passes JSON-serializable input/result dicts.
- **`app/routes/ai.py`:** Loads saved calculation by ID and user; on success/error persists full prompt and response/error to **`AIRequestLog`**.
- **Current AI role:** Post-hoc natural language explanation of an **already persisted** deterministic room calculation—not a calculator, not altering figures.

**Production gaps:** No token usage/cost logging, prompt versioning field, timeouts/retries, structured explanation schema, or prompt injection hardening beyond instruction text.

### Configuration

- **`app/config.py`:** Single `Settings` object: DB host/port/name/user/password; `secret_key`, `algorithm`, `access_token_expire_minutes`; `openai_api_key`. All required fields (no defaults in code)—app fails fast if `.env` incomplete.
- **`.env`** is gitignored; no committed example `.env.sample` was found.

### Logging and observability

- **Application code:** No dedicated structured logging module; no correlation IDs in routes.
- **Dependencies:** `sentry-sdk` appears in `requirements.txt` but **no initialization** exists in `main.py` or elsewhere in the scanned codebase—currently unused.

### Authentication

- **JWT** (`python-jose`) with Bearer scheme; token URL `'login'` (path `/login`). Password hashing: **passlib** + bcrypt (`app/utils/utils.py`).

### Tests

- **`tests/test_calculation_service.py`:** Asserts floor/ceiling areas for one scenario.
- **`tests/test_calculation_service_perimeter.py`:** Asserts `wall_area` for one scenario.
- **Missing:** Routes (integration), AI (mocked), auth, room CRUD, `StripFoundation`, edge cases for openings, Alembic upgrade smoke tests.

**Assessment:** Minimal unit coverage; not sufficient for regression safety before production changes.

---

## Packages And Dependencies

The project declares dependencies only in **`requirements.txt`** (no `pyproject.toml`).

| Package | Version (pinned) | Use in this project |
|---------|------------------|---------------------|
| **fastapi** | 0.128.8 | Web framework and OpenAPI. |
| **uvicorn** | 0.39.0 | ASGI server (typical runner; not scripted in-repo). |
| **starlette** | 0.49.3 | ASGI toolkit (FastAPI dependency). |
| **pydantic** | 2.13.3 | Request/response validation. |
| **pydantic-settings** | 2.11.0 | `Settings` from environment (`.env`). |
| **pydantic-extra-types** | 2.11.1 | Available for extended types (limited direct use observed). |
| **SQLAlchemy** | 2.0.49 | ORM engine, models, sessions. |
| **alembic** | 1.16.5 | DB migrations. |
| **psycopg2-binary** | 2.9.12 | PostgreSQL driver. |
| **openai** | 2.32.0 | Official OpenAI Python SDK (`OpenAI`, `responses.create`). |
| **httpx** | 0.28.1 | HTTP client stack (often pulled by SDK/CLI tooling). |
| **python-dotenv** | 1.2.1 | Environment loading (via pydantic-settings / tooling). |
| **python-jose** | 3.5.0 | JWT encode/decode. |
| **passlib** | 1.7.4 (+ **bcrypt** 4.3.0) | Password hashing. |
| **email-validator** | 2.3.0 | `EmailStr` support in Pydantic. |
| **python-multipart** | 0.0.20 | Form uploads / OAuth2 form parser. |
| **pytest** | 8.4.2 | Test runner (`pytest.ini` present). |
| **sentry-sdk** | 2.58.0 | Listed for error reporting; **not wired in application code**. |
| **fastapi-cli** / **typer** / **rich** | various | CLI / dev tooling transitive or optional FastAPI tooling. |

No Redis, Celery, RQ, or SQLModel appears in requirements.

---

## Product Vision

BuildCalcAi should evolve into a **backend for realistic construction and renovation quantity and cost workflows**, spanning **foundation through roof**: foundations, concrete, reinforcement, masonry/blocks, walls and partitions, plaster, putty, paint, tiles, laminate and other flooring, screed, insulation, drywall, roof structure, roofing and underlayments, drainage/gutters, ancillary materials, **waste factors**, **approximate cost**, **shopping lists**, and **full estimates**.

**Non-negotiable principle:** **AI must not perform critical arithmetic** for primary quantities. All main calculations must be **deterministic** and implemented in **backend calculator services**. AI should act as:

- A **parser** of natural language into structured intents and fields.
- An **explainer** of completed `CalculationResult` objects.
- An **assistant** that asks **clarifying questions**.
- An **estimator helper** that structures multi-step estimate workflows.
- An **advisor** driven by **rules, assumptions, and a knowledge base** (later RAG).
- A **router** that selects **which calculator** to invoke; the **backend executes** the tool.

---

## Target Backend Architecture

The following layout is a **target** organization, adapted from the current codebase’s concepts (`routes`, `services`, `schemas`, `models`).

```
app/
  api/
    routes/
      calculations.py    # Room + future calculation HTTP surface
      ai.py                # Explanation, future parser/router endpoints
      projects.py          # Future: project aggregation
      rooms.py             # Room CRUD + room-scoped calculations
      estimates.py         # Future: estimates and line items
      materials.py         # Future: catalogs, norms, shopping lists

  core/
    config.py              # Settings, env
    security.py            # JWT, password policies, OAuth2 schemes
    logging.py             # Structured logging, request IDs

  domain/
    calculations/
      schemas.py           # Shared calculation DTOs
      services.py          # Orchestration / shared helpers
      validators.py
      constants.py
    foundation/
      schemas.py
      services.py          # Strip/slab/pile, concrete, rebar, etc.
      validators.py
      constants.py
    walls/
      schemas.py
      services.py
      validators.py
      constants.py
    floors/
      schemas.py
      services.py
      validators.py
      constants.py
    roofing/
      schemas.py
      services.py
      validators.py
      constants.py
    materials/
      schemas.py
      services.py
      constants.py
    estimates/
      schemas.py
      services.py
    projects/
      schemas.py
      services.py

  ai/
    client.py              # Thin OpenAI client wrapper
    schemas.py             # AIExplanation, ParsedCalculationRequest, etc.
    services/
      explanation_service.py
      parser_service.py
      tool_router.py
      estimate_ai_service.py
    prompts/
      explain_calculation_v1.txt
      parse_calculation_request_v1.txt
      generate_estimate_v1.txt
    logging.py             # AI-specific logging fields
    evals/                 # Golden tests / eval harness

  infrastructure/
    db/
      models.py            # ORM models (or split by aggregate)
      session.py
      migrations/          # Alembic (or symlink to repo alembic)
    redis/                 # Optional: cache, rate limits, queues
    storage/               # Optional: files, PDFs, uploads

  tests/
    unit/
    integration/
    ai_evals/
```

| Layer | Purpose |
|-------|---------|
| **api** | HTTP adapters only: validation, auth, status codes, mapping to domain/AI services. |
| **core** | Cross-cutting configuration, security, logging—no business rules. |
| **domain** | Deterministic calculators, shared validation, norms/constants per construction subdomain. |
| **ai** | LLM integration, prompts, structured AI outputs, routing **decisions** (not math). |
| **infrastructure** | Persistence, external systems, migrations. |
| **tests** | Fast unit tests for math; integration tests for API+DB; AI evals for parsers/routers. |

---

## Unified Calculation Result Schema

All calculator services should converge on a **single machine- and human-friendly result shape**. That yields:

- **Stable API contracts** for clients and mobile apps.
- **Easier AI explanations** (steps + formulas + assumptions are explicit).
- **Easier persistence** (`Calculation.result_data` maps naturally).
- **Easier PDF/estimate generation** from `materials` and `steps`.
- **Easier testing** (golden files per calculator).
- **Easier aggregate estimates** from many `CalculationResult` instances.

### Proposed Pydantic models (target)

```python
from pydantic import BaseModel, Field
from typing import Any


class CalculationInput(BaseModel):
    """Generic envelope; calculators may use subclasses or typed extensions."""
    calculation_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class CalculationStep(BaseModel):
    label: str
    formula: str | None = None
    input_values: dict[str, Any] = Field(default_factory=dict)
    result: float
    unit: str


class MaterialItem(BaseModel):
    name: str
    quantity: float
    unit: str
    waste_percent: float | None = None


class CalculationAssumption(BaseModel):
    key: str
    description: str
    source: str | None = None  # e.g. "default_norm", "user_override"


class CalculationWarning(BaseModel):
    code: str
    message: str
    severity: str = "warning"  # "info" | "warning" | "error"


class CalculationResult(BaseModel):
    calculation_type: str
    steps: list[CalculationStep]
    materials: list[MaterialItem]
    assumptions: list[CalculationAssumption] = Field(default_factory=list)
    warnings: list[CalculationWarning] = Field(default_factory=list)


class EstimateItem(BaseModel):
    sku_or_name: str
    quantity: float
    unit: str
    unit_price: float | None = None
    line_total: float | None = None
    calculation_type: str | None = None
    notes: str | None = None


class EstimateResult(BaseModel):
    title: str
    currency: str | None = None
    items: list[EstimateItem]
    subtotal_materials: float | None = None
    assumptions: list[CalculationAssumption] = Field(default_factory=list)
    warnings: list[CalculationWarning] = Field(default_factory=list)
```

Today’s **`CalculationResponse`** is a flat list of floats; migrating to **`CalculationResult`** would be a deliberate refactor (planned in roadmap phases).

---

## Planned Calculator Services

Below: **inputs**, **outputs** (conceptually aligned with `CalculationResult`), **assumptions**, **warnings**, and **edge cases**. This is specification-level guidance for future implementation.

### Foundation calculators

| Calculator | Primary inputs | Output highlights | Typical assumptions | Warnings / edge cases |
|------------|----------------|-------------------|---------------------|-------------------------|
| **Strip foundation** | Footprint lengths, strip width/depth, grid layout if complex | Concrete m³, surface areas | Uniform section; ignores chamfers | Depth/width → zero or negative; re-entrant corners |
| **Slab** | Length, thickness, overlaps, openings | Concrete m³, mesh area | Single plane slab | Thick vs thin slab limits; curled edges |
| **Piles** | Count or spacing, diameter, embedment | Concrete, pile cap ties | Soil capacity out of scope | Spacing vs equipment |
| **Concrete volume** | Geometry primitives or aggregated shapes | Volume, wastage layers | Density optional for mass | Units mix (mm vs m) |
| **Rebar** | Bar diameters, spans, laps, grids | kg or pieces, overlaps | Lap lengths from norms | Anchorage and stirrups omissions |
| **Formwork** | Perimeter × height panels | Area of boards | Modular panel sizes | Irregular shapes underestimated |
| **Gravel/sand cushion** | Compacted thickness, width | Volume + compaction factor | Typical 0.95–1.05 factors | Drainage slopes |
| **Waterproofing** | Surfaces linear or area | Rolls/linear meters | Lap widths | Indoor vs membrane type |

### Wall calculators

Brick/block/partition/drywall: footprint, height, openings, bonding, joint mortar. Plaster/putty/paint: substrate area layers, coats, spreads. Wallpaper: perimeter rolls. Insulation: area × thickness → packs.

**Warnings:** Opening overlap double-counted; unrealistic coat thickness; solvent vs water zones.

### Floor calculators

Screed, insulation, finishes (tile, laminate, parquet), baseboards: substrate dimensions, plank/tile dimensions, grout and adhesive spreads, expansion gaps.

**Edge cases:** Diagonal installs (higher waste), patterned tiles, thresholds.

### Roofing calculators

Plan area vs slope area, ridge/valley/eave adjustments, insulation and membranes, gutters/downpipes by perimeter and rainfall assumptions.

**Edge cases:** Multi-pitch valleys, dormers; wind zones for fastener spacing (advisory warnings only unless norms encoded).

### Estimate calculators

Material list rollup, waste by category, regional price placeholders, labor-hours by activity (explicitly approximate), room/house/full project aggregates.

**Principle:** costs and labor remain **scenario-based** with clear assumptions—not hidden single numbers.

---

## AI Integration Plan (Stages)

1. **AI explanation (current baseline + hardening)**  
   Backend computes; AI receives equivalent of `CalculationResult` (today: raw dicts) and explains **without changing numbers**.

2. **Structured AI explanation**  
   Return `{ title, short_summary, detailed_explanation, assumptions_explained, warnings, next_questions }` validated by Pydantic.

3. **Natural language parser**  
   User message → `ParsedCalculationRequest` (intent, dimensions, materials, openings, missing_fields, assumptions, confidence).

4. **Tool router**  
   Model selects **`calculate_wall_paint`**, **`calculate_floor_tiles`**, **`calculate_foundation`**, **`generate_estimate`**, etc.—**Python executes**.

5. **AI estimate assistant**  
   Guided multi-turn flow: fills gaps, batches calculator calls, assembles estimate narrative.

6. **RAG knowledge base**  
   Norms, manufacturer PDFs, FAQ; answers cite chunks.

7. **Production AI layer**  
   Prompt versioning, usage/cost per request, evals, rate limits, fallback models, injection defenses, audit logs.

---

## Planned AI Services

| Service | Responsibility |
|---------|----------------|
| **AIClient** | Centralize OpenAI calls: model selection, timeouts, retries, response parsing hooks. |
| **ExplanationService** | Input `CalculationResult` → `AIExplanation` (free text today; structured tomorrow). |
| **ParserService** | User NL → `ParsedCalculationRequest`. |
| **ToolRouter** | Maps intent + entities → calculator function names and arguments **for backend dispatch**. |
| **EstimateAIService** | Conversation state + multiple `CalculationResult` → draft `EstimateResult` narrative and checklist. |
| **AIRequestLogger** | Extended beyond current table: tokens, latency, estimated cost, feature name, prompt version, outcomes. |
| **EvalRunner** | Runs golden conversations for parser, explainer consistency, router accuracy. |

Existing **`AIRequestLog`** already stores prompt, raw response/error, status, user, calculation FK—extend rather than replace when adding metrics.

---

## Production Requirements

**Must-have before calling the system production-ready:**

- **Validation:** Per-calculator boundary checks (strict positive dims, sane openings, configurable max spans).
- **Error handling:** Consistent problem JSON (`422` vs `400` vs `503`), never leak raw stack traces externally.
- **Structured logging:** JSON logs with `request_id`, user id (hashed where needed), route, latency.
- **Request IDs:** Propagate correlation ID middleware → logs → AI audit.
- **AI request logs:** Model, tokens, cost estimate, latency, status, truncated prompt hash—not necessarily full prompts in hot storage forever.
- **Retry / timeout:** OpenAI bounded retries with jitter; deadlines per dependency.
- **Rate limits / quotas:** Per IP/user/route; distinguish AI-heavy routes.
- **DB transactions:** Atomic multi-write operations (estimate + lines).
- **Tests / AI evals:** Unit for every calculator invariant; integration for authenticated flows; periodic eval batches.
- **Migrations-only schema:** Prefer Alembic as single authority; deprecate incidental `create_all` in prod.
- **Environment config:** Validated `.env.example`, secrets injected via platform (no keys in logs).
- **Docker / CI/CD:** Build images, lint, pytest, migrate on deploy.
- **Security:** bcrypt cost review, JWT rotation/expiry refresh strategy, CSP not applicable backend-only but strict CORS, dependency scanning.
- **Prompt injection mitigation:** Sandbox tool args; reject instructions that conflict with calculator-only math policy.

---

## Planned Database Entities

| Entity | Purpose |
|--------|---------|
| **User** | Auth identity, billing tier (future), preferences. *(Exists as `Users`.)* |
| **Project** | Groups rooms/buildings/calcs for one job. *(Not present.)* |
| **Room** | Saved geometry for repeat calcs. *(Exists.)* |
| **Building** | Multi-zone envelope for roof/facade aggregates. *(Not present.)* |
| **Calculation** | Persisted deterministic run snapshot. *(Exists.)* |
| **CalculationStep** | Normalize steps for analytics (optional normalization vs JSON blob today). *(Not present.)* |
| **Material** | Canonical material catalog rows. *(Not present.)* |
| **MaterialItem** | Resolved line items referencing catalog + quantity. *(Not present.)* |
| **Estimate** | Aggregate financial/scope document. *(Not present.)* |
| **EstimateItem** | Rows in estimate referencing materials/calcs. *(Not present.)* |
| **AIRequestLog** | Audit AI calls *(exists)*; extend for tokens/cost/prompt_versions. |
| **PromptVersion** | Track hashes and rollout of prompt templates. *(Not present.)* |
| **KnowledgeDocument** | Source files for RAG. *(Not present.)* |
| **KnowledgeChunk** | Embedded segments with citations back to documents. *(Not present.)* |

---

## Backend Roadmap (Phases)

| Phase | Focus |
|-------|-------|
| **1 — Stabilize current backend** | Document architecture (this file), align naming/style across services, introduce unified `CalculationResult`, test existing calculators. |
| **2 — Improve existing calculators** | Explicit assumptions/warnings, configurable norms, deterministic rounding policy. |
| **3 — AI explanation layer** | `AIClient`, `ExplanationService`, structured outputs, prompt files + versioning. |
| **4 — Natural language input** | `ParserService`, intent detection, entity extraction, missing fields & confidence. |
| **5 — Tool calling / router** | Declare calculator tools; router selects tool; backend executes + explains. |
| **6 — More building calculators** | Foundation/wall/floor/roof as domain modules. |
| **7 — Projects and estimates** | Persist projects, rollup materials, versioning of estimates. |
| **8 — AI estimate assistant** | Multi-turn orchestration over calculators + estimate builder. |
| **9 — Observability and evals** | Tokens/cost, dashboards, regression eval pipelines. |
| **10 — RAG knowledge base** | Ingest, chunk, embed, cite; guardrails vs hallucinations. |
| **11 — Production hardening** | Rate limits, Docker, CI/CD, security review, HA DB. |

---

## Technical TODO

- [ ] Create unified `CalculationResult` schema  
- [ ] Refactor existing calculators to return `CalculationResult`  
- [ ] Add assumptions and warnings to calculators  
- [ ] Add `AIExplanation` schema  
- [ ] Add `ExplanationService`  
- [ ] Add prompt files (`prompts/*.txt`) and loader  
- [ ] Extend AI request logging (tokens, cost, latency, model, prompt_version)  
- [ ] Add `ParserService`  
- [ ] Add intent detection  
- [ ] Add entity extraction  
- [ ] Add `ToolRouter`  
- [ ] Add foundation calculators (API + validation + tests)  
- [ ] Add wall calculators  
- [ ] Add floor calculators  
- [ ] Add roofing calculators  
- [ ] Add estimate generator  
- [ ] Add broader automated tests (integration + calculators)  
- [ ] Add AI evals harness  
- [ ] Add RAG knowledge base (later phase)

---

## Current Issues And Risks

Issues below are grounded in repository inspection.

1. **`app/routes/user.py` — Broken duplicate-email query**  
   - **Where:** `create_user` uses `db.query(Users).filter(user.email == Users.email)`.  
   - **Risk:** SQLAlchemy column comparison semantics are wrong intended filter; duplicates may slip through or query misbehaves depending on dialect.  
   - **Fix:** `filter(Users.email == user.email)`.

2. **`app/main.py` — `Base.metadata.create_all`**  
   - **Risk:** Duplicate or divergent DDL vs Alembic; accidental schema drift across environments.  
   - **Fix:** Use migrations only for production-like environments; keep `create_all` only for ephemeral dev if documented.

3. **`Room` model vs `RoomCreate`**  
   - **Where:** DB column `rooms.room_type` is `nullable=False`; schema allows optional `None`.  
   - **Risk:** INSERT failure at DB if client omits room type—400 may be SQLite/Postgres constraint error surfaced poorly.  
   - **Align:** Defaults in DB/schema or require field in API.

4. **`StripFoundation` calculator not wired**  
   - **Risk:** Dead code confusion; testers cannot validate via HTTP.  
   - **Fix:** Add route behind auth + validators + tests when scope allows.

5. **`sentry-sdk` unused**  
   - **Risk:** Operational blindness to 5xx in production; dependency weight without benefit.  
   - **Fix:** Initialize Sentry in `main.py` with env DSN or remove dependency.

6. **Minimal test coverage**  
   - **Risk:** Regressions in paint/tile/heuristics unnoticed.  
   - **Expand:** Parameterized tests for walls, rounding, openings edge cases.

7. **AI path — no timeouts/structured logging**  
   - **Risk:** Hanging requests and poor debuggability.  
   - **Fix:** Client timeouts; log latency and HTTP status separately from user-facing detail.

8. **`CalculationHistoryResponse` omits linkage fields**  
   - **Where:** History rows have `room_project_id`; response model does not expose it.  
   - **Impact:** Clients cannot distinguish ad-hoc vs room-scoped history without widening schema.

9. **Typo persistence: `create_acces_token`**  
   - **Risk:** Naming inconsistency impedes refactoring and onboarding.  
   - **Fix:** Cosmetic rename (`create_access_token`) when touching auth next.

---

*Document generated from repository analysis; update as modules and migrations change.*
