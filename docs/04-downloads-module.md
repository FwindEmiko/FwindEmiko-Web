# 04 — 下载站模块 + RBAC 权限

> **依赖**: `01-backend-core.md`  
> **目标**: 虚拟文件树 + 文件 CRUD + 角色权限隔离 + 下载计数  
> **验证**: 不同角色用户看到不同的文件夹，未登录只能看公开区

---

## 1. 设计理念

**不暴露物理路径**。所有文件和文件夹存在于数据库的虚拟树中，物理文件存储在 `uploads/` 按 ID 组织。权限通过 `role` 和 `FolderPermission` 控制。

对标 OpenList 的核心能力：密码保护文件夹 → 换成角色权限；文件直链；上传到指定目录。

---

## 2. 数据模型 (`backend/app/modules/downloads/models.py`)

```python
class Folder(Base):
    __tablename__ = "folders"
    id: int (PK)
    name: str                           # 显示名称
    slug: str (unique)                  # URL 标识符
    parent_id: int (FK → folders.id, nullable)  # 树形结构
    description: str (nullable)         # Markdown, 文件夹说明/README
    is_visible: bool (default True)     # 在列表中是否可见
    sort_order: int (default 0)
    created_at: datetime
    updated_at: datetime

class FileNode(Base):
    __tablename__ = "files"
    id: int (PK)
    folder_id: int (FK → folders.id, ondelete CASCADE)
    filename: str                       # 原始文件名
    display_name: str (nullable)        # 显示名称（为空则用 filename）
    file_size: int (default 0)          # 字节
    file_hash: str (nullable)           # SHA-256
    mime_type: str (nullable)
    storage_path: str                   # 物理路径: uploads/downloads/{folder_id}/{id}_{filename}
    external_url: str (nullable)        # 第三方跳转链接
    download_count: int (default 0)
    created_at: datetime

class FolderPermission(Base):
    __tablename__ = "folder_permissions"
    id: int (PK)
    folder_id: int (FK → folders.id, ondelete CASCADE)
    role: str                           # admin / author / member / guest
    can_read: bool (default True)       # 能否看到文件列表
    can_download: bool (default False)  # 能否下载文件
    # 唯一约束: (folder_id, role)
```

### 默认权限规则（内置逻辑，不需要数据库记录）

| 角色 | 默认可见 | 默认可下载 |
|------|----------|-----------|
| `admin` | 全部 | 全部 |
| `author` | 全部（如果没设限制） | 全部 |
| `member` | 仅 `is_visible=True` 的文件夹 | 仅在 `FolderPermission` 中授权的 |
| `guest` (未登录) | 仅 `is_visible=True` + FolderPermission 中 role=guest 的 | 同上 |

特殊规则：如果文件夹没有任何 `FolderPermission` 记录 → 默认所有角色可读可下载（公开文件夹）。

---

## 3. API 端点

### 公开接口

```
GET  /api/downloads/folders
  说明: 返回当前用户有权看到的文件夹树
  逻辑:
    1. 识别用户角色（未登录 = guest）
    2. 遍历所有文件夹 → 根据角色和 FolderPermission 决定是否返回
    3. 返回嵌套 JSON 树结构
  返回: [{id, name, slug, description?, children: [...]}, ...]

GET  /api/downloads/folders/{id}/files
  说明: 获取文件夹下的文件列表 + 子文件夹
  返回: {
    folder: {...},                      # 当前文件夹信息 (含 description 作为 README)
    breadcrumbs: [{id, name}, ...],     # 面包屑导航
    subfolders: [{id, name, slug}, ...],
    files: [{id, filename, display_name, file_size, mime_type, download_count, has_external, created_at}, ...]
  }

GET  /api/downloads/files/{id}/download
  说明: 下载文件（触发计数）
  逻辑:
    1. 查文件 → 查文件夹 → 查权限
    2. 有外部链接? → 302 重定向
    3. 本地文件? → StreamingResponse + Content-Disposition: attachment
    4. download_count += 1
    5. 记录下载日志 (可选)
```

### 管理接口（需 admin 角色）

