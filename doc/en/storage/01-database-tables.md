# Database Tables

Read [00-storage-catalog.md](./00-storage-catalog.md) first and [../01-overview.md](../01-overview.md) for system context, then use this file as the database table reference.

## 1. Overview

- Database schema: `py_mgmt_test`
- ORM model location: `app/shared/model/`
- Timestamp defaults use `app/shared/utils/time.py::now_utc0`
- `created_at` is present on every table
- `updated_at` currently exists on `user` and `permission` only
- Current ORM-backed tables:
  - `user`
  - `permission`
  - `user_permission`
  - `notifications`
  - `audit_log`
- `user` has one-to-many relationships with `user_permission` and `notifications`.
- `permission` has a one-to-many relationship with `user_permission`.
- `user_permission` is the join table between `user` and `permission`.
- `audit_log` currently stores `user_id` as a plain integer field; the model does not define a foreign key or ORM relationship for it.

## 2. Tables

### 2.1 `user`

- Source: `app/shared/model/user.py`
- Used for: application user accounts

| Column | Type | Notes |
| --- | --- | --- |
| `user_id` | integer | Primary key, auto-increment |
| `username` | string(50) | Required, unique |
| `email` | string(100) | Required |
| `password_hash` | string(255) | Required |
| `is_active` | boolean | Defaults to `True` |
| `created_at` | datetime | Required, defaults to `now_utc0` |
| `updated_at` | datetime | Required, defaults to `now_utc0`, updates on row update |

### 2.2 `permission`

- Source: `app/shared/model/permission.py`
- Used for: module/action permission definitions

| Column | Type | Notes |
| --- | --- | --- |
| `permission_id` | integer | Primary key, auto-increment |
| `module` | string(50) | Required |
| `action` | string(30) | Required |
| `description` | string(100) | Optional |
| `is_active` | boolean | Defaults to `True` |
| `created_at` | datetime | Required, defaults to `now_utc0` |
| `updated_at` | datetime | Required, defaults to `now_utc0`, updates on row update |

### 2.3 `user_permission`

- Source: `app/shared/model/user_permission.py`
- Used for: user-to-permission mappings

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer | Primary key, auto-increment |
| `user_id` | integer | Required, FK to `py_mgmt_test.user.user_id` |
| `permission_id` | integer | Required, FK to `py_mgmt_test.permission.permission_id` |
| `created_at` | datetime | Required, defaults to `now_utc0` |

### 2.4 `notifications`

- Source: `app/shared/model/notification.py`
- Used for: per-user notification records

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer | Primary key, auto-increment |
| `user_id` | integer | Required, FK to `py_mgmt_test.user.user_id` |
| `message` | string(500) | Required |
| `is_read` | boolean | Required, defaults to `False` |
| `created_at` | datetime | Required, defaults to `now_utc0` |

### 2.5 `audit_log`

- Source: `app/shared/model/audit_log.py`
- Used for: audit trail event records

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer | Primary key, auto-increment |
| `user_id` | integer | Required, plain integer field with no FK in the model |
| `ip` | string(45) | Optional |
| `device` | string(255) | Optional |
| `created_at` | datetime | Required, defaults to `now_utc0` |
| `module` | string(100) | Optional |
| `action` | string(100) | Optional |
| `details` | text | Optional |
