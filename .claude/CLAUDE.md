# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Session Startup

At the start of every session, read the following files if they exist:

1. `.github/copilot-instructions.md` — shared project conventions and architecture overview kept in sync across editors.
2. `documents/CONSTITUTION.md` — non-negotiable principles and constraints that govern all development decisions.

## Commands

**Run the application natively:**
```bash
source .venv/bin/activate
python -m src.main
```

**Apply database migrations:**
```bash
alembic upgrade head
```

**Run all tests:**
```bash
pytest
```

**Run a single test file:**
```bash
pytest tests/domains/test_organizations.py
```

**Run a single test by name:**
```bash
pytest tests/domains/test_organizations.py::test_function_name
```

**Type checking:**
```bash
pyright
```

## Architecture

### Application Structure

- **Entry point**: `src/main.py` — creates the FastAPI app, registers all routers, and manages lifespan (DB engine init/dispose).
- **Configuration**: `src/configuration.py` — `pydantic-settings` based; reads `MNZ_PB_*` env vars from `.env` and `.env.<ENVIRONMENT>`. The `ENVIRONMENT` env var selects the environment file (`dev-native`, `dev-container`, `production`).
- **Database**: `src/database.py` — SQLAlchemy 2.0 async engine using `asyncpg`. Provides `retrieve_database` dependency (FastAPI `Depends`).
- **Authentication**: `src/authentication.py` — Keycloak JWT validation. Extracts user, email, roles, and organization from token claims. Organization is derived from a Keycloak group named `org-{id}-{name}`. Use `CurrentUser` type annotation in route handlers.
- **Models**: `src/models.py` — imports all ORM models from domain subpackages and re-exports them; `Base` is defined in `src/base.py`.

### Domain Structure

All business logic is organized under `src/domains/` by GHG scope:

```
src/domains/
  organizations/       # Multi-tenant org management
  users/               # User profiles and permissions
  inventories/         # GHG inventory periods
  scope1/
    mobile_combustion/
    stationary_combustion/  # Includes SPED file import
    fugitive/
    effluents/
  scope2/
    energy/            # Electricity consumption + reprocess
  scope3/
    business_travel/   # Haversine + air haul classification
  commuting/           # Gamification (points, levels, medals)
  questionnaires/      # Public token-based questionnaires
  reference_data/      # Emission factors; bulk Excel import
  reports/             # PDF (fpdf2) and Excel (openpyxl) export
```

Each domain package follows a consistent pattern:
- `models.py` — SQLAlchemy ORM models
- `schemas.py` — Pydantic request/response schemas
- `service.py` — business logic (async, takes `AsyncSession`)
- `routes.py` — FastAPI router
- `calculations.py` — pure emission calculation functions (where applicable)

### Auth Pattern

Routes that require authentication inject `CurrentUser` (from `src/authentication.py`). The Keycloak token must include a group matching `org-{id}-{name}` to identify the tenant organization. Fine-grained permissions (scope/category) are stored in DB tables, not in the JWT.

Public endpoints (questionnaires) are at `/public/questionnaires/{token}` and require no auth. Rate limiting for these is stored in the `rate_limits` DB table, keyed by `{ip}:{function_name}`.

### Testing

Tests use SQLite in-memory via `aiosqlite`. The `conftest.py` sets all required `MNZ_PB_*` env vars via `os.environ.setdefault` **before** any `src` imports. Key fixtures:
- `database_session` — isolated transaction per test (auto-rolled back)
- `client` — `httpx.AsyncClient` with DB and auth overrides
- `authenticated_user` — returns a default `AuthenticationUser`

When testing service methods that modify ORM objects in memory, call `await database_session.flush()` before `await database_session.refresh(obj)` to see DB state.

To test with a custom user (e.g., specific roles), override the `client` fixture's auth dependency directly using `app.dependency_overrides[retrieve_authentication_user]`.

## Code Style

- **No comments in code** (per project constitution).
- **No abbreviations**: use `configuration` not `config`, `authentication` not `auth`, `database` not `db`, `exception` not `e`.
- All REST API routes must be documented through OpenAPI (FastAPI handles this automatically via Pydantic schemas).
- Use `retrieve_logger(__name__)` from `src/util/logger.py` for logging.

## Tech Spec Documents

Do **not** modify files under `documents/tech-specs/` unless explicitly asked. These are specification documents managed separately.