```
POST   /api/downloads/folders
  body: {name, slug?, parent_id?, description?, is_visible?, permission_rules?: [{role, can_read, can_download}]}

PUT    /api/downloads/folders/{id}
DELETE /api/downloads/folders/{id}
  逻辑: 如果文件夹非空（有文件或子文件夹）→ 提示确认或直接禁止

POST   /api/downloads/files
  body: multipart (多文件上传)
  query: ?folder_id=xxx
  逻辑: 保存到 uploads/downloads/{folder_id}/ → 创建 FileNode 记录
  进度: 前端实时进度条

DELETE /api/downloads/files/{id}
  逻辑: 删除物理文件 + 数据库记录
```

---

## 4. 权限检查函数

```python
# backend/app/modules/downloads/permission.py

async def check_folder_access(folder_id: int, user: User | None, action: str) -> bool:
    """
    action: "read" | "download"
    返回: True 如果有权限
    """
    role = user.role if user else "guest"
    # 1. admin 全权限
    if role == "admin":
        return True
    # 2. 查 FolderPermission
    perm = await db.query(FolderPermission)...where(folder_id, role)
    # 3. 如果无权限记录 → 公开文件夹（默认允许）
    # 4. 根据 action 返回 can_read 或 can_download
```

---

## 5. 文件管理器前端参考

基于 `n1crack/vuefinder` 的交互设计理念（不用照搬，参考其 UX）：

```
桌面端（左右分栏）          移动端（单栏）
┌──────┬──────────┐        ┌────────────────┐
│ 树   │ 面包屑    │        │ ← 返回上级      │
│      │ ──────── │        │ ────────────── │
│ 📁源  │ 文件名    │        │ 📁 子文件夹     │
│ ├插件 │ 大小     │        │ 📄 文件1.jar   │
│ ├模组 │ 时间     │        │ 📄 文件2.zip   │
│ └工具 │          │        │                │
│ 📁限  │          │        │                │
└──────┴──────────┘        └────────────────┘
```

关键交互：
- 右键菜单：下载 / 复制链接 / 删除（如有权限）
- 拖拽上传：拖文件到文件列表区域 → 自动识别目标文件夹
- 面包屑：每级可点击跳转
- 文件图标：根据 `mime_type` 或文件后缀显示不同图标（jar/zip/pdf/图片等）

---

## 6. 验证方式

```bash
# 创建公开文件夹
curl -X POST http://localhost:8000/api/downloads/folders \
  -H "Authorization: Bearer *** \
  -d '{"name":"公开资源","slug":"public","is_visible":true}'

# 创建受限文件夹
curl -X POST http://localhost:8000/api/downloads/folders \
  -H "Authorization: Bearer *** \
  -d '{"name":"VIP资源","slug":"vip","is_visible":true,"permission_rules":[{"role":"guest","can_read":false,"can_download":false},{"role":"member","can_read":true,"can_download":true}]}'

# 未登录查看 → 应该看不到 vip 文件夹
curl http://localhost:8000/api/downloads/folders

# 登录后查看 → member 能看到 vip
curl http://localhost:8000/api/downloads/folders \
  -H "Authorization: Bearer <member_toke...

## 7. 灵活性留白

- 权限规则粒度：当前是文件夹级别。如果未来需要文件级别权限，可以加 `FilePermission` 表，逻辑类似。
- 下载日志：当前只计数。如果需要详细记录（谁 + 什么时候 + 什么文件），加 `DownloadLog` 表。
- 文件预览：图片/PDF 可以直接在新标签页打开。`.jar` / `.zip` 等二进制直接触发下载。
- 大文件上传：Multipart 有大小限制。如果要支持 GB 级文件，考虑分片上传（`tus` 协议或手动实现）。目前 500MB 上限对 MC 插件/模组已经足够。
- 文件夹树渲染：如果文件夹层级很深，前端用虚拟滚动优化（Nuxt3 可选 `@vueuse/core` 的 `useVirtualList`）。

---

> **下一份**: `05-chat-module.md` — AI 对话 API（LLM 占位）
