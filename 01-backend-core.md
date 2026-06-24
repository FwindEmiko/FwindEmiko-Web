# 01 — Backend Core: 骨架 + 数据库 + 认证

> **依赖**: `00-overview.md`  
> **目标**: FastAPI 入口、数据库引擎、用户注册/登录/JWT 全链路跑通  
> **验证**: `POST /api/auth/register` 能创建用户，`POST /api/auth/login` 返回 JWT

---

## 1. 数据库引擎 (`backend/app/database.py`)

要求：
- 异步 SQLAlchemy 2.0 引擎
- 支持 SQLite / MySQL / PostgreSQL 三种 `DATABASE_URL`
- 提供 `get_db` 依赖注入（FastAPI Depends）

要点：
- 使用 `create_async_engine` + `async_sessionmaker`
- 自动检测 URL scheme：`sqlite` → `aiosqlite`，`mysql` → `aiomysql`，`postgresql` → `asyncpg`
- Session 生命周期用 FastAPI 依赖 yield 模式保证自动关闭

---

## 2. 配置管理 (`backend/app/config.py`)

```python
# 关键配置项
class Settings(BaseSettings):
    DATABASE_URL: str       # 完整数据库连接串
    JWT_SECRET: str         # JWT 签名密钥
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440    # 24h
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 524288000           # 500MB
    CORS_ORIGINS: list[str] = ["*"]
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env")
```

---

## 3. FastAPI 入口 (`backend/app/main.py`)

要求：
- CORS 中间件
- 统一异常处理（`@app.exception_handler`）
- 各模块路由注册
- Lifespan: 启动时创建数据库表，关闭时清理连接

```python
# 建议结构
app = FastAPI(title="WindEmiko Portal API", version="0.1.0")

# 中间件注册顺序: CORS → 限流 → 日志
# 异常处理: 统一返回 {"code": xxx, "message": "..."}
# 路由注册: app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
```

---

## 4. 安全模块 (`backend/app/core/security.py`)

```python
# 需要实现:
def hash_password(password: str) -> str:        # bcrypt
def verify_password(plain: str, hashed: str):   # bcrypt
def create_access_token(data: dict) -> str:      # JWT encode
def create_refresh_token(data: dict) -> str:     # JWT encode
def decode_token(token: str) -> dict:            # JWT decode + 过期校验
```

---

## 5. 认证模块 (`backend/app/modules/auth/`)

### 5.1 数据模型 (`models.py`)

```python
# User 表（SQLAlchemy 模型）
class User(Base):
    __tablename__ = "users"
    id: int (PK)
    username: str (unique, indexed)
    email: str (unique)
    password_hash: str
    display_name: str (nullable, 自定义昵称)
    avatar_url: str (nullable)
    bio: str (nullable, Markdown)
    role: str (default "member")      # admin / author / member
    is_active: bool (default True)
    is_verified: bool (default False)
    created_at: datetime
    updated_at: datetime
```

### 5.2 API 端点 (`router.py`)

```
POST   /api/auth/register
  body: {username, email, password, display_name?}
  逻辑: 校验唯一性 → hash 密码 → 创建用户 → 返回 tokens
  注意: username 3-30字符, email 格式校验, password ≥ 8字符

POST   /api/auth/login
  body: {username, password}
  逻辑: 查用户 → verify 密码 → 返回 tokens + user info

POST   /api/auth/refresh
  body: {refresh_token}
  逻辑: decode → 验证有效期 → 返回新 access_token

GET    /api/auth/me          (需 Bearer Token)
  返回当前用户信息

PUT    /api/auth/me          (需 Bearer Token)
  body: {display_name?, bio?, avatar_url?}
  更新个人信息

POST   /api/auth/me/avatar   (需 Bearer Token)
  multipart/form-data, 文件上传
  限制: ≤ 2MB, 仅图片格式
```

### 5.3 依赖注入 (`dependencies.py`)

```python
# 两个关键注入，供其他模块使用
async def get_current_user(token: str = Depends(oauth2_scheme), 
                           db = Depends(get_db)) -> User:
    """从 JWT 解析用户，查库返回 User 对象。失败抛 401。"""

def require_role(*roles: str):
    """返回一个依赖，检查当前用户是否属于指定角色。失败抛 403。"""
    # 用法: @app.get("/protected", dependencies=[Depends(require_role("admin"))])
```

---

## 6. 数据库迁移

```bash
cd backend
alembic init alembic
# 配置 alembic/env.py:
#   target_metadata = Base.metadata  # 从 models 导入
#   使用异步引擎
alembic revision --autogenerate -m "init: users table"
alembic upgrade head
```

Alembic 需支持异步——在 `env.py` 中用 `run_async_migrations`。

---

## 7. 验证方式

```bash
# 1. 启动后端
cd backend
uvicorn app.main:app --reload

# 2. 访问 Swagger 文档
open http://localhost:8000/docs

# 3. 注册
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test1234"}'

# 4. 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test1234"}'
# 应返回 {"code":0,"data":{"access_token":"eyJ...","refresh_token":"...","user":{...}}}

# 5. 测试受保护接口
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 8. 灵活性留白

- `fastapi-users` 库如果觉得太重或不够灵活，可以手写认证逻辑（参考本表的 API 端点规格即可）
- `User.role` 字段可以用字符串枚举或关联表，只要前端能读到 `role` 属性
- 头像存储在本地文件系统，可后续换成 OSS URL
- 邮件验证（`is_verified`）字段保留，逻辑可后续实现
- JWT 的 `sub` claim 建议存 `user.id`，`role` 也编码进 payload 方便中间件校验

---

> **下一份**: `02-blog-module.md` — 博客 CRUD + 分类标签
