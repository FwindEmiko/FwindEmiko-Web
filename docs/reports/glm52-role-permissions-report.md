# GLM 5.2 · 角色权限系统升级报告

**日期**: 2026-06-25
**任务**: 角色权限系统升级（注册角色绑定 + 细粒度权限模型 + Admin 权限管理界面）

---

## 修改文件清单

### 后端（Backend）

#### 1. 注册接口绑定 .env
- [backend/app/config.py](file:///f:/FCelestial/fwe-repo/backend/app/config.py)
  - 新增 `REGISTER_DEFAULT_ROLE: str = "member"` 配置项
- [backend/app/modules/auth/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/auth/router.py)
  - 新增 `_REGISTERABLE_ROLES = {"member", "author", "moderator"}` 常量
  - 新增 `_resolve_register_role()` 函数，从 `settings.REGISTER_DEFAULT_ROLE` 读取角色，非法值回退为 member
  - `register` 接口的 `role` 字段从硬编码 `"member"` 改为调用 `_resolve_register_role()`
- [.env.prod.example](file:///f:/FCelestial/fwe-repo/.env.prod.example)
  - 新增 `REGISTER_DEFAULT_ROLE=member` 配置项及说明

#### 2. RolePermission 模型 + Alembic 迁移
- [backend/app/modules/auth/models.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/auth/models.py)
  - 新增 `ROLE_PERMISSION_FIELDS` 常量（22 个权限字段名清单）
  - 新增 `RolePermission` 模型，包含：
    - 文章权限（6 项：创建/编辑自己的/删除自己的/发布/编辑他人的/删除他人的）
    - 资源权限（6 项：同上）
    - 文件权限（4 项：上传/下载/删除/管理文件夹）
    - 分类标签（2 项：管理分类/管理标签）
    - 用户管理（2 项：查看用户/管理用户）
    - AI 对话（can_use_chat + chat_daily_limit）
    - 管理员（can_access_admin）
    - 时间戳（created_at / updated_at）
- [backend/alembic/versions/c3d4e5f6a7b8_add_role_permissions.py](file:///f:/FCelestial/fwe-repo/backend/alembic/versions/c3d4e5f6a7b8_add_role_permissions.py)
  - 新建迁移文件，`down_revision = 'b2c3d4e5f6a7'`
  - `upgrade()` 创建 `role_permissions` 表，包含全部权限列 + 唯一索引
  - `downgrade()` 删除表
- [backend/alembic/env.py](file:///f:/FCelestial/fwe-repo/backend/alembic/env.py)
  - 导入 `RolePermission` 以确保 Alembic autogenerate 能识别
- [backend/app/main.py](file:///f:/FCelestial/fwe-repo/backend/app/main.py)
  - 导入 `RolePermission` 模型
  - `lifespan` 启动钩子中调用 `ensure_role_permissions(session)`

#### 3. seed.py 预置角色权限
- [backend/app/seed.py](file:///f:/FCelestial/fwe-repo/backend/app/seed.py)
  - 新增 `_PRESET_ROLE_PERMISSIONS` 列表，定义 5 个预置角色：
    - **admin**: 全部权限 True，chat_daily_limit=9999
    - **author**: 文章/资源 CRUD（只限自己），可发布，可管理标签，聊天无限
    - **moderator**: author 权限 + 可编辑他人文章/资源 + 可删除文件 + 管理文件夹 + 管理分类 + 查看用户
    - **member**: 可下载文件，可聊天（20条/天）
    - **guest**: 仅下载公开文件，聊天 5条/天
  - 新增 `ensure_role_permissions()` 函数：幂等插入缺失角色行，admin 行强制保持全部 True

#### 4. Permissions 依赖类
- [backend/app/modules/auth/permissions.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/auth/permissions.py)（新建）
  - `load_role_permission()`: 从 DB 加载指定角色的权限行
  - `Permissions` 类：单次请求内的权限检查器
    - `can(action)`: 检查权限（admin 永远 True，未配置角色回退到基础权限）
    - `require(action)`: 检查权限，失败抛 403
  - `get_permissions`: 加载当前用户权限检查器（要求已登录）
  - `get_permissions_optional`: 同上但未登录不抛 401（按 guest 判断）
  - `require_permission(action)`: 生成 FastAPI 依赖，要求已登录 + 指定权限
  - `require_permission_optional(action)`: 同上但未登录按 guest 判断

#### 5. 路由权限替换
- [backend/app/modules/blog/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/blog/router.py)
  - `create_post`: `require_role("admin","author")` → `require_permission("can_create_post")`
  - `create_post` 内额外检查：直接发布需 `can_publish_post`
  - `update_post`: 自己的文章需 `can_edit_own_post`，他人的需 `can_edit_others_post`
  - `update_post` 状态变更：归档文章需 `can_edit_others_post` 才能改状态，草稿转发布需 `can_publish_post`
  - `delete_post`: 自己的文章需 `can_delete_own_post`，他人的需 `can_delete_others_post`
  - `create_category` / `update_category` / `delete_category`: `require_permission("can_manage_categories")`
  - `create_tag` / `delete_tag`: `require_permission("can_manage_tags")`
- [backend/app/modules/resources/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/resources/router.py)
  - `create_resource`: `require_permission("can_create_resource")`
  - `update_resource`: 需 `can_edit_own_resource` 或 `can_edit_others_resource`，发布需 `can_publish_resource`
  - `delete_resource`: `require_permission("can_delete_others_resource")`
  - `create_version`: `require_permission("can_create_resource")`
  - `update_version`: `require_permission("can_edit_own_resource")`
  - `delete_version`: `require_permission("can_delete_others_resource")`
  - `upload_screenshots`: `require_permission("can_create_resource")`
  - `reorder_screenshots` / `delete_screenshot`: `require_permission("can_edit_own_resource")`
- [backend/app/modules/downloads/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/downloads/router.py)
  - `download_file`: 新增 `require_permission_optional("can_download_file")` 全局权限检查 + 文件夹级 `can_download` 检查
  - `create_folder` / `update_folder` / `delete_folder`: `require_permission("can_manage_folders")`
  - `upload_files`: `require_permission("can_upload_file")` + 文件夹级 `can_upload`
  - `delete_file`: `get_permissions_optional` + 手动检查 `can_delete_file` + 文件夹级 `can_delete`
  - `get_permission_matrix` / `update_permission_matrix`: `require_permission("can_manage_folders")`
- [backend/app/modules/admin/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/admin/router.py)
  - `admin_stats`: `require_permission("can_access_admin")`
  - `list_users`: `require_permission("can_view_users")`
  - `update_user_role` / `update_user_status`: `require_permission("can_manage_users")`
  - `update_user_role` 角色白名单新增 `moderator`
  - `admin_list_posts`: 需登录 + `get_permissions`，无 `can_edit_others_post` 只能看自己的
  - `admin_get_post`: 非作者本人需 `can_edit_others_post`
  - `admin_list_resources` / `admin_get_resource`: `require_permission("can_access_admin")`
- [backend/app/modules/files/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/files/router.py)
  - `upload_files`: `require_role("admin","author")` → `require_permission("can_upload_file")`
- [backend/app/modules/chat/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/chat/router.py)
  - 仅清理未使用的 `require_role` 导入（聊天模块的 quota 逻辑保持不变）

#### 6. Admin API
- [backend/app/modules/auth/role_schemas.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/auth/role_schemas.py)（新建）
  - `RolePermissionOut`: 单个角色权限响应模型
  - `RolePermissionUpdateItem`: 批量保存时的单条更新项
  - `RolePermissionBatchUpdate`: 批量保存请求体
  - `RolePermissionCreate`: 新建角色请求体（role 名正则校验 `^[a-z0-9_]+$`）
- [backend/app/modules/admin/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/admin/router.py) 末尾追加
  - `GET /api/admin/role-permissions`: 返回全部角色权限矩阵（admin 行强制全开）
  - `PUT /api/admin/role-permissions`: 批量保存（admin 行忽略不修改）
  - `POST /api/admin/role-permissions`: 新建角色（admin 角色不允许创建）

### 前端（Admin SPA）

- [admin-spa/src/views/PermissionManagerView.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/views/PermissionManagerView.vue)（重写）
  - 布局：左侧角色列表 + 右侧权限分组卡片（响应式 md:flex-row）
  - 角色列表：admin/author/moderator/member/guest + 自定义角色，admin 显示锁图标
  - 权限分组（7 组卡片，2 列网格）：
    - 📝 文章权限（6 项 Switch）
    - 📦 资源权限（6 项 Switch）
    - 📁 文件权限（4 项 Switch）
    - 🏷️ 分类标签（2 项 Switch）
    - 👤 用户管理（2 项 Switch）
    - 🤖 AI 对话（1 项 Switch + 每日限额 InputNumber）
    - 🔧 后台（1 项 Switch）
  - admin 角色：全部 Switch 禁用，顶部显示"管理员角色拥有全部权限且不可修改"提示
  - 顶部操作栏：新建角色 / 刷新 / 保存当前角色权限
  - 新建角色对话框：role 名正则校验（小写字母+数字+下划线）

---

## 验证结果

### 后端 Python 语法检查
```
All Python files parse OK
```
（14 个文件全部通过 ast.parse）

### Admin SPA 构建
```
✓ built in 8.67s
```
（TypeScript 类型检查 + Vite 构建全部通过）

---

## 部署步骤

1. **后端迁移**（必须）：
   ```bash
   cd backend
   alembic upgrade head
   ```
   或重启后端容器（lifespan 会调用 `Base.metadata.create_all` 自动建表，但 Alembic 迁移更规范）

2. **后端重启**：使 `ensure_role_permissions` 种子数据生效，插入 5 个预置角色行

3. **Admin SPA 部署**：`pnpm build` 产物已生成，部署到 `admin-spa/dist`

4. **环境变量**（可选）：在 `.env` 中设置 `REGISTER_DEFAULT_ROLE=member`（或其他允许值）

---

## 权限矩阵预览

| 权限 | admin | author | moderator | member | guest |
|------|-------|--------|-----------|--------|-------|
| 创建文章 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 编辑自己的文章 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 删除自己的文章 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 发布文章 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 编辑他人的文章 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 删除他人的文章 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 创建资源 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 编辑自己的资源 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 删除自己的资源 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 发布资源 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 编辑他人的资源 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 删除他人的资源 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 上传文件 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 下载文件 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 删除文件 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 管理文件夹 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 管理分类 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 管理标签 | ✅ | ✅ | ✅ | ❌ | ❌ |
| 查看用户 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 管理用户 | ✅ | ❌ | ❌ | ❌ | ❌ |
| 启用 AI 对话 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 每日对话限额 | 9999 | 9999 | 9999 | 20 | 5 |
| 可访问管理后台 | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 注意事项

1. **admin 角色保护**：admin 行的所有布尔权限在 `ensure_role_permissions` 和 `GET /role-permissions` 中强制保持 True，防止误锁导致系统不可用

2. **Resource 模型无 author_id**：当前 `Resource` 模型没有 `author_id` 字段，无法区分资源作者归属。`update_resource` 暂时统一要求 `can_edit_own_resource` 或 `can_edit_others_resource`。如需精细化区分，需为 `Resource` 添加 `author_id` 字段

3. **chat 模块未深度改造**：聊天模块的 `user.role != "admin"` quota 逻辑保持不变，仅清理了未使用的 `require_role` 导入。如需基于 `can_use_chat` 和 `chat_daily_limit` 进行权限控制，需进一步改造 `chat/router.py` 和 `chat/service.py`

4. **向后兼容**：旧的 `require_role()` 函数仍保留在 `auth/dependencies.py` 中，未被任何路由使用，可在确认无引用后删除
