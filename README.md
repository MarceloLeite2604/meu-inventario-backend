# Pegada - Backend

Backend service for GHG (Greenhouse Gas) emissions inventory management. Provides REST API endpoints for tracking Scope 1, 2, and 3 emissions, generating compliance reports, and enabling employee commuting data collection.

## Features

- GHG emissions inventory management across Scope 1, 2, and 3 categories
- Scope 1: mobile combustion, stationary combustion (with SPED file import), fugitive emissions, effluents treatment
- Scope 2: electricity consumption with grid emission factors
- Scope 3: business travel with haversine distance calculation and air haul classification
- Commuting gamification with points, levels, streaks, and medals for sustainable transport
- Public questionnaires for employee commuting data collection (token-based, no authentication required)
- PDF and Excel report generation per inventory
- Keycloak-based JWT authentication with fine-grained database permissions
- Rate limiting on public endpoints

## Prerequisites

- Python 3.13
- [infrastructure-scripts](https://github.com/Mercado-Net-Zero/infrastructure-scripts)

## Environment Setup

Create the environment files from the provided templates:

```bash
cp .env.template .env
cp .env.environment.template .env.dev-native
cp .env.environment.template .env.dev-container
cp .env.environment.template .env.production
cp docker/.env.compose.template docker/.env.compose
```

Fill in the values in each file according to the target environment.

## Environment Variables

The project uses a three-tier environment variable detection system:

- **`docker/.env.compose`**: Used when building Docker images and spinning up containers. Contains build-time variables such as the work directory and service port.
- **`.env`**: Used for project execution in all environments. Contains variables common across all environments, such as remote debugging settings.
- **`.env.<environment>`**: Used for project execution in a specific environment (e.g., `.env.dev-native`, `.env.dev-container`, `.env.production`). Contains environment-specific variables such as the database URL, Keycloak connection settings, CORS configuration, and SMTP credentials.

The following variables are automatically managed by `infrastructure-scripts` and do not need to be defined manually:

- `HOST_UID`: Host user ID
- `HOST_GID`: Host group ID
- `HOST_USERNAME`: Host username
- `IMAGE_TAG`: Image tag, defined based on the current git commit hash

Additional environment variables managed by `infrastructure-scripts` commands may apply. Check its documentation for details.

## Running Natively

Activate the virtual environment and install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Apply database migrations:

```bash
alembic upgrade head
```

Start the server:

```bash
python -m src.main
```

## Building

The Docker image is built using `isbuild` from `infrastructure-scripts`. For backend services, no environment flag is required:

```bash
isbuild
```

The output image is named `mnz-pegada` and tagged with the current git commit hash (e.g., `mnz-pegada:a3b2c1d`).

Before building, ensure `docker/.env.compose` is filled with the appropriate values.

## Executing

Start in dev-container environment:

```bash
iscomp -e dev-container up -d
```

Start in production environment:

```bash
iscomp -e production up -d
```

The environment can also be set via the `MNZ_IS_ENVIRONMENT` variable to avoid repeating the `-e` flag:

```bash
export MNZ_IS_ENVIRONMENT=production
iscomp up -d
```

Before executing, ensure `.env` and the corresponding `.env.<environment>` file are filled with the appropriate values.

## Running Tests

```bash
pytest
```

## Type Checking

```bash
pyright
```
