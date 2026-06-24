# 02 — 博客模块

> **依赖**: `01-backend-core.md`（auth 模块已完成）  
> **目标**: 文章 CRUD、分类/标签管理、Markdown 渲染 API  
> **验证**: 前端能获取文章列表、分类过滤、单篇详情

---

## 1. 数据模型 (`backend/app/modules/blog/models.py`)

```python
class Category(Base):
    __tablename__ = "categories"
    id: int (PK)
    name: str (unique)
    slug: str (unique, URL 友好, 自动从 name 生成或手动指定)
    description: str (nullable)

class Tag(Base):
    __tablename__ = "tags"
    id: int (PK)
    name: str (unique)
    slug: str (unique)

# 多对多关联表
post_tags = Table(
    "post_tags", Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Post(Base):
    __tablename__ = "posts"
    id: int (PK)
    title: str
    slug: str (unique, indexed)        # URL 标识符，自动从 title 生成
    content: str                       # Markdown 原文
    summary: str (nullable)            # 摘要（纯文本前 200 字符或手动填写）
    cover_url: str (nullable)          # 封面图 URL
    author_id: int (FK → users.id)
    category_id: int (FK → categories.id, nullable)
    tags: relationship → Tag (M2M)
    status: str (default "draft")      # draft / published / archived
    is_pinned: bool (default False)
    view_count: int (default 0)
    published_at: datetime (nullable)  # 首次发布时间
    created_at: datetime
    updated_at: datetime
```

### 关键约束

- `slug`: 自动从 title 生成（中文转拼音或直接用 `/posts/{id}` 兜底）。如果重复则追加 `-2`, `-3`。
- `status` 状态机: draft → published → archived（不可反向，除非手动改）
- `published_at`: 首次从 draft → published 时自动设为当前时间，之后不变
- 软删除不如硬删除——一个人用的博客不需要回收站

---

## 2. API 端点 (`backend/app/modules/blog/router.py`)

### 公开接口

```
GET  /api/posts
  query: ?page=1&size=20&category=slug&tag=slug&q=关键词&status=published
  排序: is_pinned DESC, published_at DESC
  说明: 不登录也能看，只返回 status=published 的文章
  返回: {items: [...], total, page, size, pages}

GET  /api/posts/{slug}
  说明: 返回完整文章，自动 view_count +1
  返回: {post, prev_post?, next_post?}  # 上一篇/下一篇用于导航

GET  /api/categories
  返回所有分类（含每个分类的文章计数）

GET  /api/tags
  返回所有标签（含每个标签的文章计数）
```

### 认证接口（需登录 + author/admin 角色）

```
POST   /api/posts
  权限: author+
  body: {title, content, summary?, cover_url?, category_id?, tags: [id,...]?, status: "draft"|"published"}
  逻辑: 自动生成 slug → 保存 → 返回 post

PUT    /api/posts/{id}
  权限: author+ (且只能改自己的文章，admin 可改全部)
  body: 同 POST，但所有字段可选

DELETE /api/posts/{id}
  权限: admin（或自己文章的 author）
  逻辑: 解除 tag 关联 → 删除文章

POST   /api/categories        (admin)
PUT    /api/categories/{id}   (admin)
DELETE /api/categories/{id}   (admin) — 如果该分类下有文章则禁止删除，返回错误

POST   /api/tags              (author+)
DELETE /api/tags/{id}         (admin)
```

### 搜索

- `?q=关键词`: 全文搜索 title + content
- MySQL 用 `LIKE %keyword%` 或 `FULLTEXT INDEX`
- PostgreSQL 用 `to_tsvector` / `to_tsquery`（更好）
- 建议：为 content 建立全文索引，如果性能有要求后续可以接 Elasticsearch

---

## 3. Markdown 渲染

不需要独立的渲染 API——文章详情 API 直接返回两个字段：

```json
{
  "content_md": "# 原始 Markdown",     // 前端 Vditor 编辑用
  "content_html": "<h1>渲染后的 HTML</h1>"  // 前端展示用
}
```

后端用 `markdown` 库（Python-Markdown 或 mistune）渲染。
**扩展支持**: 代码高亮（`fenced_code` + `codehilite`）、表格、任务列表。

---

## 4. 验证方式

```bash
# 创建分类
curl -X POST http://localhost:8000/api/categories \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"技术笔记","slug":"tech"}'

# 创建文章
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer <author_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"第一篇文章","content":"# Hello\n这是内容","status":"published","category_id":1,"tags":[1]}'

# 查看文章列表
curl http://localhost:8000/api/posts?category=tech&page=1

# 查看详情
curl http://localhost:8000/api/posts/第一篇文章
# → content_md + content_html + prev_post + next_post
```

---

## 5. 灵活性留白

- Slug 生成：可以用 `python-slugify` 或自己写拼音转换（`pypinyin`）。如果 slug 冲突，追加 `-n` 后缀。
- 精华置顶：`is_pinned` + `published_at DESC` 排序——精华文章排最前，其余按时间。
- 上一篇/下一篇：用 `published_at` 排序取相邻记录，SQL 子查询或 ORM `lt`/`gt` 过滤即可。
- 如果 SEO 需要更友好的 URL，slug 生成逻辑可以调优（比如中文转英文或保留中文——Nuxt3 的 `[slug].vue` 对中英文都支持）。
- 封面图：推荐尺寸 1200×630（Open Graph 标准），上传时后端做 resize 更好，但不强制。

---

> **下一份**: `03-resources-module.md` — MC 资源 CRUD + 版本管理
