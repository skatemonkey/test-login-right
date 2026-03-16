# 通用工程规范

先读本目录中的 [00-eng-std-catalog.md](./00-eng-std-catalog.md) 和 [../01-overview.md](../01-overview.md)，再用本文件作为人类与 AI 共同遵循的编码规范基准。

- 架构流向：
  - 结构：`core -> module -> shared`。
  - 依赖规则：较低层的功能层不得向上导入；`shared` 不得导入 `module`。
  - 请求流：`routes -> services -> shared`。
- 日期时间输出保持 `%Y-%m-%d %H:%M:%S`；数据库默认时间戳使用 `app/shared/utils/time.py::now_utc0`。
- 受保护接口使用 `@jwt_required()`；用户身份来自 `app/shared/utils/auth.py::current_user_id()`。
- 导入风格：内部导入统一使用绝对路径（`from app...`），不要使用相对导入（`from .` / `from ..`）。
- 行为模块（services / utils / stream）应使用命名空间导入，并通过该命名空间调用，确保源码归属明确。
  - 应当：`from app.module.notification import notification_service`，然后调用 `notification_service.create_notification(...)`。
  - 不要：`from app.module.notification.notification_service import create_notification`。
- Barrel export 规则：不要通过 package 的 `__init__.py` 导入；应直接从具体模块路径导入。
  - 应当：`from app.shared.repository.user import User`。
  - 不要：`from app.shared.repository import User`。
- 命名约定（项目特定）：
  - Pydantic / dataclass 字段：`camelCase`（例如 `userId`、`createdAt`、`pageSize`）。
  - 请求 / 响应 / 表格 JSON 的字段：`camelCase`。
  - 内部变量（参数、局部变量、辅助函数内部、绝大多数 `self` 属性）：`snake_case`。
  - 函数 / 方法：`snake_case`。
  - 类（含 ORM model）：`PascalCase`。
  - 常量：`UPPER_SNAKE_CASE`。
  - 模块 / 文件 / 包：`snake_case`。
  - `app/shared/repository` 下的 repository / 数据库层继续保持 snake_case 命名。
  - 例外：JWT query-string 参数保持 `access_token`，不要改成 `accessToken`。
