# WindEmiko Portal — Trae AI 执行手册

> **给 Trae（Kimi K2.7-coder）的执行指令**  
> **项目**: FwindEmiko-Web（仓库已由汐汐酱在 GitHub 创建）  
> **约定**: 每个会话 = 独立上下文，读文档 → 写代码 → 自测 → 输出报告  

---

## 全局约定（每个会话都遵守）

### 硬约束（不可改）

- FastAPI + SQLAlchemy 2.0 async + JWT 认证
- Nuxt 3（公网 SSR/SSG）+ Admin SPA（独立 Vite + Vue3 CSR）
- API 统一响应: `{"code":0,"data":...,"message":"ok"}`
- MySQL 默认，必须可切 PostgreSQL（SQLAlchemy URL 切换）
- TailwindCSS + Element Plus + Lucide 图标
- pnpm monorepo（workspace）

### 灵活性（可自行判断）

- Repository/Service 层拆分方式
- 具体实现模式和错误处理策略
- UI 细节、动画、交互 UX
- 三方库选择（功能等价的替代方案）
- 代码组织和组件拆分粒度

### 每个会话完成后必须

1. **自测**：用 curl / pnpm dev / 浏览器验证核心功能可运行
2. **输出报告**：写入 `reports/session-N-report.md`，包含：
   - 完成了哪些功能
   - 遇到了什么问题 + 如何解决
   - 哪些地方做了灵活调整（与文档不同的实现）
   - 已知限制 / 未完成项
   - 下一会话的依赖项是否就绪

---

## 会话顺序总览

```
Session 1: Monorepo + 后端核心 + 认证
    ↓
Session 2: 全部业务 API（博客/资源/下载/聊天）
    ↓
┌──────────┴──────────┐
↓                     ↓
Session 3:             Session 4:
Nuxt3 公网站点         Admin SPA
(前台)                 (后台)
    ↓
Session 5: Live2D 集成
```

- Session 1→2 **必须串行**
- Session 3 和 4 **可并行**
- Session 5 **依赖 Session 3 完成**

---

# Session 1 — Monorepo + 后端核心 + 认证

## 读取文档

```
00-overview.md
01-backend-core.md
```

## 执行指令

```
你正在开发 FwindEmiko-Web 项目。请先阅读 00-overview.md 和 01-backend-core.md。

你的任务：从零搭建整个项目的 Monorepo 骨架，并完成 FastAPI 后端的认证模块。

完成以下全部步骤：

### Step 1: Monorepo 初始化
- pnpm workspace 配置（pnpm-workspace.yaml），包含 nuxt-app、admin-spa、packages/*
- backend/ 目录 + Python 虚拟环境 + pyproject.toml（依赖见 00-overview）
- nuxt-app/ 目录（npx nuxi init）
- admin-spa/ 目录（npm create vite@latest，vue-ts 模板）
- packages/shared/ 和 packages/ui/ 空包

### Step 2: 后端核心基础设施
- backend/app/config.py：Pydantic Settings，读取 .env
- backend/app/database.py：异步 SQLAlchemy 引擎（支持 SQLite/MySQL/PostgreSQL 三种 URL），get_db 依赖注入
- backend/app/core/security.py：密码哈希(bcrypt) + JWT 生成/验证

### Step 3: 认证模块
- backend/app/modules/auth/models.py：User 模型
- backend/app/modules/auth/schemas.py：Pydantic 请求/响应
- backend/app/modules/auth/router.py：
  - POST /api/auth/register
  - POST /api/auth/login（返回 access_token + refresh_token + user）
  - POST /api/auth/refresh
  - GET /api/auth/me
  - PUT /api/auth/me
  - POST /api/auth/me/avatar
- backend/app/modules/auth/dependencies.py：get_current_user、require_role
- backend/app/main.py：FastAPI 入口（CORS + 异常处理 + 路由注册）

### Step 4: 数据库迁移
- Alembic 初始化 + 配置异步引擎
- 生成并执行首次迁移

### Step 5: 开发环境
- docker-compose.dev.yml（MySQL 8.0）
- .env.example 完整

### Step 6: 自测
启动后端并验证：
- [ ] uvicorn 正常启动
- [ ] http://localhost:8000/docs Swagger 可访问
- [ ] POST /api/auth/register 创建用户 → 返回 200 + tokens
- [ ] POST /api/auth/login 登录 → 返回 JWT
- [ ] GET /api/auth/me (带 Bearer Token) → 返回用户信息
- [ ] 重复注册同用户名 → 返回 422 错误

### Step 7: 输出报告
写入 reports/session-1-report.md，格式见全局约定。
```

