# AGENTS v2 Guide

## 1. Purpose and Usage
- This file is the primary navigation map for AI agents working in this repository.

## 2. Engineering Standards
- Architecture flow: `routes` -> `schemas` -> `service` -> `repository`.
- Datetime output stays `%Y-%m-%d %H:%M:%S`; DB timestamp defaults use `app/shared/utils/time.py::now_utc0`.
- Protected endpoints use `@jwt_required()`; identity comes from `app/shared/utils/auth.py::current_user_id()`.
- Import style: use absolute internal imports only (`from app...`), never relative imports (`from .` / `from ..`).
- Import behavior modules (services/utils/stream modules) using namespace style and call via that namespace so source ownership is explicit.
- Do not rely on package barrel exports from `__init__.py` (e.g., avoid `from app.shared.repository import User`); import from concrete module paths instead.
- PEP 8 naming: functions/variables/modules `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.


## 3. Module Catalog (Full Index)

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
  - `app/module/table_display/output_table_class/output_table_1_class/__init__.py`
  - `app/module/table_display/output_table_class/output_table_2_class/__init__.py`
  - `app/module/table_display/output_table_class/output_table_3_class/__init__.py`
  - `app/module/table_display/output_table_class/output_table_4_class/__init__.py`
  - `app/module/table_display/output_table_class/shared/convert_to_json_layout.py`
  - `app/module/table_display/output_table_class/shared/convert_to_json_data.py`
