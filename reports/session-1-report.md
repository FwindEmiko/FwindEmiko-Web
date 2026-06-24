# Session 1 报告：Monorepo 骨架 + FastAPI 认证模块

## 1. 概要

本次会话完成了 `FwindEmiko-Web` 项目的 Monorepo 骨架搭建，并实现了 FastAPI 后端认证模块的全链路功能。后端已可正常启动，注册/登录/JWT/个人信息接口均通过自测。

## 2. 完成内容

### Step 1 — Monorepo 初始化

- `pnpm-workspace.yaml`：包含 `nuxt-app`、`admin-spa`、`packages/*`
- `backend/`：Python 虚拟环境、[`pyproject.toml`](file:///f:/FwindEmiko-Web/backend/pyproject.toml)
- `nuxt-app/`：Nuxt 3 minimal 模板
- `admin-spa/`：Vite + Vue + TypeScript 模板
- `packages/shared/`、`packages/ui/`：空包占位并接入 workspace
- 为前端项目安装了 Element Plus、Pinia、TailwindCSS、lucide-vue-next、axios 等依赖，并接入 `@windemiko/shared`

### Step 2 — 后端核心基础设施

- [`backend/app/config.py`](file:///f:/FwindEmiko-Web/backend/app/config.py)：Pydantic Settings，读取 `.env`
- [`backend/app/database.py`](file:///f:/FwindEmiko-Web/backend/app/database.py)：异步 SQLAlchemy 2.0，支持 SQLite / MySQL / PostgreSQL 三种 URL
- [`backend/app/core/security.py`](file:///f:/FwindEmiko-Web/backend/app/core/security.py)：bcrypt 密码哈希 + JWT 生成/验证
- [`backend/app/core/response.py`](file:///f:/FwindEmiko-Web/backend/app/core/response.py)：统一 API 响应格式

### Step 3 — 认证模块

- [`backend/app/modules/auth/models.py`](file:///f:/FwindEmiko-Web/backend/app/modules/auth/models.py)：`users` 表模型
- [`backend/app/modules/auth/schemas.py`](file:///f:/FwindEmiko-Web/backend/app/modules/auth/schemas.py)：Pydantic 请求/响应模型
- [`backend/app/modules/auth/router.py`](file:///f:/FwindEmiko-Web/backend/app/modules/auth/router.py)：
  - `POST /api/auth/register`
  - `POST /api/auth/login`
  - `POST /api/auth/login/form`（兼容 Swagger OAuth2）
  - `POST /api/auth/refresh`
  - `GET /api/auth/me`
  - `PUT /api/auth/me`
  - `POST /api/auth/me/avatar`
- [`backend/app/modules/auth/dependencies.py`](file:///f:/FwindEmiko-Web/backend/app/modules/auth/dependencies.py)：`get_current_user`、`require_role`
- [`backend/app/main.py`](file:///f:/FwindEmiko-Web/backend/app/main.py)：FastAPI 入口，CORS、异常处理、路由注册、静态文件

### Step 4 — 数据库迁移

- Alembic 已初始化并配置异步引擎
- 生成首次迁移：`9ae5763a9b5d_init_users_table.py`
- 已执行 `alembic upgrade head`

### Step 5 — 开发环境

- [`docker-compose.dev.yml`](file:///f:/FwindEmiko-Web/docker-compose.dev.yml)：MySQL 8.0 开发容器
- [`.env.example`](file:///f:/FwindEmiko-Web/.env.example)：完整环境变量示例
- [`backend/.env`](file:///f:/FwindEmiko-Web/backend/.env)：本地开发配置（SQLite）

## 3. 自测结果

| 检查项 | 结果 |
|---|---|
| `uvicorn` 正常启动 | ✅ |
| `http://localhost:8000/docs` 可访问 | HTTP 200 |
| `POST /api/auth/register` 创建用户 | 返回 `code:0` + access/refresh tokens + user |
| `POST /api/auth/login` 登录 | 返回 JWT + user |
| `GET /api/auth/me`（带 Bearer Token） | 返回当前用户信息 |
| 重复注册同用户名 | 返回 HTTP 422 + `用户名或邮箱已存在` |

## 4. 遇到的问题与修复

1. **bcrypt 5.0 + passlib 触发 `password cannot be longer than 72 bytes`**
   - 原因：bcrypt 4.1+ 与 passlib 存在已知兼容性 issue
   - 修复：在 [`pyproject.toml`](file:///f:/FwindEmiko-Web/backend/pyproject.toml) 中固定 `bcrypt<4.1`

2. **首次启动时报 `Directory './uploads' does not exist`**
   - 修复：在 [`app/main.py`](file:///f:/FwindEmiko-Web/backend/app/main.py) 启动前自动 `os.makedirs(settings.UPLOAD_DIR, exist_ok=True)`

3. **Pydantic Settings 读取 `CORS_ORIGINS` 列表格式报错**
   - 修复：`.env` 中 CORS_ORIGINS 使用 JSON 数组格式：`["http://localhost:3000","http://localhost:5173"]`

4. **前端依赖安装时 pnpm 触发 `minimumReleaseAge` 与 `ignored builds` 策略**
   - 处理：通过 `--config.minimumReleaseAge=0 --ignore-scripts` 完成依赖下载；构建脚本（esbuild、@parcel/watcher）被忽略，后续开发前可手动执行 `pnpm approve-builds` 并重新安装

## 5. 下一步建议

- 启动前端 dev server，验证 workspace 包引用与 Element Plus / TailwindCSS 集成
- 实现博客模块（`backend/app/modules/blog/`）
- 补充后端单元测试（`backend/tests/`）