---

# Session 2 — 全部业务 API

## 读取文档

```
02-blog-module.md
03-resources-module.md
04-downloads-module.md
05-chat-module.md
```

## 执行指令

```
你正在开发 FwindEmiko-Web 项目。Session 1 已完成认证模块。
请先阅读 02-blog-module.md、03-resources-module.md、
04-downloads-module.md、05-chat-module.md。

你的任务：在已有认证模块的基础上，完成全部业务 API。

当前项目已有：
- backend/app/main.py：FastAPI 入口（需要你注册新路由）
- backend/app/database.py：数据库引擎 + Base.metadata
- backend/app/modules/auth/：认证模块完整可用
- backend/app/core/security.py：密码哈希 + JWT

完成以下全部步骤：

### Step 1: 博客模块
- models.py：Post、Category、Tag、post_tags 关联表
- router.py：全部端点（列表/详情/CRUD/搜索）
- service.py：Markdown → HTML 渲染（content_md + content_html 双字段返回）
- 分类/标签端点 + 文章计数

### Step 2: 资源展示模块
- models.py：Resource、ResourceVersion、Screenshot
- router.py：全部端点（列表/详情/CRUD/版本/截图排序）
- 截图上传处理 + 缩略图生成
- 下载计数更新逻辑

### Step 3: 下载站模块
- models.py：Folder、FileNode、FolderPermission
- router.py：文件夹树/文件列表/下载/管理端点
- permission.py：角色权限检查函数（admin 全权限，guest 仅公开区）
- 默认权限规则（无 FolderPermission → 公开）

### Step 4: AI 对话模块
- models.py：ChatSession、ChatMessage、ChatQuota
- router.py：会话 CRUD + 消息发送 + SSE 流式端点
- llm_client.py：stream_chat() 占位（返回固定 mock 文本）
- 配额检查（admin 不限，其他 50次/天）

### Step 5: 注册路由到 main.py
所有新模块的 router 注册到 app.

### Step 6: 数据库迁移
生成并执行新迁移（新表）

### Step 7: 自测
用 curl 验证以下核心链路：
- [ ] POST /api/posts → 创建文章 → PUT 编辑 → DELETE 删除
- [ ] GET /api/posts?category=xxx&tag=xxx&q=关键词
- [ ] POST /api/resources → 添加版本 → 上传截图
- [ ] GET /api/downloads/folders（未登录只看到公开）
- [ ] POST /api/chat/sessions → POST /api/chat/sessions/1/messages（SSE 流式 mock 回复）
- [ ] 不同角色权限隔离正确

### Step 8: 输出报告
写入 reports/session-2-report.md
```

---

# Session 3 — Nuxt3 公网站点（前台）

## 读取文档

```
06-frontend-nuxt.md
```

## 执行指令

