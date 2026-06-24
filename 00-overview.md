# 00 — 项目总览 & 环境搭建

> **目标**: Trae AI 读完后能理解项目全貌，搭好开发环境，开始写代码。
> **前置**: 阅读方案书 `windemiko-portal-design.md`（同目录）。
> **仓库**: `FwindEmiko-Web`（汐汐酱已在 GitHub 创建）。

---

## 1. 项目一句话

**个人博客 + MC 资源展示 + 文件下载站 + AI 对话，Nuxt3 + FastAPI + MySQL，前后端分离。**

---

## 2. 技术决策速查

| 层 | 选型 | 不能改 |
|----|------|--------|
| 后端框架 | FastAPI (Python 3.12+) | ✅ |
| ORM | SQLAlchemy 2.0 async | ✅ |
| 数据库 | MySQL 8.0（生产）/ SQLite（开发） | 必须支持 PostgreSQL 切换 |
| 迁移 | Alembic | ✅ |
| 认证 | fastapi-users + PyJWT | ✅ |
| 前端公网 | Nuxt 3（SSR/SSG） | ✅ |
| 前端管理 | Vue 3 + Vite（独立 SPA, CSR） | ✅ |
| CSS | TailwindCSS 4 | ✅ |
| UI 组件 | Element Plus | 可用 Naive UI 替代如果更顺手 |
| 图标 | Lucide Vue Next | 可用 heroicons 替代 |
| 编辑器 | Vditor（管理后台） | ✅ |
| 包管理 | pnpm | ✅ |
| 容器化 | Docker Compose | ✅ |
| Web 服务器 | Nginx | ✅ |

---

## 3. Monorepo 目录结构

```
FwindEmiko-Web/
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── middleware.py
│   │   ├── exceptions.py
│   │   ├── modules/          # 按领域拆模块
│   │   │   ├── auth/
│   │   │   ├── blog/
│   │   │   ├── resources/
│   │   │   ├── downloads/
│   │   │   ├── chat/
│   │   │   └── files/
│   │   └── core/
│   │       ├── security.py
│   │       ├── pagination.py
│   │       └── events.py
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── nuxt-app/                 # Nuxt 3 公网站点（SSR/SSG）
│   ├── pages/
│   ├── components/
│   ├── composables/
│   ├── stores/
│   ├── server/               # BFF 层（API 代理）
│   ├── assets/
│   │   └── live2d/           # Mao 模型文件
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── admin-spa/                # Admin SPA（CSR only）
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/
│   │   ├── api/
│   │   ├── components/
│   │   └── views/
│   ├── vite.config.ts
│   └── package.json
│
├── packages/                 # 共享包
│   ├── shared/               # TypeScript 类型 + API 客户端
│   │   └── src/
│   │       ├── types/
│   │       ├── api/
│   │       └── index.ts
│   └── ui/                   # 共享 UI 组件（可选）
│       └── src/
│           ├── glass/        # Glassmorphism 组件
│           └── icons/
│
├── docs/                     # 开发者文档（这些文件）
├── scripts/
├── docker-compose.yml
├── docker-compose.dev.yml
├── nginx.conf
├── .env.example
├── Makefile
├── pnpm-workspace.yaml
└── README.md
```

---

## 4. 环境搭建（Trae 执行）

### 4.1 前置依赖

```bash
# 确认安装
python --version     # ≥ 3.12
node --version       # ≥ 20
pnpm --version       # ≥ 9
docker --version     # ≥ 26
docker compose version
```

### 4.2 初始化 Monorepo

```bash
git clone git@github.com:FwindEmiko/FwindEmiko-Web.git
cd FwindEmiko-Web

# pnpm workspace 配置
cat > pnpm-workspace.yaml << 'EOF'
packages:
  - 'nuxt-app'
  - 'admin-spa'
  - 'packages/*'
EOF
```

### 4.3 后端 Python 环境

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

cat > pyproject.toml << 'EOF'
[project]
name = "windemiko-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi[standard]>=0.115",
    "uvicorn[standard]>=0.34",
    "sqlalchemy[asyncio]>=2.0",
    "aiomysql>=0.2",
    "asyncpg>=0.30",       # PostgreSQL 备用
    "alembic>=1.14",
    "fastapi-users[sqlalchemy]>=14",
    "python-jose[cryptography]>=3.3",
    "passlib[bcrypt]>=1.7",
    "python-multipart>=0.0.18",
    "httpx>=0.28",
    "pydantic-settings>=2.7",
    "aiofiles>=24.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.24",
    "httpx>=0.28",
]
mysql = ["aiomysql>=0.2"]
postgresql = ["asyncpg>=0.30"]
EOF

pip install -e ".[dev,mysql,postgresql]"
```

### 4.4 前端环境

```bash
# 共享包
mkdir -p packages/shared/src/{types,api}
cat > packages/shared/package.json << 'EOF'
{
  "name": "@windemiko/shared",
  "version": "0.1.0",
  "type": "module",
  "main": "./src/index.ts",
  "types": "./src/index.ts"
}
EOF

