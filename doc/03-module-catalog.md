# Module Catalog

Read [00-table-of-contents.md](./00-table-of-contents.md) first and [01-overview.md](./01-overview.md) for system context, then use this file as the feature index.

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

### `line_chart` (`app/module/line_chart`)
- Blueprint prefix: `/line-chart`
- Endpoints:
  - `POST /line-chart/history`
  - `GET /line-chart/stream` (SSE)
- Key files:
  - `app/module/line_chart/routes/line_chart_routes.py`
  - `app/module/line_chart/services/line_chart_service.py`
  - `app/module/line_chart/services/line_chart_stream_service.py`
  - `app/shared/schemas/line_chart_schema.py`
  - `app/module/line_chart/pickle_test/long_running_program_demo.py`

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
