# Module Catalog

Read [../00-doc-catalog.md](../00-doc-catalog.md) first and [../01-overview.md](../01-overview.md) for system context, then use this file as the feature index.

## 1. `auth` (`app/module/auth`)
- Blueprint prefix: `/auth`
- Endpoints:
  - `POST /auth/login`
- Key files:
  - `app/module/auth/auth_routes.py`
  - `app/module/auth/auth_service.py`
  - `app/module/auth/auth_repository.py`
  - `app/shared/schemas/auth_schema.py`

## 2. `audit` (`app/module/audit`)
- Blueprint prefix: `/audit`
- Endpoints:
  - `POST /audit/log`
  - `POST /audit/log/query`
- Key files:
  - `app/module/audit/audit_routes.py`
  - `app/module/audit/audit_service.py`
  - `app/module/audit/audit_repository.py`
  - `app/shared/schemas/audit_schema.py`
  - `app/shared/model/audit_log.py`

## 3. `notification` (`app/module/notification`)
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
  - `app/module/notification/notification_repository.py`
  - `app/module/notification/notification_stream.py`
  - `app/shared/schemas/notification_schema.py`
  - `app/shared/model/notification.py`

## 4. `line_chart` (`app/module/line_chart`)
- Blueprint prefix: `/line-chart`
- Data access: Redis-backed module with a dedicated repository layer for RedisTimeSeries history and pub/sub access.
- Endpoints:
  - `POST /line-chart/history`
  - `GET /line-chart/stream` (SSE)
- Key files:
  - `app/module/line_chart/line_chart_redis_repository.py`
  - `app/module/line_chart/line_chart_routes.py`
  - `app/module/line_chart/line_chart_service.py`
  - `app/module/line_chart/line_chart_stream_service.py`
  - `app/shared/schemas/line_chart_schema.py`
  - `app/module/line_chart/pickle_test/long_running_program_demo.py`
  - `app/module/line_chart/pickle_test/long_running_program_btc_abc.py`

## 5. `table` (`app/module/table`)
- Blueprint prefix: `/tables`
- Current exception: route handlers call internal table display code directly; repository layer is not introduced in this phase.
- Endpoints:
  - `GET /tables/layout/<table_id>`
  - `GET /tables/data/<table_id>`
- Key files:
  - `app/module/table/table_routes.py`
  - `app/module/table/table_display/table_registry.py`

## 6. `permission` (`app/module/permission`)
- Blueprint prefix: `/permissions`
- Endpoints:
  - `POST /permissions/query`
  - `POST /permissions`
  - `PUT /permissions/<permission_id>`
- Key files:
  - `app/module/permission/permission_routes.py`
  - `app/module/permission/permission_service.py`
  - `app/module/permission/permission_repository.py`
  - `app/shared/schemas/permission_schema.py`
  - `app/shared/model/permission.py`

## 7. `user` (`app/module/user`)
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
  - `app/module/user/user_repository.py`
  - `app/shared/schemas/user_schema.py`
  - `app/shared/model/user.py`
  - `app/shared/model/user_permission.py`

## 8. `table-display` (`app/module/table/table_display`)
- Purpose: internal table layout/data generation used by `/tables/*` endpoints.
- Key files:
  - `app/module/table/table_display/table_registry.py`
  - `app/module/table/table_display/schema/table_schema.py`
  - `app/module/table/table_display/output_table_class/output_table_1_class/__init__.py`
  - `app/module/table/table_display/output_table_class/output_table_2_class/__init__.py`
  - `app/module/table/table_display/output_table_class/output_table_3_class/__init__.py`
  - `app/module/table/table_display/output_table_class/output_table_4_class/__init__.py`
  - `app/module/table/table_display/output_table_class/shared/convert_to_json_layout.py`
  - `app/module/table/table_display/output_table_class/shared/convert_to_json_data.py`
