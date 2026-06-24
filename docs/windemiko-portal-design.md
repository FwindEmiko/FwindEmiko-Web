# 狐风轩汐 · 个人站点重构方案书 v2

> **项目代号**: WindEmiko Portal  
> **目标域名**: F.windEmiko.top  
> **撰写**: 狐魇星玖 / FCelestial  
> **日期**: 2026-06-23  
> **状态**: 方案设计阶段（确认版）  

---

## 目录

1. [项目概述](#1-项目概述)
2. [设计美学方案](#2-设计美学方案)
3. [推荐开源项目清单](#3-推荐开源项目清单)
4. [系统架构（Nuxt3 + FastAPI）](#4-系统架构nuxt3--fastapi)
5. [模块设计 & 目录结构](#5-模块设计--目录结构)
6. [数据库设计](#6-数据库设计)
7. [API 设计](#7-api-设计)
8. [前端设计（Nuxt3 公网 + Admin SPA）](#8-前端设计nuxt3-公网--admin-spa)
9. [Live2D 集成方案](#9-live2d-集成方案)
10. [AI/LLM 集成方案](#10-aillm-集成方案)
11. [文件管理 & 权限系统](#11-文件管理--权限系统)
12. [后台管理系统（Admin SPA）](#12-后台管理系统admin-spa)
13. [部署架构](#13-部署架构)
14. [实施路线图](#14-实施路线图)
15. [版本记录](#15-版本记录)

---

## 1. 项目概述

### 1.1 现状 & 目标

| 项目 | 现状 | 目标 |
|------|------|------|
| F.windEmiko.top | WordPress 吃灰 | → **新站**：博客 + 资源 + 下载 + AI |
| cloud.miragedge.top | OpenList 故障 | → 废弃，功能并入新站 `/download` |

### 1.2 核心功能

- **博客** — Markdown 写作，SSR/SSG 渲染，SEO 友好
- **MC 资源展示** — 插件/模组详情页（图文 + 版本历史 + 下载）
- **下载站** — 文件树 + 权限组 + 直链下载 + 外链跳转
- **AI 对话** — 本地 LLM + 知识库 RAG + Live2D 交互
- **后台管理** — 独立 SPA，一个人高效操作

### 1.3 已确认决策

| 决策项 | 确认方案 |
|--------|----------|
| 后端 | FastAPI (Python) |
| 前端框架 | **Nuxt 3**（SSR/SSG，替代原 Vue3 SPA） |
| CSS 方案 | **TailwindCSS** + 自定义 CSS |
| UI 组件库 | Element Plus |
| 图标 | Lucide（平面 SVG，禁用 emoji） |
| 文章编辑器 | **Vditor**（所见即所得 + Markdown） |
| 数据库 | **MySQL** 生产默认，**PostgreSQL** 保留切换能力 |
| 后台管理 | **独立 SPA**（/admin/*），纯 CSR |
| 评论系统 | 不做 |
| 资源评分/评论 | 不做 |
| 移动端 | **全站响应式适配** |
| Live2D 模型 | **占位：Niziiro Mao** → 未来替换为星玖定制 |
| AI 对话 | Ollama 本地 + 登录验证，星玖对接预留 |
| 维护者 | 星玖（我）负责技术维护 |

---

## 2. 设计美学方案

### 2.1 设计关键词

**玻璃磨砂 · 深色基调 · 二次元 · 圆角 · 非 AI 风格 · 平面图标**

### 2.2 玻璃磨砂 (Glassmorphism)

```css
/* 核心样式 — 全站通用 */
.glass {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(14px) saturate(180%);
  -webkit-backdrop-filter: blur(14px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
}
```

TailwindCSS 扩展方式：
```js
// tailwind.config.ts
extend: {
  colors: {
    glass: 'rgba(255, 255, 255, 0.04)',
    'glass-border': 'rgba(255, 255, 255, 0.06)',
  },
  backdropBlur: { glass: '14px' },
  borderRadius: { glass: '14px' },
}
```

### 2.3 色彩变量

```css
:root {
  --c-primary: #8B5CF6;
  --c-primary-light: #A78BFA;
  --c-bg: #0B0B1A;
  --c-surface: #111128;
  --c-glass: rgba(255,255,255,0.04);
  --c-text: #E2E2ED;
  --c-text-dim: #7B7B96;
  --r-sm: 8px; --r-md: 12px; --r-lg: 16px;
}
```

### 2.4 二次元元素

- 首页顶部：可切换的 ACG 风格横幅（静态插画，非轮播）
- Live2D 右下角角色（占位：Niziiro Mao）
- MC 像素风装饰图案（资源展示页点缀）
- 保留汐汐酱博客现有的动漫氛围，但不过度

---

## 3. 推荐开源项目清单

### 3.1 后端 & 全栈

| 项目 | Stars | 用途 | 链接 |
|------|-------|------|------|
| fastapi/full-stack-fastapi-template | 29k+ | FastAPI 官方全栈模板 | [github.com/fastapi/full-stack-fastapi-template](https://github.com/fastapi/full-stack-fastapi-template) |
| fastapi-users/fastapi-users | 5k+ | 用户认证（注册/登录/JWT） | [github.com/fastapi-users/fastapi-users](https://github.com/fastapi-users/fastapi-users) |
| insistence/RuoYi-Vue3-FastAPI | 2k+ | 若依 FastAPI 版（权限参考） | [github.com/insistence/RuoYi-Vue3-FastAPI](https://github.com/insistence/RuoYi-Vue3-FastAPI) |

### 3.2 前端 & 文件管理

| 项目 | Stars | 用途 | 链接 |
|------|-------|------|------|
| Nuxt 3 (nuxt/nuxt) | 57k+ | SSR/SSG 框架 | [github.com/nuxt/nuxt](https://github.com/nuxt/nuxt) |
| element-plus/element-plus | 25k+ | Vue3 UI 组件库 | [github.com/element-plus/element-plus](https://github.com/element-plus/element-plus) |
| tailwindlabs/tailwindcss | 87k+ | 实用优先 CSS 框架 | [github.com/tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| n1crack/vuefinder | 新 | Vue3 文件管理器（后端无关） | [github.com/n1crack/vuefinder](https://github.com/n1crack/vuefinder) |
| Vanessa219/vditor | 9k+ | Markdown 编辑器（所见即所得） | [github.com/Vanessa219/vditor](https://github.com/Vanessa219/vditor) |
| lucide-icons/lucide | 14k+ | 平面 SVG 图标 | [github.com/lucide-icons/lucide](https://github.com/lucide-icons/lucide) |

### 3.3 Live2D & AI 对话

| 项目 | 用途 | 链接 |
|------|------|------|
| Live2D/CubismWebSamples | 官方 Web SDK + Mao 模型 | [github.com/Live2D/CubismWebSamples](https://github.com/Live2D/CubismWebSamples) |
| guansss/pixi-live2d-display | Web Live2D 通用框架 | [github.com/guansss/pixi-live2d-display](https://github.com/guansss/pixi-live2d-display) |
| @aivue/chatbot | Vue3 AI 聊天组件 | [npmjs.com/package/@aivue/chatbot](https://www.npmjs.com/package/@aivue/chatbot) |
| deep-chat | 任意框架聊天组件 | [github.com/OvidijusParsiunas/deep-chat](https://github.com/OvidijusParsiunas/deep-chat) |

### 3.4 本地 LLM

| 项目 | 用途 |
|------|------|
| Ollama | 本地 LLM 运行（OpenAI 兼容 API） |
| ChromaDB | 轻量向量数据库（知识库 RAG） |
| LangChain | RAG pipeline + 文档索引 |

### 3.5 设计资源

| 资源 | 链接 |
|------|------|
| ui.glass/generator | https://ui.glass/generator |
| TailwindCSS Glassmorphism | https://tailwindcss-glassmorphism.vercel.app |

---

## 4. 系统架构（Nuxt3 + FastAPI）

### 4.1 总体架构

```
┌──────────────────────────────────────────────────────────────┐
│                     F.windEmiko.top                          │
│                       (Nginx 反代)                            │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Nuxt 3 前端 (SSR/SSG)    │  Admin SPA (CSR only)       │ │
│  │  pages/                    │  /admin/*                   │ │
│  │  ┌───────┬────────┬─────┐ │  ┌───────────────────────┐  │ │
│  │  │ 博客   │ 资源   │下载 │ │  │ 仪表盘 │ 编辑器 │ 文件 │  │ │
│  │  │ SSG   │ ISR   │ SSR │ │  │ 管理   │        │ 管理 │  │ │
│  │  └───────┴────────┴─────┘ │  └───────────────────────┘  │ │
│  │                           │                              │ │
│  │  ┌──────────────────────┐ │                              │ │
│  │  │ Live2D 组件 (右下角)  │ │  共享：API Client,          │ │
│  │  │ pixi-live2d-display  │ │  组件库, Tailwind 样式       │ │
│  │  └──────────────────────┘ │                              │ │
│  └──────────────┬────────────┴──────────────┬───────────────┘ │
│                 │ REST API (JWT Bearer)     │                  │
│  ┌──────────────▼──────────────────────────────────────────┐  │
│  │           FastAPI 后端 (阿里云 ECS)                      │  │
│  │                                                          │  │
│  │  Auth ── Blog ── Resources ── Downloads ── Chat ── Files │  │
│  │                                                          │  │
│  │  MySQL 8.0 (生产) / PostgreSQL (预配置切换)              │  │
│  │  文件存储: 本地磁盘 + 可选 OSS                           │  │
│  └──────────────────────────────┬───────────────────────────┘  │
│                                 │                              │
│  ┌──────────────────────────────▼───────────────────────────┐  │
│  │  汐汐酱本地 PC (RTX 4090)                                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │  │
│  │  │ Ollama       │  │ ChromaDB     │  │ Hermes (星玖) │  │  │
│  │  │ Qwen3 14B    │  │ 向量知识库    │  │ Agent API     │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  │  │
│  │         │                 │                  │           │  │
│  │         └─────────────────┴──────────────────┘           │  │
│  │                    │ (内部 API)                          │  │
│  └────────────────────┼─────────────────────────────────────┘  │
│                       │                                        │
└───────────────────────┼────────────────────────────────────────┘
                        │
                阿里云 ECS 通过 WG VPN
                或 HTTP 代理访问
```

### 4.2 技术栈

| 层级 | 技术 | 备注 |
|------|------|------|
| 前端 SSR | Nuxt 3 | Composition API, TypeScript |
| 前端管理 | Vue 3 + Vite | 独立 SPA, CSR only |
| 状态管理 | Pinia | Nuxt & Admin 共用 |
| CSS | TailwindCSS 4 | 实用优先 |
| UI 组件 | Element Plus | 按需引入 |
| 图标 | Lucide Vue Next | 平面 SVG |
| 后端 | FastAPI + uvicorn | Python 3.12+ |
| ORM | SQLAlchemy 2.0 | async with aiomysql |
| 数据库 | MySQL 8.0 (主) / PostgreSQL 16 (备) | SQLAlchemy 切换 URL 即可 |
| 迁移 | Alembic | 自动迁移 |
| 认证 | fastapi-users + PyJWT | JWT Bearer |
| 向量库 | ChromaDB | 知识库 RAG |
| 本地 LLM | Ollama | OpenAI 兼容 API |
| 容器化 | Docker Compose | 生产 & 开发环境 |
| Web 服务器 | Nginx | SSL 终结 + 反代 + 静态文件 |
| CI/CD | GitHub Actions | 自动构建 + 部署 |

---

## 5. 模块设计 & 目录结构

```
windemiko-portal/
├── backend/                          # FastAPI
│   ├── app/
│   │   ├── main.py                   # 入口
│   │   ├── config.py                 # Pydantic Settings
│   │   ├── database.py               # SQLAlchemy async engine
│   │   ├── dependencies.py           # 依赖注入
│   │   ├── middleware.py             # CORS, 日志, 限流
│   │   ├── exceptions.py             # 异常处理
│   │   │
│   │   ├── modules/
│   │   │   ├── auth/                 # 认证
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   └── utils.py
│   │   │   ├── blog/                 # 博客
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── router.py
│   │   │   │   └── service.py
│   │   │   ├── resources/            # MC 资源
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── router.py
│   │   │   │   └── service.py
│   │   │   ├── downloads/            # 下载站
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   └── permission.py
│   │   │   ├── chat/                 # AI 对话
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── router.py
│   │   │   │   ├── service.py
│   │   │   │   └── llm_client.py
│   │   │   └── files/                # 通用文件
│   │   │       ├── models.py
│   │   │       ├── schemas.py
│   │   │       ├── router.py
│   │   │       └── storage.py
│   │   │
│   │   └── core/
│   │       ├── security.py
│   │       ├── pagination.py
│   │       └── events.py
│   │
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── nuxt-app/                         # Nuxt 3 公网站点
│   ├── pages/
│   │   ├── index.vue                 # 首页
│   │   ├── blog/
│   │   │   ├── index.vue             # 博客列表
│   │   │   └── [slug].vue            # 博客详情 (SSG)
│   │   ├── resources/
│   │   │   ├── index.vue             # 资源列表
│   │   │   └── [slug].vue            # 资源详情 (ISR)
│   │   ├── download/
│   │   │   └── index.vue             # 下载站 (SSR)
│   │   ├── login.vue                 # 登录
│   │   ├── register.vue              # 注册
│   │   └── profile.vue              # 个人中心
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppHeader.vue
│   │   │   ├── AppFooter.vue
│   │   │   └── AppNav.vue
│   │   ├── glass/
│   │   │   ├── GlassCard.vue
│   │   │   ├── GlassButton.vue
│   │   │   └── GlassModal.vue
│   │   ├── blog/
│   │   │   ├── PostCard.vue
│   │   │   └── PostList.vue
│   │   ├── resources/
│   │   │   ├── ResourceCard.vue
│   │   │   ├── ResourceDetail.vue
│   │   │   ├── ScreenshotGallery.vue
│   │   │   └── VersionTimeline.vue
│   │   ├── downloads/
│   │   │   ├── FileBrowser.vue
│   │   │   ├── FilePreview.vue
│   │   │   └── BreadcrumbBar.vue
│   │   ├── chat/
│   │   │   ├── ChatPanel.vue
│   │   │   └── ChatDialog.vue
│   │   └── live2d/
│   │       ├── Live2DWidget.vue
│   │       └── Live2DDialog.vue
│   │
│   ├── composables/
│   │   ├── useAuth.ts
│   │   ├── useLive2D.ts
│   │   └── useTheme.ts
│   ├── server/                       # Nuxt Server 路由（API 代理）
│   │   └── api/                      # 可选：BFF 层
│   ├── stores/
│   ├── assets/
│   │   └── live2d/                   # Niziiro Mao 模型文件
│   ├── nuxt.config.ts
│   ├── tailwind.config.ts
│   └── package.json
│
├── admin-spa/                        # Admin 独立 SPA (Vite + Vue3)
│   ├── src/
│   │   ├── main.ts
│   │   ├── App.vue
│   │   ├── router/
│   │   ├── stores/
│   │   ├── api/
│   │   ├── composables/
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── AdminLayout.vue
│   │   │   │   └── AdminSidebar.vue
│   │   │   ├── editors/
│   │   │   │   ├── PostEditor.vue
│   │   │   │   └── ResourceEditor.vue
│   │   │   └── file-manager/
│   │   │       ├── FileTree.vue
│   │   │       ├── FileTable.vue
│   │   │       └── UploadZone.vue
│   │   └── views/
│   │       ├── DashboardView.vue
│   │       ├── PostListView.vue
│   │       ├── PostEditView.vue
│   │       ├── ResourceListView.vue
│   │       ├── ResourceEditView.vue
│   │       ├── FileManagerView.vue
│   │       └── UserManagerView.vue
│   ├── vite.config.ts
│   └── package.json
│
├── packages/                         # 共享包 (Monorepo)
│   ├── shared/                       # 共享类型 + API 客户端
│   │   ├── src/
│   │   │   ├── types/                # TypeScript 接口定义
│   │   │   ├── api-client/           # API 请求封装
│   │   │   └── constants/
│   │   └── package.json
│   └── ui/                           # 共享 UI 组件
│       ├── src/
│       │   ├── glass/                # Glassmorphism 组件
│       │   └── icons/                # Lucide 封装
│       └── package.json
│
├── docs/                             # 开发者文档
│   ├── architecture.md
│   ├── api-reference.md
│   ├── modules/
│   │   ├── auth.md
│   │   ├── blog.md
│   │   ├── resources.md
│   │   ├── downloads.md
│   │   └── chat.md
│   ├── deployment.md
│   ├── development.md
│   └── live2d-setup.md
│
├── scripts/                          # 工具脚本
│   ├── migrate-wp.ts                 # WordPress 迁移
│   └── seed-db.py                    # 数据库种子
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── nginx.conf
├── .env.example
├── Makefile
├── pnpm-workspace.yaml
└── README.md
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `packages/shared` | TypeScript 接口定义、API 请求封装、常量（Nuxt & Admin 共用） |
| `packages/ui` | Glassmorphism 组件、Lucide 图标封装（Nuxt & Admin 共用） |
| `nuxt-app` | 公网站点：SSR/SSG 渲染，SEO 优化 |
| `admin-spa` | 后台管理：纯 CSR，独立构建和部署 |
| `backend` | REST API + 数据库 + 文件存储 + LLM 桥接 |

---

## 6. 数据库设计

### 6.1 数据库选择策略

```
开发环境:  SQLite (零配置)
生产环境:  MySQL 8.0 (默认)
备选方案:  PostgreSQL 16 (预配置，切换仅改 DATABASE_URL)

# SQLAlchemy 2.0 async 引擎均支持，一行配置切换
DATABASE_URL=mysql+aiomysql://user:pass@host/db
# 或
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

### 6.2 核心表

**User**
```
id, username, email, password_hash, avatar_url, display_name
bio, role, is_active, is_verified, created_at, updated_at
```

**Post**
```
id, title, slug, content (Markdown), summary, cover_url
author_id (FK), category_id (FK)
status (draft/published), is_pinned
view_count, published_at, created_at, updated_at
```

**Category / Tag**
```
id, name, slug, description
# Post ↔ Tag 为多对多关系表
```

**Resource**
```
id, title, slug, description (Markdown)
type (plugin/mod/datapack), game_version, loader
icon_url, cover_url, download_count
status, created_at, updated_at
```

**ResourceVersion**
```
id, resource_id (FK), version_string, changelog
file_url, external_url (第三方网盘跳转)
file_size, file_hash, downloads, created_at
```

**Screenshot**
```
id, resource_id (FK), image_url, caption, sort_order
```

**Folder**（虚拟目录树）
```
id, name, slug, parent_id (自引用), description
is_visible, sort_order, created_at, updated_at
```

**FileNode**
```
id, folder_id (FK), filename, display_name
file_size, file_hash, mime_type, storage_path
external_url, is_directory, parent_file_id (自引用)
download_count, created_at
```

**FolderPermission**
```
id, folder_id (FK), role, can_read, can_download
```

**ChatSession**
```
id, user_id (FK), title, model, created_at, updated_at
```

**ChatMessage**
```
id, session_id (FK), role, content, tokens, created_at
```

---

## 7. API 设计

### 7.1 端点草案

```
# === 认证 ===
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/refresh
GET    /api/auth/me
PUT    /api/auth/me                         # 更新个人信息/头像
POST   /api/auth/me/avatar                  # 上传头像

# === 博客 ===
GET    /api/posts                           # ?page=&category=&tag=&q=
GET    /api/posts/:slug                     # 文章详情
POST   /api/posts                           # 新建 (author+)
PUT    /api/posts/:id                       # 编辑
DELETE /api/posts/:id                       # 删除
GET    /api/categories
GET    /api/tags

# === 资源展示 ===
GET    /api/resources                       # ?type=&version=&loader=
GET    /api/resources/:slug                 # 详情 + versions + screenshots
POST   /api/resources                       # 新建
PUT    /api/resources/:id                   # 编辑
POST   /api/resources/:id/versions          # 添加版本
DELETE /api/resources/:id                   # 删除

# === 下载站 ===
GET    /api/downloads/folders               # 文件夹树
GET    /api/downloads/folders/:id/files     # 文件列表
GET    /api/downloads/files/:id/download    # 下载 + 计数
POST   /api/downloads/folders               # 创建文件夹 (admin)
POST   /api/downloads/files                 # 上传文件 (admin)
DELETE /api/downloads/folders/:id
DELETE /api/downloads/files/:id

# === AI 对话 (需登录) ===
GET    /api/chat/sessions                   # 我的对话列表
POST   /api/chat/sessions                   # 新建对话
POST   /api/chat/messages                   # 发送消息 (SSE 流式)
GET    /api/chat/sessions/:id/messages      # 历史消息
DELETE /api/chat/sessions/:id

# === 文件上传 ===
POST   /api/files/upload                    # 通用上传

# === 管理 ===
GET    /api/admin/stats                     # 仪表盘统计
GET    /api/admin/users                     # 用户列表
PUT    /api/admin/users/:id/role            # 修改角色
```

### 7.2 统一响应格式

```json
{
  "code": 0,
  "data": { ... },
  "message": "ok"
}
```

分页：
```json
{
  "code": 0,
  "data": {
    "items": [...],
    "total": 42,
    "page": 1,
    "size": 20,
    "pages": 3
  }
}
```

### 7.3 渲染策略 (Nuxt3)

| 页面类型 | 渲染策略 | 理由 |
|----------|----------|------|
| 首页 | SSG (构建时生成) | 内容不频繁变化 |
| 博客列表 | ISR (增量静态再生) | 新文章发布后更新 |
| 博客详情 | SSG | 文章不改动，构建时预渲染 |
| 资源列表 | ISR | 新资源发布后更新 |
| 资源详情 | SSG | 内容稳定 |
| 下载站 | SSR (每次请求渲染) | 权限实时校验 |
| 登录/注册 | CSR (客户端渲染) | 交互性强 |
| 个人中心 | CSR | 登录后才能看 |

---

## 8. 前端设计（Nuxt3 公网 + Admin SPA）

### 8.1 公网页面清单

| 路由 | 组件 | 渲染 | 权限 |
|------|------|------|------|
| `/` | index.vue | SSG | 公开 |
| `/blog` | blog/index.vue | ISR | 公开 |
| `/blog/:slug` | blog/[slug].vue | SSG | 公开 |
| `/resources` | resources/index.vue | ISR | 公开 |
| `/resources/:slug` | resources/[slug].vue | SSG | 公开 |
| `/download` | download/index.vue | SSR | 部分需登录 |
| `/login` | login.vue | CSR | 公开 |
| `/register` | register.vue | CSR | 公开 |
| `/profile` | profile.vue | CSR | 需登录 |

### 8.2 Nuxt3 关键配置

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', '@element-plus/nuxt'],
  nitro: {
    prerender: {
      routes: ['/', '/blog'],  // SSG 预渲染
      crawlLinks: true,
    },
  },
  routeRules: {
    '/blog/**': { swr: 3600 },       // ISR 1 小时
    '/resources/**': { swr: 86400 },  // ISR 1 天
    '/download/**': { ssr: true },     // SSR 实时
  },
  app: {
    head: {
      // SEO 全局 meta
    },
  },
})
```

### 8.3 移动端适配策略

- TailwindCSS 响应式断点：`sm` (640px) / `md` (768px) / `lg` (1024px)
- 导航栏：桌面端横向菜单 → 移动端汉堡菜单（抽屉式）
- 文件管理器：桌面端左右分栏 → 移动端单栏 + 返回按钮
- 资源卡片：桌面端 3 列 → 平板 2 列 → 手机 1 列
- Live2D 组件：移动端可折叠到左下角（避免遮挡内容）

### 8.4 SEO

```vue
<!-- 文章页 SEO -->
<script setup lang="ts">
const { data: post } = await useFetch('/api/posts/' + route.params.slug)

useSeoMeta({
  title: post.value.title,
  ogTitle: post.value.title,
  description: post.value.summary,
  ogDescription: post.value.summary,
  ogImage: post.value.cover_url,
  articlePublishedTime: post.value.published_at,
})
</script>
```

- 自动生成 sitemap.xml
- robots.txt 配置
- Schema.org Article 结构化数据

---

## 9. Live2D 集成方案

### 9.1 占位模型：Niziiro Mao

**来源**: Live2D Cubism SDK for Web Samples  
**仓库**: [Live2D/CubismWebSamples](https://github.com/Live2D/CubismWebSamples)  
**路径**: `Samples/Resources/Mao/`  
**协议**: Live2D Free Material License（允许用于非商业展示/测试）

**模型能力**:
- Cubism 4 格式 (`.model3.json` + `.moc3`)
- 多个表情 (`.exp3.json`)
- 多个动作组：idle, tap, special (`.motion3.json`)
- 物理效果 (`.physics3.json`)
- 唇形同步参数支持

**替换为星玖**:
- Mao 模型文件路径：`nuxt-app/assets/live2d/mao/`
- 替换时只需将星玖模型放入同路径，更新 `model3.json` 引用
- 动画参数保持同名即可无缝切换

### 9.2 技术栈

```
Live2DWidget.vue (Nuxt3 组件)
    │
    ├── pixi-live2d-display (Cubism 4)
    │   └── Mao.model3.json → PixiJS Canvas
    │
    ├── @aivue/chatbot (对话气泡 UI)
    │   └── SSE 流式显示 LLM 回复
    │
    └── LLM 桥接
        ├── Nuxt Server API 代理: /api/internal/chat → ECS 后端
        └── 后端 → Ollama / Hermes
```

### 9.3 交互设计

| 触发 | 行为 |
|------|------|
| 页面加载 | 待机动画循环 + 随机眨眼 |
| 鼠标悬停 | 视线跟随光标 |
| 点击身体 | 触发 `tap` 动作 + 弹出小气泡「怎么了喵？」 |
| 用户发消息 | 播放说话动画 + 对话气泡逐字显示 |
| AI 回复结束 | 回到待机状态 |
| 长按 3 秒 | 切换模型（未来：Mao ↔ 星玖） |
| 移动端 | 缩小到 80%，位置可拖动 |

### 9.4 Composables 关键接口

```ts
// composables/useLive2D.ts
export function useLive2D() {
  const { t } = useI18n()

  function tap(x: number, y: number) {
    model.value?.motion('Tap')
    showBubble('怎么了喵？')
  }

  async function speak(text: string) {
    // 流式显示在气泡中
    // 设置 isSpeaking → 播放唇形同步
  }

  function onMessageSent(msg: string) {
    // POST → SSE Stream → speak(chunk)
  }

  return { tap, speak, onMessageSent, isSpeaking }
}
```

---

## 10. AI/LLM 集成方案

### 10.1 架构

```
用户输入（博客对话 / Live2D 聊天框）
    │
    ▼
Nuxt Server (BFF) → POST /api/internal/chat (SSE)
    │
    ▼
FastAPI Chat Module
    │
    ├── Auth: 验证 JWT + 每日配额检查
    ├── Intent: 判断是否触发知识库检索
    ├── RAG: ChromaDB 向量检索 → 相关文档片段
    ├── Prompt: System Prompt + 历史 + RAG + 用户输入
    │
    └── LLM: Ollama API (本地)
        └── POST http://localhost:11434/api/chat (stream)
            → SSE 逐 token 返回前端
```

### 10.2 本地 LLM

```bash
# 安装 Ollama（汐汐酱 Windows 主机）
ollama pull qwen3:14b       # 推荐：14B 参数，RTX 4090 24GB 游刃有余
ollama pull deepseek-r1:14b # 备选：推理能力强
```

后端 LLM 客户端核心（`backend/app/modules/chat/llm_client.py`）:
```python
# 异步调用 Ollama API，返回 AsyncGenerator
async def stream_chat(model: str, messages: list) -> AsyncGenerator[str, None]:
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={"model": model, "messages": messages, "stream": True},
            timeout=120,
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk.get("message", {}).get("content", "")
```

### 10.3 知识库 RAG

```
博客发布 / 更新
    → FastAPI Event (background task)
        → 文章内容分块 (Markdown → text → chunks)
        → Ollama Embedding (nomic-embed-text)
        → ChromaDB 存储向量 + 元数据

对话时
    → 用户问题 Embedding
    → ChromaDB 相似度检索 (top_k=3)
    → 拼接 System Prompt: "参考以下内容回答：{retrieved_chunks}"
    → LLM 生成回答
```

### 10.4 星玖对接（预留）

```
Chat Module 配置：
  LLM_MODE = "ollama"          # 当前
  LLM_MODE = "hermes"          # 未来切换
  LLM_MODE = "cloud_agent"     # 云端星玖节点
```

- 通过环境变量 `LLM_BACKEND` 切换
- Hermes 模式下后端将对话转发到 Hermes Agent API
- 云端节点模式：通过 WG VPN 或 HTTP 代理访问
- 对话风格 System Prompt 保持一致（星玖角色定义）

### 10.5 登录 & 配额

- AI 对话需登录验证
- 每日默认 50 次对话（本地 API 无费用，仅管理限制）
- 管理员无限制

---

## 11. 文件管理 & 权限系统

### 11.1 虚拟文件系统

参考 OpenList 的设计理念——不暴露物理路径，通过数据库管理虚拟目录树。

**与 OpenList 的对标**:

| OpenList 功能 | 新站实现 |
|--------------|----------|
| 密码保护文件夹 | 角色权限 (FolderPermission) |
| 文件直链 | `/api/downloads/files/:id/download` |
| 文件列表 | FileBrowser 组件 + 面包屑导航 |
| 上传到指定文件夹 | FileManager 拖拽上传 |
| README 展示 | Folder.description (Markdown) |
| 登录后可见更多 | 角色隔离 + 前端条件渲染 |
| 外部存储源 | external_url 字段 |

### 11.2 权限模型

**四角色 RBAC**:

| 角色 | 可见文件夹 | 可下载 | 可上传/管理 |
|------|-----------|--------|-------------|
| `admin` | **全部** | **全部** | **全部** |
| `author` | 公开 + 资源区 | 全部 | 资源区文件 |
| `member` | 公开 + 分配区 | 允许的 | 否 |
| `guest` (匿名) | 仅公开区 | 公开文件 | 否 |

权限检查流程：
```
GET /api/downloads/files/:id/download
    → 1. 查询文件归属文件夹
    → 2. 查询用户角色
    → 3. 查询 FolderPermission (role × folder)
    → 4. can_download? → 返回文件内容 : 403
```

### 11.3 第三方网盘跳转

`ResourceVersion.external_url` 字段存储外链。
前端资源详情页：
```
「本地下载」按钮 (如果 file_url 非空)
「网盘下载」按钮 (如果 external_url 非空) → target="_blank"
```

下载站同理：`FileNode.external_url` 可选外链。

---

## 12. 后台管理系统（Admin SPA）

### 12.1 设计理念

> **维护者 = 星玖（我）**  
> 界面清晰、接口规范、文档完善——确保我能在任何新会话中快速上手

### 12.2 页面清单

| 路由 | 页面 | 说明 |
|------|------|------|
| `/admin` | DashboardView | 统计：文章数/资源数/文件数/下载量/最近活动 |
| `/admin/posts` | PostListView | 文章列表：筛选/搜索/批量操作 |
| `/admin/posts/new` | PostEditView | Vditor 编辑器 + 预览 + 发布 |
| `/admin/posts/:id/edit` | PostEditView | 同上，加载已有内容 |
| `/admin/resources` | ResourceListView | 资源列表 |
| `/admin/resources/new` | ResourceEditView | 资源编辑器（信息+截图+版本） |
| `/admin/resources/:id/edit` | ResourceEditView | 编辑已有资源 |
| `/admin/files` | FileManagerView | 文件管理器（vuefinder 集成） |
| `/admin/users` | UserManagerView | 用户管理 |

### 12.3 编辑器设计（重点）

**文章编辑器 (PostEditView)**:
```
┌────────────────────────────────────────────┐
│  [标题输入框]                               │
│  [分类选择] [标签选择]                      │
│  ┌──────────────────────────────────────┐  │
│  │           Vditor 编辑器               │  │
│  │  (所见即所得 → 左下角切换 Markdown)    │  │
│  └──────────────────────────────────────┘  │
│  [封面图上传]                              │
│  [存草稿] [预览] [发布]                    │
└────────────────────────────────────────────┘
```

**资源编辑器 (ResourceEditView)**:
```
┌────────────────────────────────────────────┐
│  Tab 1: 基本信息                            │
│  [标题] [类型: 插件/模组/数据包]             │
│  [MC版本] [加载器: Paper/Spigot/Folia...]   │
│  [图标上传] [封面图上传]                    │
│  [描述 (Markdown)]                          │
│                                             │
│  Tab 2: 截图管理                            │
│  [拖拽上传区] → 排序列表（可拖拽调整顺序）   │
│                                             │
│  Tab 3: 版本管理                            │
│  [+ 添加版本]                               │
│  ├─ v1.2.0: [更新日志] [文件/外链] [删除]   │
│  ├─ v1.1.0: [更新日志] [文件/外链] [删除]   │
│  └─ v1.0.0: [更新日志] [文件/外链] [删除]   │
└────────────────────────────────────────────┘
```

**文件管理器 (FileManagerView)**:
```
┌────────────────────────────────────────────┐
│  ┌──────────┬─────────────────────────────┐│
│  │ 文件夹树  │  [面包屑]                    ││
│  │           │  ┌─────────────────────────┐││
│  │ 📁 公开   │  │ 文件名      大小  日期   │││
│  │ ├📁 插件  │  │ SkyIsland-v1.2.jar ... │││
│  │ ├📁 模组  │  │ BentoBox-v3.16.jar ... │││
│  │ └📁 工具  │  │ ...                     │││
│  │ 🔒 内部   │  └─────────────────────────┘││
│  │ 🔒 VIP    │  [拖拽文件到此处上传]        ││
│  └──────────┴─────────────────────────────┘│
│  [新建文件夹] [上传文件] [批量删除]          │
└────────────────────────────────────────────┘
```

### 12.4 单人操作优化

| 优化 | 说明 |
|------|------|
| 快捷键 | `Ctrl+S` 保存，`Ctrl+Enter` 发布，`Esc` 关闭弹窗 |
| 自动保存 | 编辑器每 30 秒保存草稿到 localStorage |
| 拖拽操作 | 截图排序、文件上传均支持拖拽 |
| 模板功能 | 资源描述可保存为模板，新建时一键加载 |
| 记忆选项 | 上次选择的分类/标签/版本自动记住 |
| 批量操作 | 资源列表多选 → 批量修改分类/标签/删除 |

---

## 13. 部署架构

### 13.1 Docker Compose（阿里云 ECS 生产环境）

```yaml
version: '3.9'
services:
  nginx:
    image: nginx:alpine
    ports: ['80:80', '443:443']
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certbot/www:/var/www/certbot
    depends_on: [backend, nuxt]

  backend:
    build: ./backend
    expose: [8000]
    env_file: .env
    volumes: [uploads:/app/uploads]
    depends_on: [mysql]

  nuxt:
    build: ./nuxt-app
    expose: [3000]
    env_file: .env

  admin:
    build: ./admin-spa
    # 静态文件由 nginx 直接 serve

  mysql:
    image: mysql:8.0
    volumes: [mysqldata:/var/lib/mysql]
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASS}
      MYSQL_DATABASE: windemiko
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

volumes:
  uploads:
  mysqldata:
```

### 13.2 Nginx 路由

```
# 公网站点 (Nuxt3 SSR)
location / {
    proxy_pass http://nuxt:3000;
}

# 管理后台 (静态文件)
location /admin {
    alias /app/admin/dist;
    try_files $uri /admin/index.html;
}

# API
location /api {
    proxy_pass http://backend:8000;
}

# 文件下载直链
location /files {
    alias /app/uploads;
}
```

### 13.3 环境变量

```
# .env
DATABASE_URL=mysql+aiomysql://windemiko:password@mysql:3306/windemiko
JWT_SECRET=xxx
JWT_ALGORITHM=HS256
OLLAMA_BASE_URL=http://192.168.2.x:11434    # 汐汐酱本地PC（WG VPN IP）
CHROMADB_HOST=192.168.2.x
CHROMADB_PORT=8000
LLM_BACKEND=ollama                           # ollama | hermes | cloud_agent
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE=524288000                    # 500MB
```

---

## 14. 实施路线图

### Phase 0 — Monorepo 初始化 (2 天)

- [ ] pnpm workspace 配置
- [ ] `packages/shared` 共享类型 + API 客户端
- [ ] `packages/ui` Glassmorphism 组件
- [ ] FastAPI 骨架 + Alembic 初始迁移
- [ ] MySQL Docker 服务 + 本地 SQLite 模式
- [ ] Nuxt3 空项目 + TailwindCSS + Element Plus
- [ ] Admin SPA 空项目 (Vite + Vue3)
- [ ] `docs/` 目录初始化
- [ ] GitHub Actions CI/CD

### Phase 1 — 认证 + 博客 (1-1.5 周)

- [ ] 用户注册/登录/个人信息 + 头像上传
- [ ] 文章 CRUD + 分类/标签
- [ ] Vditor 集成到 Admin SPA
- [ ] Nuxt3 博客列表 + 详情页 (SSG/ISR)
- [ ] WordPress 迁移脚本
- [ ] SEO meta + sitemap

### Phase 2 — 资源 + 下载站 (1-1.5 周)

- [ ] 资源模块 CRUD + 版本管理 + 截图
- [ ] 下载站虚拟目录 + 文件 CRUD
- [ ] RBAC 权限控制
- [ ] FileBrowser 组件（Nuxt3 公网 + Admin）
- [ ] Admin 资源/文件管理器
- [ ] 外链跳转支持

### Phase 3 — AI + Live2D (1 周)

- [ ] Ollama 部署 + ChromaDB 配置
- [ ] AI 对话后端 (SSE) + 配额
- [ ] Nuxt3 ChatPanel 组件
- [ ] pixi-live2d-display 集成 + Mao 模型加载
- [ ] Live2D ↔ Chat 联动（说话动画 + 气泡）
- [ ] RAG 知识库索引 pipeline

### Phase 4 — 打磨 + 上线 (1 周)

- [ ] 玻璃磨砂全局主题覆盖
- [ ] 响应式适配全面测试
- [ ] 性能优化（图片懒加载、Nuxt Image、CDN）
- [ ] Nginx 配置 + SSL
- [ ] 生产部署 + smoke test
- [ ] 旧域名 301 重定向
- [ ] 数据库备份策略 (mysqldump cron)

**预计总工期**: 4-5 周

---

## 15. 版本记录

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-06-23 | 初始方案，Vue3 SPA 单页 |
| **v2** | **2026-06-23** | **确认决策版**：Nuxt3 + Admin SPA 双前端、MySQL 默认/PostgreSQL 预留、TailwindCSS、Vditor、Mao 占位模型、星玖预留对接 |

---

> 方案书 v2 确认完毕。  
> 下一个交付物：**开发者文档**（架构细节 + API 接口规范 + 数据库 DDL + 前端组件 API）  
> 准备开写喵？🦊