```
你正在开发 FwindEmiko-Web 项目。Session 1-2 已完成全部后端 API。
请先阅读 06-frontend-nuxt.md。

你的任务：使用 Nuxt 3 构建公网站点，包含博客、资源展示、下载站、AI 对话面板。

后端 API 运行在 http://localhost:8000/api，所有接口文档见 http://localhost:8000/docs。
项目根目录已有 packages/shared/ 和 packages/ui/ 空包。

完成以下全部步骤：

### Step 1: 共享包
- packages/shared/src/types/：所有 TypeScript 接口定义（User、Post、Resource 等，与后端模型对应）
- packages/shared/src/api/：Axios 封装（JWT 拦截器 + 统一错误处理 + 各模块 API 函数）
- packages/ui/src/glass/：GlassCard、GlassButton、GlassModal（TailwindCSS 玻璃磨砂）

### Step 2: Nuxt3 配置
- nuxt.config.ts：SSR/SSG 策略、TailwindCSS、Element Plus、Pinia、SEO
- tailwind.config.ts：颜色变量、backdropBlur、圆角、阴影扩展
- 全局 CSS 变量（深色/浅色）

### Step 3: 布局 + 导航
- layouts/default.vue（AppHeader + slot + AppFooter + Live2DWidget）
- AppHeader：Logo、导航链接、搜索框、登录/头像、主题切换
- 汉堡菜单（移动端）

### Step 4: 页面实现
- / (index.vue)：SSG，精选文章 + 热门资源
- /blog：ISR 1h，列表 + 分类/标签过滤 + 分页
- /blog/[slug]：SSG，详情 + SEO meta + 上一篇/下一篇
- /resources：ISR 24h，列表 + 类型/MC版本过滤
- /resources/[slug]：SSG，详情 + 截图画廊 + 版本列表 + 下载按钮
- /download：SSR，文件浏览器（文件夹树 + 文件列表 + 面包屑）
- /login、/register、/profile：CSR

### Step 5: AI 对话面板
- ChatPanel.vue：可折叠面板 + SSE 流式渲染 + 消息历史
- 未登录时面板隐藏

### Step 6: 响应式适配
- 所有页面在手机(<768px) / 平板 / 桌面三个断点正常显示
- 导航 → 汉堡菜单
- 资源卡片：3列→2列→1列
- 文件管理器：左右分栏→单栏

### Step 7: SEO
- @nuxtjs/sitemap 自动生成
- useSeoMeta 在文章/资源详情页
- robots.txt

### Step 8: 自测
- [ ] pnpm dev → http://localhost:3000 可访问所有页面
- [ ] 博客列表加载、详情渲染正常
- [ ] 资源列表 + 详情 + 下载按钮可用
- [ ] 下载站：未登录只看到公开文件夹，登录后看到更多
- [ ] 移动端（F12 模拟）所有页面正常
- [ ] 深色/浅色切换正常
- [ ] SEO meta 标签在页面源码中可见
- [ ] AI 对话面板可发送消息（mock 回复）

### Step 9: 输出报告
写入 reports/session-3-report.md
```

---

# Session 4 — Admin SPA（后台）

## 读取文档

```
07-frontend-admin.md
```

## 执行指令

```
你正在开发 FwindEmiko-Web 项目。Session 1-2 已完成全部后端 API。
请先阅读 07-frontend-admin.md。

你的任务：构建独立的 Admin SPA（Vite + Vue3 + CSR only）。

后端 API 运行在 http://localhost:8000/api。
packages/shared/ 和 packages/ui/ 已由 Session 3 完成，直接引用。

完成以下全部步骤：

### Step 1: 项目配置
- vite.config.ts：代理 /api → http://localhost:8000
- router/index.ts：所有路由 + 路由守卫（auth + role）
- TailwindCSS 集成 + Element Plus 按需引入

### Step 2: 布局
- AdminLayout.vue：侧边栏 + 顶部面包屑 + 主内容区
- AdminSidebar.vue：菜单（根据角色条件渲染）
- 移动端侧边栏自动折叠

### Step 3: 页面实现
- /login：登录表单 → JWT 存储 → 跳转
- / (DashboardView)：统计卡片 + 最近活动 + 快捷操作
- /posts、/posts/new、/posts/:id：
  - PostListView：筛选 + 批量操作
  - PostEditView：Vditor wysiwyg，Ctrl+S 保存，自动草稿缓存
- /resources、/resources/new、/resources/:id：
  - ResourceListView
  - ResourceEditView：三 Tab（基本信息/截图管理/版本管理）
- /files (FileManagerView)：
  - el-tree 文件夹树 + el-table 文件列表 + 面包屑
  - 右键菜单（下载/复制链接/删除）
  - 拖拽上传区域
- /users (UserManagerView)：admin only

### Step 4: 编辑器体验优化
- Ctrl+S 保存、Ctrl+Enter 发布、Esc 关闭弹窗
- 30s 自动草稿缓存（localStorage）
- 记忆上次选择的分类/标签/版本
- 模板功能：资源描述可保存/加载模板

### Step 5: 自测
- [ ] pnpm dev → 登录 → 仪表盘显示统计数据
- [ ] 新建文章 → Vditor 正常 → 存草稿 → 发布
- [ ] 新建资源 → 三 Tab 切换 → 截图拖拽上传排序 → 添加版本
- [ ] 文件管理 → 文件夹树展开 → 上传文件 → 右键菜单
- [ ] 路由守卫：未登录跳转登录页，非 admin 进不去 /users 和 /files
- [ ] 移动端侧边栏折叠
- [ ] npm run build 成功

### Step 6: 输出报告
写入 reports/session-4-report.md
```

---

# Session 5 — Live2D 集成

## 读取文档

```
08-live2d-integration.md
```

## 执行指令

