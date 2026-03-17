# Overview

Read [00-doc-catalog.md](./00-doc-catalog.md) first, then use this file for system context. Next: [02-change-context-map.md](./02-change-context-map.md), [engineering-standards/00-eng-std-catalog.md](./engineering-standards/00-eng-std-catalog.md), and [modules/00-module-catalog.md](./modules/00-module-catalog.md).

## 1. System & Environment

### 1.1 Tech Stack
- Python 3.13
- Flask API stack: Flask, Flask-CORS, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-Pydantic
- Data and infra: MySQL via PyMySQL, Redis, `requests`
- Modeling and validation: Pydantic
- Quality and tests: `unittest`, Ruff, isort

### 1.2 Commands to run / build / test
```bash
pipenv install
pipenv run python app.py
pipenv run python -m unittest discover tests
pipenv run ruff check app tests
```

There is no separate build step. Install dependencies before running the app or tests. On startup, `app/core/config.py` fetches MySQL connection settings from a remote config API. Redis must be reachable for realtime streaming features.

## 2. System Architecture

### 2.1 High-level architecture
- `app.py` starts the server, and `app/__init__.py::create_app()` loads config, initializes JWT, database, CORS, and Redis, then registers feature blueprints.
- The repo is organized into three main package areas:
  - `core`: app-level infrastructure, extension setup, and infra clients
  - `module`: feature packages such as `auth`, `audit`, `notification`, `permission`, `user`, `table`, and `line_chart`
  - `shared`:
    - models: SQLAlchemy table definitions
    - schemas: Request/Response models (DTOs)
    - utilities: common helper functions
- The current dependency graph is:
![Overview dependency graph](../-files/overview.png)
  - `app -> core`
  - `app -> module`
  - `module -> shared`
  - `module -> core`
  - `shared -> core`

- The common request path for DB-backed modules is `routes -> services -> repositories`:
  - `routes`: HTTP, auth decorators, and response shaping
  - `services`: business logic
  - `repositories`: database operations and queries
- DB-backed modules commonly use the flat trio `*_routes.py`, `*_service.py`, and `*_repository.py`.
- Architectural exceptions in this phase: `line_chart` and `table` use non-SQL access patterns and are not normalized to the repository pattern.
- Add new features under `app/module/<feature>/`. To trace a DB-backed request, start at a route, then move to its service and repository dependencies; use `shared` models, schemas, and utilities as supporting context.

### 2.2 File Structure
```text
app/
  core/
  module/
    auth/ audit/ notification/ permission/ user/ table/ line_chart/
  shared/
    model/ schemas/ utils/
tests/
doc/
```
