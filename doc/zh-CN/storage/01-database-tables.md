# 数据库表结构

先读 [00-storage-catalog.md](./00-storage-catalog.md) 和 [../01-overview.md](../01-overview.md) 获取系统背景，再使用本文件作为数据库表结构参考。

## 1. 概览

- 数据库 schema：`py_mgmt_test`
- ORM 模型位置：`app/shared/model/`
- 时间戳默认值使用 `app/shared/utils/time.py::now_utc0`
- 每张表都有 `created_at`
- 当前只有 `user` 和 `permission` 具有 `updated_at`
- 当前由 ORM 定义的表：
  - `user`
  - `permission`
  - `user_permission`
  - `notifications`
  - `audit_log`
- `user` 与 `user_permission`、`notifications` 都是一对多关系。
- `permission` 与 `user_permission` 是一对多关系。
- `user_permission` 是 `user` 和 `permission` 之间的关联表。
- `audit_log` 当前只是保存 `user_id` 整数字段；模型里没有为它定义外键或 ORM 关系。

## 2. 表

### 2.1 `user`

- 模型来源：`app/shared/model/user.py`
- 用途：应用用户账号

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `user_id` | integer | 主键，自增 |
| `username` | string(50) | 必填，唯一 |
| `email` | string(100) | 必填 |
| `password_hash` | string(255) | 必填 |
| `is_active` | boolean | 默认值为 `True` |
| `created_at` | datetime | 必填，默认 `now_utc0` |
| `updated_at` | datetime | 必填，默认 `now_utc0`，更新行时自动更新 |

### 2.2 `permission`

- 模型来源：`app/shared/model/permission.py`
- 用途：模块/动作权限定义

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `permission_id` | integer | 主键，自增 |
| `module` | string(50) | 必填 |
| `action` | string(30) | 必填 |
| `description` | string(100) | 可选 |
| `is_active` | boolean | 默认值为 `True` |
| `created_at` | datetime | 必填，默认 `now_utc0` |
| `updated_at` | datetime | 必填，默认 `now_utc0`，更新行时自动更新 |

### 2.3 `user_permission`

- 模型来源：`app/shared/model/user_permission.py`
- 用途：用户与权限的关联关系

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键，自增 |
| `user_id` | integer | 必填，外键指向 `py_mgmt_test.user.user_id` |
| `permission_id` | integer | 必填，外键指向 `py_mgmt_test.permission.permission_id` |
| `created_at` | datetime | 必填，默认 `now_utc0` |

### 2.4 `notifications`

- 模型来源：`app/shared/model/notification.py`
- 用途：按用户存储通知记录

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键，自增 |
| `user_id` | integer | 必填，外键指向 `py_mgmt_test.user.user_id` |
| `message` | string(500) | 必填 |
| `is_read` | boolean | 必填，默认值为 `False` |
| `created_at` | datetime | 必填，默认 `now_utc0` |

### 2.5 `audit_log`

- 模型来源：`app/shared/model/audit_log.py`
- 用途：审计事件记录

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | integer | 主键，自增 |
| `user_id` | integer | 必填，模型中只是普通整数字段，没有外键 |
| `ip` | string(45) | 可选 |
| `device` | string(255) | 可选 |
| `created_at` | datetime | 必填，默认 `now_utc0` |
| `module` | string(100) | 可选 |
| `action` | string(100) | 可选 |
| `details` | text | 可选 |