```
你正在开发 FwindEmiko-Web 项目。Session 3 已完成 Nuxt3 公网站点。
请先阅读 08-live2d-integration.md。

你的任务：在 Nuxt3 公网站点中集成 Live2D 角色组件。

Nuxt3 项目在 nuxt-app/，已有 ChatPanel 组件和 Pinia stores/。

完成以下全部步骤：

### Step 1: 获取 Mao 模型
- Clone Live2D/CubismWebSamples
- 复制 Samples/Resources/Mao/ → nuxt-app/public/live2d/mao/
- 复制 Core/live2dcubismcore.min.js → nuxt-app/public/live2d/

### Step 2: 安装依赖
- pnpm add pixi.js@^7 pixi-live2d-display（在 nuxt-app 目录）
- 确认 live2dcubismcore.min.js 在 HTML 中预加载

### Step 3: 创建 Live2DWidget 组件
- components/live2d/Live2DWidget.vue
- ClientOnly 包裹（防 SSR 报错）
- PixiJS Application 初始化 + Mao 模型加载
- 右下角固定定位 + 响应式尺寸
- 拖拽移动（mousedown/move/up 或 useDraggable）

### Step 4: 交互实现
- 点击 → 随机 Tap 动作 + 随机气泡文本（3 秒消失）
- 鼠标悬停 → 视线跟随
- 对话模式 → 播放说话动画

### Step 5: 对话联动
- Pinia store（stores/live2d.ts）：isSpeaking, bubbleText
- ChatPanel 发消息 → SSE 流 → live2d store.speak(chunk)
- 对话结束 → idle()

### Step 6: 移动端适配
- <768px 时缩小到 140×200px
- 气泡文本截断更短

### Step 7: 自测
- [ ] pnpm dev → 右下角显示 Mao 角色
- [ ] 点击 → 动作 + 气泡
- [ ] 拖拽可移动
- [ ] 登录 → 发送 AI 消息 → 角色进入说话状态 + 气泡逐字显示
- [ ] 未登录 → 点击只显示静态气泡
- [ ] 移动端正常显示（缩小 + 可拖拽）

### Step 8: 输出报告
写入 reports/session-5-report.md
```

---

# 附录

## 最终项目结构（Trae 完成全部后）

```
FwindEmiko-Web/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   ├── middleware.py
│   │   ├── core/security.py
│   │   └── modules/
│   │       ├── auth/
│   │       ├── blog/
│   │       ├── resources/
│   │       ├── downloads/
│   │       ├── chat/
│   │       └── files/
│   ├── alembic/
│   ├── tests/
│   └── Dockerfile
├── nuxt-app/
│   ├── pages/
│   ├── components/
│   ├── composables/
│   ├── stores/
│   ├── public/live2d/
│   └── nuxt.config.ts
├── admin-spa/
│   ├── src/
│   │   ├── views/
│   │   └── components/
│   └── vite.config.ts
├── packages/
│   ├── shared/
│   └── ui/
├── 
│   ├── 00-overview.md
│   ├── 01-backend-core.md
│   ├── 02-blog-module.md
│   ├── 03-resources-module.md
│   ├── 04-downloads-module.md
│   ├── 05-chat-module.md
│   ├── 06-frontend-nuxt.md
│   ├── 07-frontend-admin.md
│   ├── 08-live2d-integration.md
│   ├── 09-deployment.md
│   └── reports/
│       ├── session-1-report.md
│       ├── session-2-report.md
│       ├── session-3-report.md
│       ├── session-4-report.md
│       └── session-5-report.md
├── windemiko-portal-design.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
├── Makefile
└── pnpm-workspace.yaml
```

## 报告模板

```markdown
# Session N — 实现报告

## 完成功能
- [具体功能列表]

## 与文档的差异（灵活调整）
- [调整了什么 / 为什么]

## 遇到的问题 & 解决
- [问题描述] → [解决方式]

## 已知限制
- [未完成的功能 / 需要注意的点]

## 自测结果
- [ ] 测试项1: 通过
- [ ] 测试项2: 通过
- [ ] 测试项3: 有瑕疵（说明）

## 下一会话依赖
- [下一会话需要什么已就绪]
```

---

> **给汐汐酱的说明**  
> 1. 创建 `reports/` 空目录  
> 2. 按顺序开 Trae 会话，复制对应 Session 的「执行指令」粘贴  
> 3. Session 3 和 4 可同时开两个窗口并行跑  
> 4. 全部完成后告诉我 → 我接手部署
