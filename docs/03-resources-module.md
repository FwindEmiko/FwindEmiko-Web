# 03 — MC 资源展示模块

> **依赖**: `01-backend-core.md`  
> **目标**: MC 插件/模组资源 CRUD + 多版本管理 + 截图 Gallery  
> **验证**: GET /api/resources 返回分类列表，GET /api/resources/{slug} 返回完整详情

---

## 1. 数据模型 (`backend/app/modules/resources/models.py`)

```python
class Resource(Base):
    __tablename__ = "resources"
    id: int (PK)
    title: str
    slug: str (unique, indexed)
    description: str                    # Markdown
    type: str                           # plugin / mod / datapack / tool
    game_versions: str                  # JSON 数组字符串: '["1.21.11","26.1.2"]'
    loaders: str                        # JSON: '["Paper","Spigot","Folia"]'
    icon_url: str (nullable)
    cover_url: str (nullable)           # 横幅大图
    download_count: int (default 0)     # 所有版本下载总和（用聚合计算或手动更新）
    status: str (default "draft")       # draft / published
    created_at: datetime
    updated_at: datetime

class ResourceVersion(Base):
    __tablename__ = "resource_versions"
    id: int (PK)
    resource_id: int (FK → resources.id, ondelete CASCADE)
    version_string: str                 # "v1.2.0" 或 "26.1.2-build3"
    changelog: str (nullable)           # Markdown
    file_url: str (nullable)            # 本站文件直链 (通过 /api/downloads/...)
    external_url: str (nullable)        # 第三方网盘链接
    file_size: int (nullable)           # 字节
    file_hash: str (nullable)           # SHA-256
    downloads: int (default 0)
    is_prerelease: bool (default False)
    created_at: datetime

class Screenshot(Base):
    __tablename__ = "screenshots"
    id: int (PK)
    resource_id: int (FK → resources.id, ondelete CASCADE)
    image_url: str
    caption: str (nullable)
    sort_order: int (default 0)         # 越小越靠前
```

### 字段说明

- `game_versions` 和 `loaders` 用 JSON 数组字符串存储，SQLAlchemy 存为 TEXT/JSON 列。在 schema 中自动转换 `list[str] ↔ str`。
- `download_count` 在 `Resource` 表冗余存储总下载次数，创建/删除版本时更新。
- `Screenshot.sort_order` 用于拖拽排序——管理后台每次调整排序后重新编号。

---

## 2. API 端点 (`backend/app/modules/resources/router.py`)

### 公开接口

```
GET  /api/resources
  query: ?page=1&size=20&type=plugin&version=1.21.11&loader=Paper&q=关键词&sort=downloads|newest
  说明: game_versions 用 LIKE 或 JSON_CONTAINS 匹配
  返回: {items: [{...resource, latest_version: {...}}], total, page, size, pages}

GET  /api/resources/{slug}
  返回: {
    resource,           # 基本信息
    versions: [...],    # 按 created_at DESC, 每个带下载 URL
    screenshots: [...], # 按 sort_order ASC
  }
```

### 认证接口（需 login + author/admin）

```
POST   /api/resources
  权限: author+
  body: {title, description, type, game_versions:[], loaders:[], icon_url?, cover_url?}

PUT    /api/resources/{id}
  权限: author/admin

DELETE /api/resources/{id}
  权限: admin
  逻辑: 级联删除 versions + screenshots + 关联文件

# === 版本 ===
POST   /api/resources/{id}/versions
  权限: author+
  body: {version_string, changelog?, file_url?, external_url?, file_size?, file_hash?, is_prerelease?}
  说明: file_url 和 external_url 至少有一个

PUT    /api/resources/{id}/versions/{version_id}
  权限: author/admin

DELETE /api/resources/{id}/versions/{version_id}
  权限: admin

# === 截图 ===
POST   /api/resources/{id}/screenshots
  权限: author+
  body: multipart (多文件上传) + captions[]
  说明: 上传后自动生成缩略图（建议宽 ≤ 1200px）

PUT    /api/resources/{id}/screenshots/reorder
  权限: author+
  body: {screenshot_ids: [3, 1, 2]}   # 新排序

DELETE /api/resources/{id}/screenshots/{shot_id}
  权限: author/admin
```

---

## 3. 截图处理

上传截图时：
1. 保存原图到 `uploads/screenshots/{resource_id}/`
2. 生成缩略图（宽 400px），存到 `uploads/screenshots/{resource_id}/thumb_`
3. 返回缩略图 URL 给前端列表展示，详情页加载原图

Python 图像处理: `Pillow` 或 `python-resize-image`

---

## 4. 统计更新

- 版本下载计数: 每次调用下载接口时 `downloads += 1`
- 资源总下载: 所有版本 downloads 之和 → 可实时聚合或定时更新
- 简单的做法: 下载时同时更新 `ResourceVersion.downloads` 和 `Resource.download_count`

---

## 5. 前端展示参考

资源详情页布局（参考 Modrinth/SpigotMC 设计模式）：

```
┌──────────────────────────────────────────────┐
│  [图标]  标题          类型徽标  版本标签      │
│          MC 1.21.x  Paper  Folia             │
├──────────────────────────────────────────────┤
│  [截图 Gallery - 横向滚动]                    │
│  ┌─────┐ ┌─────┐ ┌─────┐                    │
│  │ Img │ │ Img │ │ Img │                    │
│  └─────┘ └─────┘ └─────┘                    │
├──────────────────────────────────────────────┤
│  描述 (Markdown 渲染)                         │
│  ...正文...                                   │
├──────────────────────────────────────────────┤
│  版本历史 (倒序)                              │
│  v1.2.0 (最新)  [本地下载] [网盘下载]         │
│  v1.1.0         [本地下载]                    │
│  v1.0.0         [本地下载]                    │
└──────────────────────────────────────────────┘
```

---

## 6. 验证方式

```bash
# 创建资源
curl -X POST http://localhost:8000/api/resources \
  -H "Authorization: Bearer *** \
  -d '{"title":"SkyIslandHome","type":"plugin","game_versions":["1.21.11"],"loaders":["Paper"],"description":"空岛家园系统"}'

# 添加版本
curl -X POST http://localhost:8000/api/resources/skyislandhome/versions \
  -H "Authorization: Bearer *** \
  -d '{"version_string":"v1.2.0","external_url":"https://123pan.com/xxx"}'

# 查看详情
curl http://localhost:8000/api/resources/skyislandhome
```

---

## 7. 灵活性留白

- `game_versions` 和 `loaders` 的 JSON 存储方式如果觉得别扭，可以拆成关联表。但 JSON 列查询简单（`JSON_CONTAINS`），对数据量不大的个人站够用。
- 截图 Gallery 前端可以用 `Swiper.js` 或原生 CSS scroll-snap。
- 版本下载数统计的并发安全性：用 `UPDATE ... SET downloads = downloads + 1` 原子操作即可，不需要锁。
- 资源卡片列表的排序：如果有"推荐/精华"需求，可以加 `is_featured` 字段。

---

> **下一份**: `04-downloads-module.md` — 下载站 + RBAC 权限
