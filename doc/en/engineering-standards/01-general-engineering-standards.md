# General Engineering Standards

Read [00-eng-std-catalog.md](./00-eng-std-catalog.md) first and [../01-overview.md](../01-overview.md) for system context, then use this file as the canonical coding rules reference for humans and AI agents.


- Architecture flow:
  - Structure: `core -> module -> shared`.
  - Dependency rule: lower feature layers must not import upward; `shared` must not import `module`.
  - DB-backed request flow: `routes -> services -> repositories`.
- DB-backed services must not call `db.session`, ORM `.query`, or build SQLAlchemy queries; repositories own query construction, eager loading, and transaction boundaries.
- Datetime output stays `%Y-%m-%d %H:%M:%S`; DB timestamp defaults use `app/shared/utils/time.py::now_utc0`.
- Protected endpoints use `@jwt_required()`; identity comes from `app/shared/utils/auth.py::current_user_id()`.
- Import style: use absolute internal imports only (`from app...`), never relative imports (`from .` / `from ..`).
- Import behavior modules (services/utils/stream modules) using namespace style and call via that namespace so source ownership is explicit.
  - Do: `from app.module.notification import notification_service` then `notification_service.create_notification(...)`.
  - Don't: `from app.module.notification.notification_service import create_notification`.
- Barrel export rule: do not import through package `__init__.py`; import from the concrete module path instead.
  - Do: `from app.shared.model.user import User`.
  - Don't: `from app.shared.model import User`.
- Naming conventions (project-specific):
  - Data-model fields (Pydantic/dataclass): `camelCase` (e.g., `userId`, `createdAt`, `pageSize`).
  - Wire payload keys (request/response/table JSON): `camelCase`.
  - Internal variables (params/locals/helper internals/most `self` attrs): `snake_case`.
  - Functions/methods: `snake_case`.
  - Classes (including ORM models): `PascalCase`.
  - Constants: `UPPER_SNAKE_CASE`.
  - Modules/files/packages: `snake_case`.
  - Model/DB layer under `app/shared/model` keeps snake_case package/module naming for ORM files.
  - Exception: JWT query-string token parameter remains `access_token` (framework/config contract), not `accessToken`.
