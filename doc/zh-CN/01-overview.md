# 概览

先读 [00-doc-catalog.md](./00-doc-catalog.md)，再用本文件了解系统背景。下一步阅读 [engineering-standards/00-eng-std-catalog.md](./engineering-standards/00-eng-std-catalog.md) 和 [modules/00-module-catalog.md](./modules/00-module-catalog.md)。

## 1. 系统与环境

### 1.1 技术栈
- Python 3.13
- Flask API 栈：Flask、Flask-CORS、Flask-JWT-Extended、Flask-SQLAlchemy、Flask-Pydantic
- 数据与基础设施：MySQL（通过 PyMySQL）、Redis、`requests`
- 建模与校验：Pydantic
- 质量与测试：`unittest`、Ruff、isort

### 1.2 运行 / 构建 / 测试命令
```bash
pipenv install
pipenv run python app.py
pipenv run python -m unittest discover tests
pipenv run ruff check app tests
```

本项目没有单独的构建步骤。运行应用或测试前先安装依赖。启动时，`app/core/config.py` 会从远程配置 API 获取 MySQL 连接信息。实时流功能需要可访问的 Redis。

## 2. 系统架构

### 2.1 高层架构
- `app.py` 用于启动服务，`app/__init__.py::create_app()` 负责加载配置、初始化 JWT、数据库、CORS 和 Redis，并注册各个 blueprint。
- 仓库按三个主要 package 区域组织：
  - `core`：应用级基础设施、扩展初始化和基础设施客户端。
  - `module`：功能模块，例如 `auth`、`audit`、`notification`、`permission`、`user`、`table`、`line_chart`。
  - `shared`：
    - models：SQLAlchemy 表定义。
    - schemas：请求/响应模型（DTO）。
    - utilities：公共辅助函数。
- 当前依赖关系图为：
  ![Overview dependency graph](../-files/overview.png)
  - `app -> core`
  - `app -> module`
  - `module -> shared`
  - `module -> core`
  - `shared -> core`

- 面向数据库的模块常见请求流向是 `routes -> services -> repositories`：
  - `routes`：处理 HTTP、鉴权装饰器和响应组装。
  - `services`：承载业务逻辑。
  - `repositories`：负责数据库操作与查询。
- 面向数据库的模块通常采用扁平三件套：`*_routes.py`、`*_service.py` 和 `*_repository.py`。
- 本阶段的架构例外是 `line_chart` 与 `table`：它们使用非 SQL 访问模式，暂不纳入 repository 模式。
- 新功能放在 `app/module/<feature>/` 下。排查数据库模块请求时，先看 route，再看对应 service 与 repository 依赖；`shared` 中的 models、schemas 和 utilities 作为辅助上下文查看。

### 2.2 文件结构
```text
app/
  core/
  module/
    auth/ audit/ notification/ permission/ user/ table/ line_chart/
  shared/
    model/ schemas/ utils/
tests/
doc/
```
