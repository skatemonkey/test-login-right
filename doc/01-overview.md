# Overview

Read [00-table-of-contents.md](./00-table-of-contents.md) first, then use this file for system context. Next: [02-engineering-standards.md](./02-engineering-standards.md) and [03-module-catalog.md](./03-module-catalog.md).

## 1. System & Environment

### Tech Stack
- Python 3.13
- Flask API stack: Flask, Flask-CORS, Flask-JWT-Extended, Flask-SQLAlchemy, Flask-Pydantic
- Data and infra: MySQL via PyMySQL, Redis, `requests`
- Modeling and validation: Pydantic
- Quality and tests: `unittest`, Ruff, isort

### Commands to run / build / test
```bash
pipenv install
pipenv run python app.py
pipenv run python -m unittest discover tests
pipenv run ruff check app tests
```

There is no separate build step. Install dependencies before running the app or tests. On startup, `app/core/config.py` fetches MySQL connection settings from a remote config API. Redis must be reachable for realtime streaming features.

## 2. System Architecture

### High-level architecture
- `app.py` starts the server, and `app/__init__.py::create_app()` loads config, initializes JWT, database, CORS, and Redis, then registers feature blueprints.
- The repo follows `core -> module -> shared`:
  - `core`: app-level infrastructure and extension setup
  - `module`: feature packages such as `auth`, `audit`, `notification`, `permission`, `user`, `table`, and `line_chart`
  - `shared`: reusable repositories, schemas, and utilities used across features
- The common request path is `routes -> services -> shared`:
  - `routes`: HTTP, auth decorators, and response shaping
  - `services`: business logic
  - `shared`: schemas, repositories, and cross-feature helpers
- Add new features under `app/module/<feature>/`. To trace a request, start at a route, then move to its service and shared dependencies.

### File Structure
```text
app/
  core/
  module/
    auth/ audit/ notification/ permission/ user/ table/ line_chart/
  shared/
    repository/ schemas/ utils/
tests/
doc/
```
