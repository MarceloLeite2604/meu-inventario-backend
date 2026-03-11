# Pegada Backend — Copilot Instructions

FastAPI backend for GHG (Greenhouse Gas) emissions inventory management. Multi-tenant, Keycloak-authenticated, PostgreSQL-backed.

## Build and Test

```bash
# Activate virtualenv
source .venv/bin/activate

# Run application
python -m src.main

# Apply migrations
alembic upgrade head

# Run all tests
pytest

# Run a single test file or test
pytest tests/domains/test_organizations.py
pytest tests/domains/test_organizations.py::test_function_name

# Type check
pyright
```

## Architecture

**Entry point**: `src/main.py` — creates the FastAPI app, registers all routers, manages lifespan (DB engine init/dispose).

**Configuration**: `src/configuration.py` — Pydantic-settings; reads `MNZ_PB_*` env vars from `.env` and `.env.<ENVIRONMENT>`. The `ENVIRONMENT` env var selects the environment file.

**Database**: `src/database.py` — SQLAlchemy 2.0 async engine (`asyncpg`). Inject via `DatabaseSession = Annotated[AsyncSession, Depends(retrieve_database)]`. Auto-commits on success, auto-rollbacks on exception.

**Authentication**: `src/authentication.py` — Keycloak JWT validation. Organization is derived from a group named `org-{id}-{name}`. Inject `current_user: CurrentUser` in route handlers. Fine-grained permissions (scope/category) are stored in DB, not in the JWT.

**Models**: `src/models.py` — re-exports all ORM models; `Base` is defined in `src/base.py`.

### Domain Structure

All business logic lives in `src/domains/` organized by GHG scope:

```
src/domains/
  organizations/        # Multi-tenant org management
  users/                # User profiles and permissions
  inventories/          # GHG inventory periods
  scope1/
    mobile_combustion/
    stationary_combustion/  # Includes SPED file import
    fugitive/
    effluents/
  scope2/
    energy/             # Electricity consumption + reprocess
  scope3/
    business_travel/    # Haversine + air haul classification
  commuting/            # Gamification (points, levels, medals)
  questionnaires/       # Public token-based questionnaires
  reference_data/       # Emission factors; bulk Excel import
  reports/              # PDF (fpdf2) and Excel (openpyxl) export
```

Each domain follows this file pattern:
- `models.py` — SQLAlchemy ORM models
- `schemas.py` — Pydantic request/response schemas
- `service.py` — async business logic, takes `AsyncSession`
- `routes.py` — FastAPI router
- `calculations.py` — pure emission calculation functions (where applicable), using dataclasses for I/O

## Code Style

- **No comments in code.** Code must be self-explanatory.
- **No abbreviations**: use `configuration` not `config`, `authentication` not `auth`, `database` not `db`, `exception` not `e`, etc.
- **Logging**: use `retrieve_logger(__name__)` from `src/util/logger.py`. Never use `print`.
- **Naming**: ORM model fields and DB column names are in Portuguese; Python code, configuration, and API field names are in English.
- **Service errors**: raise `HTTPException` directly from service functions (not routes).
- **Database flush**: call `await session.flush()` before `await session.refresh(obj)` to read DB-generated state.

## Testing Conventions

- Tests use SQLite in-memory via `aiosqlite`. `conftest.py` sets all required `MNZ_PB_*` env vars **before** any `src` imports.
- Key fixtures in `tests/conftest.py`:
  - `database_session` — isolated transaction per test, auto-rolled back
  - `client` — `httpx.AsyncClient` with DB and auth overrides
  - `authenticated_user` — returns a default `AuthenticationUser`
- To test with a custom user (e.g., specific roles), override the auth dependency directly via `app.dependency_overrides[retrieve_authentication_user]`.
- Test classes group related scenarios (`TestListOrganizations`, `TestCreateOrganization`, etc.).

## Public Endpoints

Questionnaire endpoints at `/public/questionnaires/{token}` require no authentication but are rate-limited. Rate limit state is stored in the `rate_limits` table, keyed by `{ip}:{function_name}`.

## Project Constitution

Before implementing any task, read `documents/CONSTITUTION.md`. It defines the non-negotiable principles and constraints that govern all development decisions in this project.

## Tech Spec Documents

Do **not** modify files under `documents/tech-specs/` unless explicitly asked.
