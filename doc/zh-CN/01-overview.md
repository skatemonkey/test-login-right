# 概览

先读 [00-doc-catalog.md](./00-doc-catalog.md)，再用本文件了解系统背景。下一步阅读 [engineering-standards/00-eng-std-catalog.md](./engineering-standards/00-eng-std-catalog.md) 和 [modules/00-module-catalog.md](./modules/00-module-catalog.md)。

## 1. 系统与环境

### 技术栈
- Python 3.13
- Flask API 栈：Flask、Flask-CORS、Flask-JWT-Extended、Flask-SQLAlchemy、Flask-Pydantic
- 数据与基础设施：MySQL（通过 PyMySQL）、Redis、`requests`
- 建模与校验：Pydantic
- 质量与测试：`unittest`、Ruff、isort

### 运行 / 构建 / 测试命令
```bash
pipenv install
pipenv run python app.py
pipenv run python -m unittest discover tests
pipenv run ruff check app tests
```

本项目没有单独的构建步骤。运行应用或测试前先安装依赖。启动时，`app/core/config.py` 会从远程配置 API 获取 MySQL 连接信息。实时流功能需要可访问的 Redis。

## 2. 系统架构

### 高层架构
- `app.py` 用于启动服务，`app/__init__.py::create_app()` 负责加载配置、初始化 JWT、数据库、CORS 和 Redis，并注册各个 blueprint。
- 仓库结构遵循 `core -> module -> shared`：
  - `core`：应用级基础设施与扩展初始化。
  - `module`：功能模块，例如 `auth`、`audit`、`notification`、`permission`、`user`、`table`、`line_chart`。
  - `shared`：跨功能复用的 repository、schema 和 utility。
- 常见请求流向是 `routes -> services -> shared`：
  - `routes`：处理 HTTP、鉴权装饰器和响应组装。
  - `services`：承载业务逻辑。
  - `shared`：提供 schema、repository 和跨功能公共工具。
- 新功能放在 `app/module/<feature>/` 下。排查请求时，先看 route，再看对应 service，最后看它依赖的 shared 部分。

### 文件结构
```text
app/
  core/
  module/
    auth/ audit/ notification/ permission/ user/ table/ line_chart/
  shared/
    repository/ schemas/ utils/
tests/
doc/
```
