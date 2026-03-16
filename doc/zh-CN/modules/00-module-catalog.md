# 模块目录

先读 [../00-doc-catalog.md](../00-doc-catalog.md) 和 [../01-overview.md](../01-overview.md)，再使用本文件作为功能索引。

## 1. `auth` (`app/module/auth`)
- Blueprint 前缀：`/auth`
- 接口：
  - `POST /auth/login`
- 关键文件：
  - `app/module/auth/auth_routes.py`
  - `app/module/auth/auth_service.py`
  - `app/module/auth/auth_repository.py`
  - `app/shared/schemas/auth_schema.py`

## 2. `audit` (`app/module/audit`)
- Blueprint 前缀：`/audit`
- 接口：
  - `POST /audit/log`
  - `POST /audit/log/query`
- 关键文件：
  - `app/module/audit/audit_routes.py`
  - `app/module/audit/audit_service.py`
  - `app/module/audit/audit_repository.py`
  - `app/shared/schemas/audit_schema.py`
  - `app/shared/model/audit_log.py`

## 3. `notification` (`app/module/notification`)
- Blueprint 前缀：`/notifications`
- 接口：
  - `GET /notifications`
  - `PATCH /notifications/<notification_id>/read`
  - `PATCH /notifications/read-all`
  - `GET /notifications/unread-count`
  - `GET /notifications/stream` (SSE)
  - `POST /notifications/mock-approve`
- 关键文件：
  - `app/module/notification/notification_routes.py`
  - `app/module/notification/notification_service.py`
  - `app/module/notification/notification_repository.py`
  - `app/module/notification/notification_stream.py`
  - `app/shared/schemas/notification_schema.py`
  - `app/shared/model/notification.py`

## 4. `line_chart` (`app/module/line_chart`)
- Blueprint 前缀：`/line-chart`
- 当前例外：这是非 SQL 模块，本阶段不引入 repository 层。
- 接口：
  - `POST /line-chart/history`
  - `GET /line-chart/stream` (SSE)
- 关键文件：
  - `app/module/line_chart/routes/line_chart_routes.py`
  - `app/module/line_chart/services/line_chart_service.py`
  - `app/module/line_chart/services/line_chart_stream_service.py`
  - `app/shared/schemas/line_chart_schema.py`
  - `app/module/line_chart/pickle_test/long_running_program_demo.py`

## 5. `table` (`app/module/table`)
- Blueprint 前缀：`/tables`
- 当前例外：route 直接调用内部 table display 代码，本阶段不引入 repository 层。
- 接口：
  - `GET /tables/layout/<table_id>`
  - `GET /tables/data/<table_id>`
- 关键文件：
  - `app/module/table/table_routes.py`
  - `app/module/table/table_display/table_registry.py`

## 6. `permission` (`app/module/permission`)
- Blueprint 前缀：`/permissions`
- 接口：
  - `POST /permissions/query`
  - `POST /permissions`
  - `PUT /permissions/<permission_id>`
- 关键文件：
  - `app/module/permission/permission_routes.py`
  - `app/module/permission/permission_service.py`
  - `app/module/permission/permission_repository.py`
  - `app/shared/schemas/permission_schema.py`
  - `app/shared/model/permission.py`

## 7. `user` (`app/module/user`)
- Blueprint 前缀：`/users`
- 接口：
  - `POST /users/query`
  - `GET /users/permission-matrix`
  - `GET /users/<user_id>`
  - `POST /users`
  - `PUT /users/<user_id>`
  - `PUT /users/<user_id>/permissions/<permission_id>`
- 关键文件：
  - `app/module/user/user_routes.py`
  - `app/module/user/user_service.py`
  - `app/module/user/user_repository.py`
  - `app/shared/schemas/user_schema.py`
  - `app/shared/model/user.py`
  - `app/shared/model/user_permission.py`

## 8. `table-display` (`app/module/table/table_display`)
- 用途：供 `/tables/*` 接口使用的内部表格布局 / 数据生成模块。
- 关键文件：
  - `app/module/table/table_display/table_registry.py`
  - `app/module/table/table_display/schema/table_schema.py`
  - `app/module/table/table_display/output_table_class/output_table_1_class/__init__.py`
  - `app/module/table/table_display/output_table_class/output_table_2_class/__init__.py`
  - `app/module/table/table_display/output_table_class/output_table_3_class/__init__.py`
  - `app/module/table/table_display/output_table_class/output_table_4_class/__init__.py`
  - `app/module/table/table_display/output_table_class/shared/convert_to_json_layout.py`
  - `app/module/table/table_display/output_table_class/shared/convert_to_json_data.py`