# Nuxt 3 公网站点
npx nuxi@latest init nuxt-app
cd nuxt-app
pnpm add @element-plus/nuxt @pinia/nuxt lucide-vue-next
pnpm add -D tailwindcss @tailwindcss/vite
# 手动添加 packages/shared 的 workspace 依赖

# Admin SPA
npm create vite@latest admin-spa -- --template vue-ts
cd admin-spa
pnpm add vue-router pinia element-plus lucide-vue-next axios
pnpm add -D tailwindcss @tailwindcss/vite
```

### 4.5 Docker 开发环境（数据库）

```yaml
# docker-compose.dev.yml
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: devpassword
      MYSQL_DATABASE: windemiko_dev
    ports: ['3306:3306']
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    volumes: [dev_mysql:/var/lib/mysql]

  # PostgreSQL 备选（需要时取消注释）
  # postgres:
  #   image: postgres:16-alpine
  #   environment:
  #     POSTGRES_PASSWORD: devpassword
  #     POSTGRES_DB: windemiko_dev
  #   ports: ['5432:5432']
  #   volumes: [dev_pg:/var/lib/postgresql/data]

volumes:
  dev_mysql:
```

```bash
docker compose -f docker-compose.dev.yml up -d mysql
```

---

## 5. 关键约定（Trae 请遵守）

### 5.1 代码风格

- **Python**: 遵循 PEP 8，用 `ruff` 格式化
- **TypeScript**: 严格模式，ESLint + Prettier
- **注释**: 中文注释在文件头说明模块用途，关键函数用英文 docstring
- **命名**: 
  - Python: `snake_case` 文件和函数，`PascalCase` 类
  - TypeScript: `camelCase` 变量/函数，`PascalCase` 组件和类

### 5.2 API 约定

- 所有 API 返回统一格式: `{"code": 0, "data": ..., "message": "ok"}`
- 分页: `{"items": [], "total": N, "page": 1, "size": 20, "pages": M}`
- 认证: `Authorization: Bearer <jwt>`
- 错误码: `0` 成功, `401` 未认证, `403` 无权限, `404` 不存在, `422` 参数错误, `500` 服务端错误

### 5.3 TailwindCSS + Element Plus 共存

- TailwindCSS 负责布局、间距、玻璃磨砂、自定义颜色
- Element Plus 负责表单、表格、弹窗、菜单等交互组件
- 冲突处理: Element Plus 的 `ElButton` 等组件用 Tailwind 类名覆盖样式

### 5.4 灵活性原则

以下是**不能改**的硬约束，其他都可以根据实际情况调整：

| 硬约束 | 原因 |
|--------|------|
| FastAPI + SQLAlchemy async | 方案决策 |
| Nuxt3 + Admin SPA 分离 | 方案决策 |
| MySQL 默认，必须可切换 PostgreSQL | 未来迁移 |
| API 统一响应格式 | 前端依赖 |
| JWT 认证 | 前后端分离 |
| RBAC 四角色 | 权限需求 |
| 数据库表结构（核心表） | 详细文档约定 |

**可以灵活调整的**:
- 具体实现模式（repository/service 层是否拆分）
- 三方库选择（如 fastapi-users 的替代方案）
- 组件拆分粒度
- CSS 实现方式（Tailwind 插件 vs 原生 CSS）
- 目录结构微调

---

## 6. 开发顺序（建议）

```
1. backend/app/config.py          # 配置管理
2. backend/app/database.py        # 数据库引擎
3. backend/app/core/security.py   # 密码哈希 + JWT
4. backend/app/modules/auth/      # 用户认证模块
5. backend/app/modules/blog/      # 博客模块
6. backend/app/modules/resources/ # MC 资源模块
7. backend/app/modules/downloads/ # 下载站模块
8. backend/app/modules/chat/      # AI 对话模块（占位）
9. backend/app/modules/files/     # 文件存储模块
10. packages/shared/              # 共享类型 + API 客户端
11. nuxt-app/                     # 公网站点
12. admin-spa/                    # 管理后台
13. Live2D 集成
14. Docker 完整编排
```

---

## 7. 环境变量 (`.env.example`)

```env
# === 数据库 ===
# 开发: sqlite+aiosqlite:///./dev.db
# MySQL: mysql+aiomysql://root:pass@localhost:3306/windemiko_dev
DATABASE_URL=mysql+aiomysql://root:devpassword@127.0.0.1:3306/windemiko_dev

# === JWT ===
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440

# === 文件上传 ===
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=524288000

# === LLM (预留，暂不集成) ===
OLLAMA_BASE_URL=http://localhost:11434
LLM_BACKEND=none

# === CORS ===
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# === 应用 ===
APP_NAME=WindEmiko Portal
DEBUG=true
```

---

> **下一份**: `01-backend-core.md` — FastAPI 骨架 + 数据库引擎 + 认证模块
