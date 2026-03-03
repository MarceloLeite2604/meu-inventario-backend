# Meu Inventario - Backend

Backend service for GHG (Greenhouse Gas) emissions inventory management. Provides REST API endpoints for tracking Scope 1, 2, and 3 emissions, generating compliance reports, and enabling employee commuting data collection.

## Features

- GHG emissions inventory management across Scope 1, 2, and 3 categories
- Scope 1: mobile combustion, stationary combustion, fugitive emissions, effluents
- Scope 2: electricity consumption with grid emission factors
- Scope 3: business travel with haversine distance calculation and air haul classification
- Commuting gamification with points and medals for sustainable transport
- Public questionnaires for employee commuting data collection
- PDF and Excel report generation per inventory
- Keycloak-based JWT authentication with fine-grained DB permissions
- Rate limiting on public endpoints

## Prerequisites

- Python 3.13
- PostgreSQL
- Keycloak
- [infrastructure-scripts](https://github.com/Mercado-Net-Zero/infrastructure-scripts) (for container workflows)

## Environment Setup

Create the environment files from the provided templates:

```bash
cp .env.template .env
cp .env.environment.template .env.dev-container
cp .env.environment.template .env.production
cp docker/.env.compose.template docker/.env.compose
```

Fill in the values in each file. The `.env.environment.template` variables include database URL, Keycloak connection, CORS settings, and SMTP configuration. The `docker/.env.compose` file requires the work directory and host user information.

## Running Natively

Install dependencies:

```bash
uv venv
uv pip install -r requirements.txt
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

Build the Docker image:

```bash
isbuild
```

## Executing

Start in dev-container environment:

```bash
iscomp -e dev-container up -d
```

Start in production environment:

```bash
iscomp -e production up -d
```

## Running Tests

```bash
pytest
```

## Type Checking

```bash
pyright
```
