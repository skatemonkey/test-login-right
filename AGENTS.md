# AGENTS Guide

## Purpose
This file is the primary navigation map for AI agents working in this repository.
Use this map first and jump directly to listed files; avoid full codebase rescans unless this map is outdated.

## Core Rules
1. Hierarchy: `core/` -> `module/` -> `shared/`. Keep business logic in `*-service.py`, not in route handlers.
2. API flow standard: `routes` -> `schemas` -> `service` -> `repository` (and `db.session` only in service layer).
3. Register every new blueprint in `app/__init__.py`; endpoint prefixes are owned there.
4. Keep API payload field names camelCase to match frontend contracts (for example `pageSize`, `createdAt`, `isActive`).
5. Datetime output format should stay `%Y-%m-%d %H:%M:%S`; DB timestamp defaults use `app/shared/utils/time.py::now_utc0`.
6. Protected endpoints use `@jwt_required()` and user identity should come from `app/shared/utils/auth.py::current_user_id()`.
7. SQLAlchemy models are in schema `py_mgmt_test`; keep `__table_args__` schema + constraints consistent when adding models.
8. Prefer namespace-style imports for shared/internal modules and call methods via that namespace so usage is explicit (for example `from app.shared.utils import auth as auth_utils` then `auth_utils.current_user_id()`, or `from app.shared.utils import pagination_utils` then `pagination_utils.paginate(...)`).

## Project Entry Points
- `app.py`
- `app/__init__.py`
- `app/core/config.py`
- `app/core/db_ext.py`
- `app/shared/repository/__init__.py`

## Module Catalog (Full Index)

### `auth` (`app/module/auth`)
- Blueprint prefix: `/auth`
- Endpoints:
  - `POST /auth/login`
- Key files:
  - `app/module/auth/auth_routes.py`
  - `app/module/auth/auth_service.py`
  - `app/shared/schemas/auth_schema.py`

### `audit` (`app/module/audit`)
- Blueprint prefix: `/audit`
- Endpoints:
  - `POST /audit/log`
  - `POST /audit/log/query`
- Key files:
  - `app/module/audit/audit_routes.py`
  - `app/module/audit/audit_service.py`
  - `app/shared/schemas/audit_schema.py`
  - `app/shared/repository/audit_log.py`

### `notification` (`app/module/notification`)
- Blueprint prefix: `/notifications`
- Endpoints:
  - `GET /notifications`
  - `PATCH /notifications/<notification_id>/read`
  - `PATCH /notifications/read-all`
  - `GET /notifications/unread-count`
  - `GET /notifications/stream` (SSE)
  - `POST /notifications/mock-approve`
- Key files:
  - `app/module/notification/notification_routes.py`
  - `app/module/notification/notification_service.py`
  - `app/module/notification/notification_stream.py`
  - `app/shared/schemas/notification_schema.py`
  - `app/shared/repository/notification.py`

### `table` (`app/module/table`)
- Blueprint prefix: `/tables`
- Endpoints:
  - `GET /tables/layout/<table_id>`
  - `GET /tables/data/<table_id>`
- Key files:
  - `app/module/table/table_routes.py`
  - `app/module/table_display/table_registry.py`

### `permission` (`app/module/permission`)
- Blueprint prefix: `/permissions`
- Endpoints:
  - `POST /permissions/query`
  - `POST /permissions`
  - `PUT /permissions/<permission_id>`
- Key files:
  - `app/module/permission/permission_routes.py`
  - `app/module/permission/permission_service.py`
  - `app/shared/schemas/permission_schema.py`
  - `app/shared/repository/permission.py`

### `user` (`app/module/user`)
- Blueprint prefix: `/users`
- Endpoints:
  - `POST /users/query`
  - `GET /users/permission-matrix`
  - `GET /users/<user_id>`
  - `POST /users`
  - `PUT /users/<user_id>`
  - `PUT /users/<user_id>/permissions/<permission_id>`
- Key files:
  - `app/module/user/user_routes.py`
  - `app/module/user/user_service.py`
  - `app/shared/schemas/user_schema.py`
  - `app/shared/repository/user.py`
  - `app/shared/repository/user_permission.py`

### `table-display` (`app/module/table_display`)
- Purpose: internal table layout/data generation used by `/tables/*` endpoints.
- Key files:
  - `app/module/table_display/table_registry.py`
  - `app/module/table_display/schema/table_schema.py`
  - `app/module/table_display/outputTableClass/outputTable1Class/__init__.py`
  - `app/module/table_display/outputTableClass/outputTable2Class/__init__.py`
  - `app/module/table_display/outputTableClass/outputTable3Class/__init__.py`
  - `app/module/table_display/outputTableClass/outputTable4Class/__init__.py`
  - `app/module/table_display/outputTableClass/shared/convert_to_json_layout.py`
  - `app/module/table_display/outputTableClass/shared/convert_to_json_data.py`

## Shared Layer Index (Where To Find Common Concerns)
- ORM entities: `app/shared/repository/`
- DTO/request-response schemas: `app/shared/schemas/`
- JWT current-user helper: `app/shared/utils/auth.py`
- Pagination/search/sorting helpers: `app/shared/utils/pagination_utils.py`
- Time helpers (`UTC0`/`now_utc0`): `app/shared/utils/time.py`
- Password hash generation helper script: `app/shared/utils/password_hash_generator.py`

## Core Layer Index
- Flask app factory + blueprint registration: `app/__init__.py`
- SQLAlchemy extension object: `app/core/db_ext.py`
- Runtime config (JWT + DB URI bootstrap): `app/core/config.py`
- Core export surface: `app/core/__init__.py`

## Fast Task-To-File Map
- Add/change endpoint in existing module -> `app/module/<module>/<module>_routes.py` + matching `*_service.py` + related schema in `app/shared/schemas/`
- Add a new module blueprint -> `app/module/<module>/` + register in `app/__init__.py`
- Change login/token behavior -> `app/module/auth/auth_service.py` + `app/shared/schemas/auth_schema.py` + JWT config in `app/core/config.py`
- Change paginated list behavior -> target `*_service.py` + `app/shared/schemas/pagination_schema.py` + `app/shared/utils/pagination_utils.py`
- Change permission matrix/assignable actions -> `app/module/user/user_service.py` (`ALLOWED_PERMISSION_ACTIONS`)
- Change notification SSE flow -> `app/module/notification/notification_routes.py` + `notification_stream.py` + `notification_service.py`
- Change table payload/layout generation -> `app/module/table_display/table_registry.py` + selected class in `outputTableClass/` + corresponding converter in `outputTableClass/shared/`
- Add/modify DB model -> `app/shared/repository/*.py` + service logic + schema mapping in related `app/shared/schemas/*.py`

## No-Rescan Workflow Rule
Follow this checklist before any broad repository scan:
1. Start with this AGENTS module catalog.
2. Jump directly to the listed file paths for the task.
3. Rescan only if target file/path is missing or outdated.
4. If structure changes, update `AGENTS.md` in the same PR/task.

## Maintenance Rule
When adding or restructuring a module:
1. Add/update the module row in the Module Catalog.
2. Add/update endpoint mapping (including blueprint prefix).
3. Add/update key files (`routes`, `service`, `schemas`, `repository`, and helpers as applicable).
4. Update the Fast Task-To-File Map if new cross-cutting patterns are introduced.
