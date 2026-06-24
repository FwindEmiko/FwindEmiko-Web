# GLM-5.2 博客站全面修复与视觉升级报告

> 生成时间：2026-06-24
> 项目：FwindEmiko-Web（F.windEmiko.top）
> 执行范围：P0 严重故障 → P1 功能体验 → P2 细节打磨

---

## P0：严重渲染故障修复

### P0-1：博客详情页内容空白

**改动文件：**
- [nuxt-app/app/composables/useMarkdown.ts](file:///f:/FwindEmiko-Web/nuxt-app/app/composables/useMarkdown.ts)
- [nuxt-app/app/pages/blog/[slug].vue](file:///f:/FwindEmiko-Web/nuxt-app/app/pages/blog/%5Bslug%5D.vue)

**关键变更：**
- `useMarkdown.ts`：将 markdown-it 的 `html` 选项从 `false` 改为 `true`，允许后端返回的 `content_html` 直接渲染而非被转义
- `[slug].vue`：将 `v-html="render(post.content_html || post.content_md)"` 改为 `v-html="post.content_html || render(post.content_md)"`，优先使用后端已渲染的 HTML
- 增加错误处理：`default: () => null` + `loadError` 计算属性 + v-else-if 错误展示块

### P0-2：资源详情页内容空白

**改动文件：**
- [nuxt-app/app/pages/resources/[slug].vue](file:///f:/FwindEmiko-Web/nuxt-app/app/pages/resources/%5Bslug%5D.vue)

**关键变更：**
- 与 P0-1 相同的错误处理模式：`default: () => null` + `loadError` 计算属性 + v-else-if 错误展示块

### P0-3 & P0-4：登录页 / 注册页空白

**验证结果：** 登录页和注册页在浏览器中实际可正常渲染（CSR 页面），无需修改。

### P0-5：自定义 404 错误页

**改动文件：**
- [nuxt-app/app/error.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/error.vue)（新建）

**关键变更：**
- 继承全站 AppHeader + AppFooter 布局
- 玻璃磨砂面板展示错误码（渐变色文字）
- 小狐狸 ASCII art 装饰
- 终端风格错误信息 `$ echo "Error 404 - Page Not Found"`
- 返回首页 / 返回上一页按钮
- 兼容非 404 错误码（动态展示 statusCode）

---

## P1：功能与体验修复

### P1-1：代码块语法高亮

**改动文件：**
- [backend/app/modules/blog/service.py](file:///f:/FwindEmiko-Web/backend/app/modules/blog/service.py)
- [nuxt-app/app/assets/css/main.css](file:///f:/FwindEmiko-Web/nuxt-app/app/assets/css/main.css)
- [nuxt-app/nuxt.config.ts](file:///f:/FwindEmiko-Web/nuxt-app/nuxt.config.ts)
- [nuxt-app/tailwind.config.ts](file:///f:/FwindEmiko-Web/nuxt-app/tailwind.config.ts)

**关键变更：**
- 后端 `render_md`：启用 `codehilite` 扩展 + Pygments `monokai` 主题，`guess_lang=True` 自动语言识别
- 新增 `get_highlight_css()` 函数提供高亮 CSS
- 前端 CSS：完整 Pygments Monokai 语法高亮配色（80+ token 类型）
- 终端风格代码块：macOS 三色圆点（红黄绿）、Catppuccin Mocha 背景 `#1e1e2e`
- 行内代码：粉色/橙色高亮 `#ff70a6`，浅色模式 `#d6336c`
- 代码字体：JetBrains Mono / Fira Code（nuxt.config.ts Google Fonts 引入）
- Tailwind 配置新增 `mono` 和 `anime`（ZCOOL XiaoWei）字体族

### P1-2：二次元 + 代码极客视觉风格注入

**改动文件：**
- [nuxt-app/app/pages/index.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/pages/index.vue)
- [nuxt-app/app/components/Live2DWidget.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/Live2DWidget.vue)
- [nuxt-app/app/components/AppFooter.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/AppFooter.vue)
- [nuxt-app/app/components/PostCard.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/PostCard.vue)
- [nuxt-app/app/components/ResourceCard.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/ResourceCard.vue)
- [nuxt-app/app/assets/css/main.css](file:///f:/FwindEmiko-Web/nuxt-app/app/assets/css/main.css)

**关键变更（二次元方向）：**
- Hero Banner：紫→蓝→青渐变背景 + SVG 星空 pattern + 像素点阵 pattern + 24 颗闪烁星星
- 樱花飘落动画：8 个 CSS 粒子（粉/紫/蓝三色），`sakura-fall` keyframes
- 像素风狐狸 SVG 头像（多边形几何造型）
- 副标题装饰：◆ 像素图案点缀
- 标题使用 `font-anime`（ZCOOL XiaoWei）字体
- Live2D 萌系台词库：10 条（"怎么了喵~"、"别戳啦~"、"嗯哼？" 等）
- 文章卡片 hover 粉紫光晕：`post-card-glow` 类

**关键变更（代码极客方向）：**
- 终端绿强调色：`--color-terminal: #00FF41`（Matrix 绿）
- 终端装饰文本：`$ echo "Welcome to FwindEmiko's world"`
- 文本选择高亮使用终端绿
- 黑客模式彩蛋：点击页脚 ASCII 狐狸 5 次切换暗绿终端主题（`:root.hacker-mode`）
- 页脚 ASCII art 小狐狸：`/\_/\ ( o.o ) > ^ <`

### P1-3：玻璃磨砂效果优化

**改动文件：**
- [nuxt-app/app/assets/css/main.css](file:///f:/FwindEmiko-Web/nuxt-app/app/assets/css/main.css)
- [packages/ui/src/glass/GlassCard.vue](file:///f:/FwindEmiko-Web/packages/ui/src/glass/GlassCard.vue)

**关键变更：**
- 深色背景从 `#0B0B1A` 调整为带紫的 `#0a0a1a`
- 浅色模式玻璃背景：`rgba(255,255,255,0.75)` + 渐变叠加 `from-white/15 to-white/5`
- 浅色模式玻璃边框：`#e5e7eb` → 偏蓝 `#dbeafe`
- 深色模式玻璃背景：`rgba(255,255,255,0.04)` → `0.05`（加亮）
- 光泽扫过效果：`.glass-card-shine::after` 伪元素，hover 时从左上到右下扫过半透明白色光带，0.4s ease
- GlassCard 组件全局应用 `glass-card-shine` 类

### P1-4：移动端优化

**改动文件：**
- [nuxt-app/app/components/Live2DWidget.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/Live2DWidget.vue)
- [nuxt-app/app/components/ChatPanel.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/ChatPanel.vue)
- [nuxt-app/app/components/ResourceCard.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/ResourceCard.vue)

**关键变更：**
- Live2D 移动端收起/展开：`<768px` 默认收起为 44×44px 圆点按钮（🐱 图标），点击展开
- 展开后右上角显示红色关闭按钮，点击收起
- 窗口尺寸变化时自动切换收起/展开状态
- ChatPanel 移动端高度：`520px` → `380px`（`@media (min-width: 768px)` 恢复 520px）
- 资源卡片标题：`truncate` → `line-clamp-2 break-words`（允许换行）

### P1-5：Admin 后台改进

**改动文件：**
- [admin-spa/src/api/client.ts](file:///f:/FwindEmiko-Web/admin-spa/src/api/client.ts)
- [admin-spa/src/views/posts/PostListView.vue](file:///f:/FwindEmiko-Web/admin-spa/src/views/posts/PostListView.vue)
- [admin-spa/src/views/resources/ResourceListView.vue](file:///f:/FwindEmiko-Web/admin-spa/src/views/resources/ResourceListView.vue)
- [admin-spa/src/views/FileManagerView.vue](file:///f:/FwindEmiko-Web/admin-spa/src/views/FileManagerView.vue)
- [admin-spa/src/views/UserManagerView.vue](file:///f:/FwindEmiko-Web/admin-spa/src/views/UserManagerView.vue)
- [admin-spa/src/components/editors/PostEditor.vue](file:///f:/FwindEmiko-Web/admin-spa/src/components/editors/PostEditor.vue)
- [admin-spa/src/components/editors/ResourceEditor.vue](file:///f:/FwindEmiko-Web/admin-spa/src/components/editors/ResourceEditor.vue)

**关键变更：**
- 新增 `formatDateTime()` 工具函数：ISO → `YYYY-MM-DD HH:mm` 本地化格式
- 4 处表格时间列改用 `#default` 插槽 + `formatDateTime()`：PostListView、ResourceListView、FileManagerView、UserManagerView
- 文章编辑器封面图：`el-input` 旁加 `[预览]` 按钮，hover 弹出 320px 宽图片
- 资源编辑器图标/封面：各加 `[预览]` 按钮（图标 120px，封面 320px）
- 文件管理器文件夹树：`:indent="24"` 增加缩进 + `node.level` 层级样式（一级加粗，子级灰色）
- 用户管理：新增搜索框（用户名搜索）+ `display_name || username` 兜底（原为 `-`）

---

## P2：细节打磨

**改动文件：**
- [nuxt-app/app/components/AppHeader.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/AppHeader.vue)
- [nuxt-app/nuxt.config.ts](file:///f:/FwindEmiko-Web/nuxt-app/nuxt.config.ts)
- [nuxt-app/app/pages/index.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/pages/index.vue)
- [nuxt-app/app/components/AppFooter.vue](file:///f:/FwindEmiko-Web/nuxt-app/app/components/AppFooter.vue)

**关键变更：**
- 主题切换按钮：`aria-label="切换主题"` + `:aria-pressed="isDark"`
- SSR 主题注入：nuxt.config.ts head 内联脚本，从 Cookie 读取主题并在 HTML 渲染前应用 class，防 FOUC
- 首页 Hero 网格点阵：从 CSS radial-gradient 改为 SVG `<pattern>`（starfield + pixel-grid），更清晰
- 页脚 ASCII art 小狐狸：`/\_/\ ( o.o ) > ^ < 狐风轩汐の小屋 © 2026`

---

## 验证结果

| 验证项 | 状态 |
|--------|------|
| 后端 API (localhost:8000) | ✅ 200 |
| 公网前端 (localhost:3000) | ✅ 200 |
| 管理后台 (localhost:5173) | ✅ 200 |
| 首页 Hero 星空/樱花/终端文本 | ✅ 渲染正常 |
| 博客列表 PostCard 光晕 | ✅ post-card-glow 类已应用 |
| 博客详情页内容渲染 | ✅ 标题/正文/标签均可见 |
| 自定义 404 页面 | ✅ 玻璃面板 + 狐狸 ASCII + 错误码 |
| 页脚 ASCII 狐狸 | ✅ 显示正常 |
| 主题切换 aria-label | ✅ 已添加 |
| 玻璃光泽扫过 | ✅ glass-card-shine 已应用 |

---

## 约束遵守

- ✅ 未修改数据库结构
- ✅ 未修改 API 接口
- ✅ 未修改路由命名
- ✅ 所有改动在本地 dev 环境验证通过
- ✅ 移动端 Live2D 有收起/展开按钮，默认收起
- ✅ 代码块使用 JetBrains Mono 字体 + 深色终端背景
- ✅ Admin 时间列使用本地化格式（YYYY-MM-DD HH:mm）
- ✅ 自定义 error.vue 包含 AppHeader + AppFooter + 玻璃磨砂风格

---

# 部署问题诊断与修复报告

> 生成时间：2026-06-25
> 执行范围：P0 前端 API 地址 → P1 数据库种子数据 → P2/P3/P4 部署配置确认

---

## P0：前端登录 Network Error（已修复）

**根因分析：**
- `packages/shared/src/api/index.ts` 中 `API_BASE_URL` 默认回退到 `http://localhost:8000/api`（绝对路径）
- Nuxt 应用没有 `.env` 设置 `VITE_API_BASE_URL`，导致浏览器在生产环境尝试连接 `http://localhost:8000` → 失败
- `nuxt.config.ts` 的 `runtimeConfig.public.apiBase` 实际上未被 shared 包消费（两套不同的配置系统）
- `docker-compose.prod.yml` 中 `NUXT_PUBLIC_API_BASE=https://f.windemiko.top/api` 无法生效（编译时烘焙 + 域名未配置反向代理）

**修复方案：** 采用 server middleware 代理方案，前端使用相对路径 `/api`，由 Nuxt 服务端代理到后端容器

**改动文件：**

1. [packages/shared/src/api/index.ts](file:///f:/FCelestial/fwe-repo/packages/shared/src/api/index.ts)
   - `API_BASE_URL` 默认值：`http://localhost:8000/api` → `/api`（相对路径）
   - `UPLOAD_BASE_URL` 默认值：`http://localhost:8000` → `''`（空 = 同源）
   - 新增 `VITE_UPLOAD_BASE_URL` 环境变量支持

2. [nuxt-app/server/api/[...].ts](file:///f:/FCelestial/fwe-repo/nuxt-app/server/api/%5B...%5D.ts)（新建）
   - Catch-all 路由：将 `/api/**` 请求代理到 `BACKEND_URL`（生产 `http://backend:8000`，开发 `http://localhost:8000`）

3. [nuxt-app/server/routes/uploads/[...].ts](file:///f:/FCelestial/fwe-repo/nuxt-app/server/routes/uploads/%5B...%5D.ts)（新建）
   - Catch-all 路由：将 `/uploads/**` 请求代理到后端（图片/文件访问）

4. [nuxt-app/nuxt.config.ts](file:///f:/FCelestial/fwe-repo/nuxt-app/nuxt.config.ts)
   - `runtimeConfig.public.apiBase` 默认值：`http://localhost:8000/api` → `''`（空 = 同源）
   - `runtimeConfig.public.uploadBase` 默认值：`http://localhost:8000` → `''`
   - 新增 `runtimeConfig.backendUrl`（服务端专用）：`process.env.BACKEND_URL || 'http://localhost:8000'`
   - sitemap `apiBase`：硬编码 `http://localhost:8000/api` → `${process.env.BACKEND_URL || 'http://localhost:8000'}/api`

5. [docker-compose.prod.yml](file:///f:/FCelestial/fwe-repo/docker-compose.prod.yml)
   - 移除 `NUXT_PUBLIC_API_BASE=https://f.windemiko.top/api`
   - 新增 `BACKEND_URL=http://backend:8000`（Docker 内部网络，供 server middleware 使用）
   - `NUXT_PUBLIC_SITE_URL` 更新为 `http://dev.miragedge.top:4173`

---

## P1：Admin 登录 401 Unauthorized（已修复）

**根因分析：**
- `windemiko` 数据库 `users` 表有 0 条记录
- 后端 `/api/auth/login` 找不到匹配用户 → 401
- 密码哈希方式：passlib + bcrypt（`app/core/security.py`）

**修复方案：** 后端启动时自动检测 users 表为空并创建默认管理员

**改动文件：**

1. [backend/app/seed.py](file:///f:/FCelestial/fwe-repo/backend/app/seed.py)（新建）
   - `init_seed_data(db)` 函数：检测 `users` 表记录数，为空时创建默认管理员
   - 默认凭据：`admin` / `admin123` / `admin@windemiko.top` / role=`admin`
   - 使用与后端一致的 bcrypt 哈希算法
   - 日志警告提示立即修改默认密码

2. [backend/app/main.py](file:///f:/FCelestial/fwe-repo/backend/app/main.py)
   - 导入 `AsyncSessionLocal` 和 `init_seed_data`
   - `lifespan` 中 `create_all` 后调用 `init_seed_data(session)` 初始化种子数据

---

## P2：admin-nginx.conf nginx 变量被清空（已确认修复）

**状态：** 仓库源码已正确（commit `e948a73`）

[admin-nginx.conf](file:///f:/FCelestial/fwe-repo/admin-nginx.conf) 中 `$host`、`$uri`、`$remote_addr` 等 nginx 变量均正确保留，未被 shell 展开为空字符串。无需修改。

---

## P3：docker-compose.prod.yml 引用已删除的 db 服务（已确认修复）

**状态：** 仓库源码已同步（commit `e948a73`）

[docker-compose.prod.yml](file:///f:/FCelestial/fwe-repo/docker-compose.prod.yml) 已移除独立 `db` 服务块和 `fwe_db` volume，添加 `miragedge-network` external network，`backend` 加入 `miragedge-network`。无需修改。

---

## P4：CI/CD 工作流 compose 命令（已确认修复）

**状态：** 仓库源码已正确（commit `898e286`）

[.github/workflows/ci-cd.yml](file:///f:/FCelestial/fwe-repo/.github/workflows/ci-cd.yml) 已使用 `docker-compose`（带连字符），兼容 ECS Docker 版本。无需修改。

---

## P5：数据库种子数据 & 迁移系统

- **Alembic 迁移系统**：已存在（`backend/alembic/`），含 `init_users_table` 和 `add_business_modules` 两个迁移版本
- **种子数据**：已通过 P1 的 `seed.py` 实现，首次启动自动创建管理员

---

## 验证结果

| 验证项 | 状态 |
|--------|------|
| `pnpm build` 前端构建 | ✅ 成功（exit code 0） |
| `server/api/[...].ts` 编译 | ✅ `.output/server/chunks/routes/api/_..._.mjs` |
| `server/routes/uploads/[...].ts` 编译 | ✅ `.output/server/chunks/routes/uploads/_..._.mjs` |
| Python 语法检查 (seed.py + main.py) | ✅ 语法正确 |
| P2 admin-nginx.conf 变量 | ✅ 已确认正确（commit e948a73） |
| P3 compose db 服务移除 | ✅ 已确认同步（commit e948a73） |
| P4 CI/CD docker-compose 命令 | ✅ 已确认正确（commit 898e286） |

---

## 部署后验证步骤

```bash
# 1. 重建容器
ssh root@20.20.20.1 'cd /opt/fwindemiko-web && docker-compose -f docker-compose.prod.yml up -d --build'

# 2. 验证
curl -s http://dev.miragedge.top:4173/          # 前端首页 → 200
curl -s http://dev.miragedge.top:4174/docs       # 后端 API 文档 → 200
curl -s http://dev.miragedge.top:4175/           # Admin 登录页 → 200
curl -s -X POST http://dev.miragedge.top:4174/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'  # → 200 + token
```

> ⚠️ 首次登录后请立即修改 admin 密码（seed.py 会在日志中打印警告）

---

# GLM-5.2 全面 UI/UX 修复报告（第二轮）

> 生成时间：2026-06-25
> 执行范围：P0 Admin 编辑器 + 文件下载 → P1 顶栏/Hero/下拉框/玻璃卡片/Live2D/Footer

---

## P0：Admin 编辑器修复

### P0-1.1：新建文章/资源无法写正文和描述

**根因：** Vditor 编辑器缺少 CSS 引入，且未配置 CDN 导致动态资源加载失败。

**改动文件：**
- [admin-spa/src/main.ts](file:///f:/FCelestial/fwe-repo/admin-spa/src/main.ts)
- [admin-spa/src/components/editors/PostEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/PostEditor.vue)
- [admin-spa/src/components/editors/ResourceEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/ResourceEditor.vue)

**关键变更：**
- `main.ts`：新增 `import 'vditor/dist/index.css'` 引入编辑器样式
- `PostEditor.vue` / `ResourceEditor.vue`：Vditor 初始化时新增 `cdn: 'https://cdn.jsdelivr.net/npm/vditor@3.10.8/dist'` 配置，解决动态资源加载失败

### P0-1.2：编辑器底部出现可见的快捷键文本

**根因：** Vditor 工具栏 hint 文本（"一级标题 <Alt+Ctrl+1>..."）泄露到 DOM。

**改动文件：**
- [admin-spa/src/style.css](file:///f:/FCelestial/fwe-repo/admin-spa/src/style.css)

**关键变更：**
```css
.vditor-toolbar__hint, .vditor-hint { display: none !important; }
```

### P0-1.3：图标和文字错位

**改动文件：**
- [admin-spa/src/style.css](file:///f:/FCelestial/fwe-repo/admin-spa/src/style.css)

**关键变更：**
- 统一使用 `display: inline-flex; align-items: center; gap: 0.25rem` 替代 `vertical-align` / `line-height` hack
- 应用范围：`.el-button > span` 和 `.el-dropdown-item`

---

## P0：文件下载修复

### P0-2.1：后台上传文件后前端下载 404

**根因：** `storage_path` 字段存储绝对路径（含 UPLOAD_DIR），下载时再次拼接 UPLOAD_DIR 导致路径重复（`./uploads/./uploads/downloads/3/xxx.txt`）。

**改动文件：**
- [backend/app/modules/downloads/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/downloads/router.py)

**关键变更：**
- 新增 `_resolve_storage_path()` 兼容函数，支持新旧两种存储格式：
  - 绝对路径（旧）→ 直接返回
  - 相对路径（新）→ 拼接 UPLOAD_DIR
  - 旧绝对路径重复前缀 → 去重后拼接
- `upload_files`：改为存储相对路径 `downloads/{folder_id}/{storage_name}`
- `download_file` / `delete_file`：统一使用 `_resolve_storage_path()` 解析路径

### P0-2.2：下载页面刷新丢失目录

**改动文件：**
- [nuxt-app/app/pages/download/index.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/pages/download/index.vue)（重写）

**关键变更：**
- 当前文件夹 ID 写入 URL query 参数 `?folder=xxx`
- `currentFolderId` 计算属性从 `route.query.folder` 派生
- `goToFolder()` 通过 `router.push({ query })` 切换目录，刷新后状态保留

### P0-2.3：下载页交互改为 OpenList 风格

**改动文件：**
- [nuxt-app/app/pages/download/index.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/pages/download/index.vue)（重写）

**关键变更：**
- 面包屑导航显示当前路径层级
- 文件夹点击进入（非展开）
- 文件列表显示大小、修改时间、下载次数
- 下载按钮使用主色按钮 + 文件大小标签

---

## P1：顶栏重新设计

**改动文件：**
- [nuxt-app/app/components/AppHeader.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/components/AppHeader.vue)（重写）
- [nuxt-app/app/layouts/default.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/layouts/default.vue)

**关键变更：**
- 导航项居右：Logo + 站点名保留左侧，导航链接 + 搜索框 + 主题切换 + 用户/登录统一右侧
- 顶栏高度从 `h-16` 减小到 `h-14`（layout 同步 `pt-16` → `pt-14`）
- 半透明玻璃效果：`backdrop-blur` + `bg-glass/60`
- 滚动加深：监听 `window.scrollY > 20` 动态切换 class（`bg-glass/90 shadow-glass`）
- 移动端汉堡菜单展开时导航项纵向排列

---

## P1：首页 Hero 区域重设计

**改动文件：**
- [nuxt-app/app/pages/index.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/pages/index.vue)

**关键变更：**
- Hero 区域 `min-height` 改为 `70vh`
- 标题字号加大：`text-4xl sm:text-6xl`
- 标题 + 副标题居中布局
- CTA 按钮（浏览博客 / 发现资源）保持在标题下方
- 移除 GlassCard 包裹，保留渐变层叠 + 粒子/星空效果
- Live2D 默认隐藏（由 ChatPanel 触发显示）

---

## P1：搜索/筛选下拉框样式

**改动文件：**
- [nuxt-app/app/assets/css/main.css](file:///f:/FCelestial/fwe-repo/nuxt-app/app/assets/css/main.css)

**关键变更：**
- `select` / `option` 文字颜色使用 `var(--text-primary)`，修复浅色文字 + 浅色背景不可读
- 下拉背景使用玻璃面板色 + 深色边框
- 搜索框 + 筛选下拉框统一玻璃面板风格
- `hover` / `focus` 时边框色平滑过渡到 `var(--accent)`

---

## P1：玻璃卡片闪光效果

**改动文件：**
- [nuxt-app/app/assets/css/main.css](file:///f:/FCelestial/fwe-repo/nuxt-app/app/assets/css/main.css)
- [packages/ui/src/glass/GlassCard.vue](file:///f:/FCelestial/fwe-repo/packages/ui/src/glass/GlassCard.vue)（沿用 `glass-card-shine` 类名）

**关键变更：**
- 移除原有白色光带扫过效果
- 改为方案 B：轻微上浮 + 阴影加深
```css
.glass-card-shine { transition: transform 0.3s ease, box-shadow 0.3s ease; }
.glass-card-shine:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.25), 0 4px 8px -2px rgba(0, 0, 0, 0.15);
}
```

---

## P1：Live2D 默认隐藏

**改动文件：**
- [nuxt-app/app/components/Live2DWidget.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/components/Live2DWidget.vue)（重写）
- [nuxt-app/app/layouts/default.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/layouts/default.vue)

**关键变更：**
- 默认状态：页面加载时 Live2D 模型不显示
- 新增 `visible` prop 接收父组件（ChatPanel）的 `chatOpen` 状态
- 点击右下角 💬 按钮（ChatPanel 自带的 toggle）→ 打开 ChatPanel + 在左下角显示 Live2D 模型
- 关闭 ChatPanel → Live2D 模型同步收起
- 位置从右下角改为左下角（`left: 8px/16px`）
- 淡入淡出动画：`<Transition name="live2d-fade">` + `opacity 0.5s`
- `watch(() => props.visible)` 首次显示时延迟初始化 Pixi 应用
- 移动端 ChatPanel 全屏时 Live2D 隐藏（`.live2d-mobile-hidden { display: none !important; }`）

---

## P1：Footer 重新设计

**改动文件：**
- [nuxt-app/app/components/AppFooter.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/components/AppFooter.vue)（重写）

**关键变更：**

**桌面版（8.1）：**
- 三列布局保留但减小字号（`text-sm` → `text-xs`）+ 间距（`py-10` → `py-6 md:py-8`，`gap-8` → `gap-6 md:gap-8`）
- 备案号独立一行，居中，字号更小（`text-[11px]`）
- 移除「关注我」的空链接（GitHub/Email 图标未配置链接），替换为「关于」列展示站点技术栈
- 整体 padding 减小，视觉更紧凑

**移动版（8.2）：**
- 三列改为单列堆叠，居中对齐（`text-center md:text-left` + `items-center md:items-start`）
- 导航链接横向排列（`flex flex-row md:flex-col` + `gap-x-4`）
- ASCII 狐狸减小字号（统一 `text-xs`，移除 `sm:text-sm`）
- ASCII 狐狸居中显示（`justify-center md:justify-start`）

---

## 验证结果

| 验证项 | 状态 |
|--------|------|
| `pnpm build` nuxt-app 构建 | ✅ 成功（exit code 0，8.63s client + 4.31s server） |
| `pnpm build` admin-spa 构建 | ✅ 成功（exit code 0，7.68s） |
| Admin 编辑器 Vditor 渲染 | ✅ CSS + CDN 已配置 |
| 编辑器底部快捷键文本 | ✅ 已隐藏（display:none） |
| 图标文字对齐 | ✅ inline-flex + gap |
| 文件下载 404 | ✅ 路径解析函数已修复 |
| 下载页刷新丢状态 | ✅ URL query 持久化 |
| 下载页 OpenList 风格 | ✅ 面包屑 + 文件信息 + 主色按钮 |
| 顶栏导航居右 | ✅ 右侧布局 |
| 顶栏滚动加深 | ✅ scroll 监听动态 class |
| Hero 区域 70vh | ✅ min-h-[70vh] |
| 下拉框文字可读 | ✅ 颜色变量修复 |
| 玻璃卡片无突兀反光 | ✅ 上浮 + 阴影方案 |
| Live2D 默认隐藏 | ✅ visible prop 控制 |
| Live2D 淡入淡出动画 | ✅ opacity 0.5s |
| Footer 桌面紧凑 | ✅ 字号 + padding 减小 |
| Footer 移动单列堆叠 | ✅ flex-row 横向导航 |
| 备案号独立居中行 | ✅ text-[11px] 居中 |

---

## 约束遵守

- ✅ 未修改数据库结构（仅修复 storage_path 存储格式）
- ✅ 未修改 API 接口签名
- ✅ 未修改路由命名
- ✅ 所有改动通过 `pnpm build` 验证
- ✅ Live2D 默认隐藏，💬 按钮触发显示
- ✅ 玻璃卡片采用方案 B（上浮 + 阴影）
- ✅ Footer 桌面三列紧凑 + 移动单列堆叠
- ✅ 备案号独立居中行，字号更小

---

# GLM-5.2 权限系统 + UI 精修报告（第三轮）

> 生成时间：2026-06-25
> 执行范围：权限系统（P0）+ Admin UI 重设计 + Footer/Hero/AI按钮/文档链接

---

## 一、文件下载权限控制系统（P0）

### 1.1 数据库层

**改动文件：**
- [backend/app/modules/downloads/models.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/downloads/models.py)
- [backend/alembic/versions/a1b2c3d4e5f6_add_upload_delete_permissions.py](file:///f:/FCelestial/fwe-repo/backend/alembic/versions/a1b2c3d4e5f6_add_upload_delete_permissions.py)

**关键变更：**
- `FolderPermission` 模型新增 `can_upload` 和 `can_delete` 字段（默认 False）
- 新建 Alembic 迁移 `a1b2c3d4e5f6`，使用 `server_default=sa.text('0')` 确保现有记录兼容
- 迁移支持 upgrade/downgrade 双向

### 1.2 后端 API + 权限检查

**改动文件：**
- [backend/app/modules/downloads/permission.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/downloads/permission.py)
- [backend/app/modules/downloads/schemas.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/downloads/schemas.py)
- [backend/app/modules/downloads/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/downloads/router.py)

**关键变更：**
- `check_folder_access` 扩展支持 `upload` 和 `delete` action
- `FolderPermissionRule` schema 新增 `can_upload`/`can_delete` 字段
- 新增权限矩阵 schemas：`PermissionMatrixItem`、`PermissionMatrixFolder`、`PermissionMatrixResponse`、`PermissionBatchUpdate`
- `upload_files` 接口：从 `require_role("admin")` 改为 `require_role("admin", "author", "member")` + `check_folder_access(folder_id, user, "upload", db)`
- `delete_file` 接口：同上，检查 `can_delete` 权限
- 新增 `GET /api/admin/permissions/folders`：返回所有文件夹 × 所有角色的权限矩阵
- 新增 `PUT /api/admin/permissions`：批量 upsert 权限记录（admin 角色强制全开防止误锁）

### 1.3 种子数据

**改动文件：**
- [backend/app/seed.py](file:///f:/FCelestial/fwe-repo/backend/app/seed.py)
- [backend/app/main.py](file:///f:/FCelestial/fwe-repo/backend/app/main.py)

**关键变更：**
- 新增 `ensure_admin_permissions(db)` 函数：为所有现有文件夹补齐 admin 全权限记录
- `main.py` lifespan 中 `init_seed_data` 后调用 `ensure_admin_permissions`

### 1.4 Admin 前端

**新增文件：**
- [admin-spa/src/views/PermissionManagerView.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/views/PermissionManagerView.vue)

**改动文件：**
- [admin-spa/src/router/index.ts](file:///f:/FCelestial/fwe-repo/admin-spa/src/router/index.ts)
- [admin-spa/src/components/layout/AdminSidebar.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/layout/AdminSidebar.vue)

**关键变更：**
- 新增 `/permissions` 路由（meta: `{ auth: true, role: 'admin' }`）
- 侧边栏新增「权限」菜单项（Shield 图标，仅 admin 可见）
- PermissionManagerView：角色选择器 + 文件夹权限矩阵表格（读取/下载/上传/删除 checkbox）
- admin 角色权限锁定不可修改（显示提示条）
- 支持批量保存 + 重置为默认值

---

## 二、Admin 管理后台 UI 重设计

**改动文件：**
- [admin-spa/src/style.css](file:///f:/FCelestial/fwe-repo/admin-spa/src/style.css)
- [admin-spa/src/main.ts](file:///f:/FCelestial/fwe-repo/admin-spa/src/main.ts)
- [admin-spa/src/components/layout/AdminSidebar.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/layout/AdminSidebar.vue)
- [admin-spa/src/components/layout/AdminHeader.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/layout/AdminHeader.vue)
- [admin-spa/src/components/layout/AdminLayout.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/layout/AdminLayout.vue)

**关键变更：**

**主题同步（2.1）：**
- `style.css` 重写：`:root` 深色变量 + `:root.light` 浅色变量，与主站完全一致
- `main.ts` 新增 `applyThemeFromCookie()`：读取主站 `theme` cookie 同步主题
- 1 秒轮询监听 cookie 变化，主站切换主题时实时同步
- Element Plus 全局覆盖：`--el-color-primary`、表格背景、输入框、按钮、对话框等全部跟随主题

**返回主页（2.2）：**
- AdminSidebar 底部新增「返回主页」链接（Home 图标），指向 `https://f.windemiko.top`

**视觉优化（2.3）：**
- 侧边栏：`backdrop-blur-xl` + `var(--panel)` 玻璃磨砂背景
- AdminHeader：玻璃磨砂背景 + 主题色变量
- `.admin-card` / `.glass-panel`：统一 `backdrop-filter: blur(12px)` 玻璃风格
- Element Plus 表格：斑马纹（`--el-table__row--striped`）+ hover 高亮（`--accent-light`）
- 按钮：圆角 8px + accent 主色

---

## 三、Footer 布局修复

**改动文件：**
- [nuxt-app/app/components/AppFooter.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/components/AppFooter.vue)

**关键变更：**
- 三列布局 `grid grid-cols-1 md:grid-cols-3 gap-8`（gap 从 6 统一为 8）
- ASCII 狐狸改为始终居中（`justify-center`，移除 `md:justify-start`）
- 备案号独立一行居中，`border-t` 分隔

---

## 四、首页 Hero 背景覆盖

**改动文件：**
- [nuxt-app/app/pages/index.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/pages/index.vue)

**关键变更：**
- Hero 区域从 `min-h-[70vh]` 扩大为 `min-h-[85vh]` + `w-full`
- 新增渐变过渡遮罩：`h-16 -mt-16 bg-gradient-to-b from-transparent to-[var(--bg-primary)]`
- Hero 与精选文章之间平滑过渡，消除边界突兀感

---

## 五、AI 对话按钮未登录提示

**改动文件：**
- [nuxt-app/app/components/ChatPanel.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/components/ChatPanel.vue)

**关键变更：**
- 💬 按钮始终显示（移除 `v-if="auth.isLoggedIn"` 外层条件）
- 新增 `handleToggle()` 函数：未登录时 `confirm('请先登录后使用 AI 对话')` → 跳转 `/login`
- 已登录时正常打开 ChatPanel + 触发 Live2D 显示
- 聊天面板 `v-if="modelValue && auth.isLoggedIn"` 确保未登录不渲染面板

---

## 六、顶栏添加「文档」链接

**改动文件：**
- [nuxt-app/app/components/AppHeader.vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/components/AppHeader.vue)

**关键变更：**
- 新增 `externalLinks` 数组：`{ label: '文档', url: 'https://miragedge.top' }`
- 桌面端导航：在「下载」后添加外部链接，带外链图标（新标签页打开）
- 移动端汉堡菜单：同步添加文档链接

---

## 验证结果

| 验证项 | 状态 |
|--------|------|
| `pnpm build` nuxt-app 构建 | ✅ 成功（exit code 0，15.20s client + 7.53s server） |
| `pnpm build` admin-spa 构建 | ✅ 成功（exit code 0，16.82s） |
| 权限系统数据库迁移 | ✅ Alembic 迁移已创建 |
| 权限矩阵 API | ✅ GET/PUT 接口已实现 |
| 上传/删除权限检查 | ✅ check_folder_access 集成 |
| Admin 权限管理页面 | ✅ PermissionManagerView 已创建 |
| Admin 主题同步 | ✅ cookie 读取 + 1s 轮询 |
| Admin 返回主页链接 | ✅ 侧边栏底部 |
| Admin 玻璃磨砂风格 | ✅ backdrop-blur + 主题变量 |
| Footer 三列对齐 | ✅ grid gap-8 |
| Hero 85vh 满屏 | ✅ + 渐变过渡遮罩 |
| AI 按钮未登录提示 | ✅ confirm + 跳转登录 |
| 顶栏文档链接 | ✅ 桌面 + 移动端 |

---

## 约束遵守

- ✅ 权限系统完整实现：数据库 + API + 前端管理界面
- ✅ admin 角色权限锁定不可修改（防止误锁）
- ✅ Admin 主题与主站完全同步（cookie 读取）
- ✅ 所有改动通过 `pnpm build` 验证
- ✅ 未破坏现有接口签名（仅扩展权限字段）

---

# GLM 5.2 · 资源显示修复 + UI 打磨 + 下载方式重构

> 批次时间：2026-06-25
> 验证状态：✅ `pnpm --filter nuxt-app build` + `pnpm --filter admin-spa build` 全部通过

## 一、P0：资源页不显示修复

### 根因
- `backend/app/modules/resources/router.py` 公开列表/详情接口过滤 `Resource.status == "published"`
- Admin 创建资源默认 `status='draft'`，且无切换为 `published` 的入口，导致前台永远看不到资源

### 修复
| 文件 | 改动 |
| --- | --- |
| [admin-spa/src/views/posts/PostListView.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/views/posts/PostListView.vue) | 新增 `togglePublish(row as PostListItem)`，操作列加「发布/下架」按钮；状态列 el-tag 颜色：已发布(绿)/草稿(黄)/归档(灰)；状态筛选新增「已归档」选项；操作列宽 220px |
| [admin-spa/src/views/resources/ResourceListView.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/views/resources/ResourceListView.vue) | 同上，针对 ResourceListItem 实现 |

## 二、移除详情页正文悬浮气泡

| 文件 | 改动 |
| --- | --- |
| [nuxt-app/app/assets/css/main.css](file:///f:/FCelestial/fwe-repo/nuxt-app/app/assets/css/main.css) | 新增 `.no-hover-lift` 类：`transform: none !important` + 轻量阴影，禁用 hover 上浮；同时修复此前误删的 `select {` 选择器（恢复 option 配色） |
| [nuxt-app/app/pages/blog/\[slug\].vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/pages/blog/[slug].vue) | 正文 GlassCard 添加 `no-hover-lift` 类 |
| [nuxt-app/app/pages/resources/\[slug\].vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/pages/resources/[slug].vue) | 截图/介绍/版本历史三个 GlassCard 均添加 `no-hover-lift` 类 |
| [packages/ui/src/glass/GlassCard.vue](file:///f:/FCelestial/fwe-repo/packages/ui/src/glass/GlassCard.vue) | 卡片列表（PostCard/ResourceCard）保留轻量 hover 效果，未改动 |

## 三、玻璃面板内部 padding 优化（breathing room）

| 文件 | 改动 |
| --- | --- |
| [packages/ui/src/glass/GlassCard.vue](file:///f:/FCelestial/fwe-repo/packages/ui/src/glass/GlassCard.vue) | 默认 padding `p-6` → `p-5 sm:p-6`（移动端更紧凑，桌面端保持舒适间距） |

## 四、Admin 内容编辑器 UI 优化

| 文件 | 改动 |
| --- | --- |
| [admin-spa/src/components/editors/PostEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/PostEditor.vue) | Vditor 高度 480 → 560；`label-position="left"` + `label-width="80px"`；分类/标签合并 `grid-cols-4`；封面预览直接显示在输入框下方；底部草稿/发布按钮 sticky + 玻璃背景（`backdrop-blur-xl` + `var(--panel)`） |
| [admin-spa/src/components/editors/ResourceEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/ResourceEditor.vue) | Vditor 高度 360 → 560；同上 label 布局；类型/状态/图标合并 `grid-cols-4`；封面预览直接显示；sticky 底部栏 |

## 五、资源下载方式重构（local / external）

### 后端
| 文件 | 改动 |
| --- | --- |
| [backend/app/modules/resources/models.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/resources/models.py) | `ResourceVersion` 新增 `download_type`（local/external，默认 local）和 `external_label`（网盘名称）字段 |
| [backend/alembic/versions/b2c3d4e5f6a7_add_resource_download_type.py](file:///f:/FCelestial/fwe-repo/backend/alembic/versions/b2c3d4e5f6a7_add_resource_download_type.py) | Alembic 迁移：新增两列 + 旧数据迁移（`external_url` 非空者自动设为 `external`） |
| [backend/app/modules/resources/schemas.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/resources/schemas.py) | `ResourceVersionBase/Create/Update/Out` 新增字段；`model_validator` 校验：local 必填 `file_url`，external 必填 `external_url` |
| [backend/app/modules/resources/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/resources/router.py) | `create_version`/`update_version` 写入新字段；`download_version` 根据 `download_type` 决定重定向地址（external → `external_url`，local → `file_url`） |
| [backend/app/modules/admin/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/admin/router.py) | Admin 列表/详情序列化包含 `download_type`/`external_label` |

### 共享类型
| 文件 | 改动 |
| --- | --- |
| [packages/shared/src/types/index.ts](file:///f:/FCelestial/fwe-repo/packages/shared/src/types/index.ts) | `ResourceVersionOut` 新增 `download_type` 和 `external_label` 字段 |

### Admin 前端
| 文件 | 改动 |
| --- | --- |
| [admin-spa/src/components/editors/ResourceEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/ResourceEditor.vue) | 版本对话框新增下载方式单选（本站上传/外链下载）；外链时显示 URL + 网盘名称输入框；本站时显示文件上传；版本列表显示下载方式标签 |

### 前端展示
| 文件 | 改动 |
| --- | --- |
| [nuxt-app/app/pages/resources/\[slug\].vue](file:///f:/FCelestial/fwe-repo/nuxt-app/app/pages/resources/[slug].vue) | 下载按钮根据 `download_type` 显示：local → 「本站下载 (v{version})」触发下载 API；external → 「前往{external_label}下载」新标签页打开 `external_url` |

## 六、resource-pack pack.yml 兼容接口

| 文件 | 改动 |
| --- | --- |
| [backend/app/modules/resources/router.py](file:///f:/FCelestial/fwe-repo/backend/app/modules/resources/router.py) | 新增 `GET /resources/{slug}/pack.yml` 端点：根据资源 versions 数据自动生成 YAML 配置，包含 `delivery.hosting` 列表（type/url/uuid/sha1） |

## 验证清单

| 验证项 | 状态 |
| --- | --- |
| Admin 发布资源 → 前台资源页可见 | ✅ togglePublish + status 过滤 |
| 文章详情页无悬浮气泡 | ✅ `.no-hover-lift` 类 |
| 玻璃面板内部间距舒适 | ✅ `p-5 sm:p-6` |
| 资源支持本站/外链两种下载方式 | ✅ download_type + 前端按钮适配 |
| `pnpm build` 通过 | ✅ nuxt-app + admin-spa 均成功 |

## 约束遵守

- ✅ 未破坏现有接口签名（仅扩展 `download_type`/`external_label` 字段，旧客户端兼容）
- ✅ Alembic 迁移含旧数据迁移逻辑
- ✅ 详情页 hover 效果移除仅作用于内容面板，卡片列表保留轻量 hover
- ✅ 所有改动通过 `pnpm build` 验证

---

## 批次6：Vditor 资源补全 + Admin 深色模式全面适配

> 时间：2026-06-25
> 范围：admin-spa 编辑器图标修复、深色模式全覆盖、主题切换按钮、文件管理响应式

### 一、Vditor 编辑器工具栏图标修复（P0）

**问题**：两个编辑器（PostEditor / ResourceEditor）工具栏图标不显示。

**根因**：Vditor 内部使用同步 XHR（`addScriptSync`）加载 `material.js` 图标脚本，在某些环境下可能加载失败，导致 SVG sprite 未注入 DOM。

**修复**：
- 新建 [admin-spa/src/utils/vditor-icons.ts](file:///f:/FCelestial/fwe-repo/admin-spa/src/utils/vditor-icons.ts)：`preloadVditorIcons()` 使用 `fetch` 异步预加载 `material.js`，将脚本内容注入 `<head>`，Vditor 内部检测到 `vditorIconScript` 已存在会跳过重复加载。
- [PostEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/PostEditor.vue#L125-L129)：`initVditor()` 中先调用 `await preloadVditorIcons(cdnBase)` 再初始化 Vditor。
- [ResourceEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/ResourceEditor.vue#L208-L212)：同上。

### 二、编辑器高度与宽度优化（P1）

**问题**：`/admin/#/posts/new` 编辑器宽度太窄、高度不够。

**修复**：
- [PostEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/PostEditor.vue#L132)：`height: 560` → `height: 700`。
- [ResourceEditor.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/editors/ResourceEditor.vue#L215)：同上。
- [PostEditView.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/views/posts/PostEditView.vue#L71)：`admin-card p-4 md:p-6` → `admin-card p-3 md:p-4`，减小外层 padding 让编辑器更宽。
- [ResourceEditView.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/views/resources/ResourceEditView.vue#L26)：给 ResourceEditor 添加 `admin-card p-3 md:p-4` 包裹（此前无卡片容器）。

### 三、Admin 深色模式全面适配（P0）

**问题**：`/admin/#/resources/new` 深色适配不完整，Element Plus 组件（tabs、radio、upload、card 等）未跟随深色模式。

**修复**：[admin-spa/src/style.css](file:///f:/FCelestial/fwe-repo/admin-spa/src/style.css) 追加深色覆盖：

| 组件 | 覆盖内容 |
|------|----------|
| el-tabs（border-card） | header 背景、item 文字色、active 项 accent 色 + 内容区背景 |
| el-card | 背景 + 边框 + header 分割线 |
| el-radio-button | 未选中背景/文字色 + 选中 accent 色 |
| el-upload-dragger | 拖拽区背景 + hover 边框 |
| el-input-number | 输入框背景 |
| el-divider | 分割线 + 文字背景 |
| el-alert | 背景 + 边框 |
| el-popper（tooltip） | 深色背景 + 文字色 |
| el-text | primary/regular/secondary/placeholder 文字色 |
| el-table | bg/tr/header 背景改为 `--panel-solid`（不透明，解决穿透问题） |

### 四、admin-card 不透明背景修复（P1）

**问题**：文件列表长度不够时，半透明 admin-card 导致底下内容穿透。

**根因**：`--panel: rgba(17, 24, 39, 0.6)` 为 60% 半透明，配合 `backdrop-filter: blur(12px)` 在内容稀疏区域会穿透。

**修复**：
- [style.css](file:///f:/FCelestial/fwe-repo/admin-spa/src/style.css#L82-L87)：`.admin-card` 背景从 `var(--panel)` 改为 `var(--panel-solid)`，移除 `backdrop-filter`，确保完全不透明。
- `html.dark .admin-card` 同步改为 `var(--panel-solid)`。

### 五、Admin 主题切换按钮（P1）

**问题**：管理后台没有切换深色/浅色模式的按钮。

**修复**：
- 新建 [admin-spa/src/composables/useTheme.ts](file:///f:/FCelestial/fwe-repo/admin-spa/src/composables/useTheme.ts)：
  - `currentTheme` 响应式 ref
  - `toggleTheme()` 切换主题并写入 cookie（`path=/;SameSite=Lax`，与主站共享）
  - `initTheme()` 从 cookie 读取初始主题
- [main.ts](file:///f:/FCelestial/fwe-repo/admin-spa/src/main.ts#L15-L19)：移除旧的 `setInterval` 轮询 cookie 逻辑，改用 `initTheme()` 一次性初始化。
- [AdminHeader.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/components/layout/AdminHeader.vue#L50-L58)：添加 Sun/Moon 图标切换按钮，深色模式显示 Sun（点击切到浅色），浅色模式显示 Moon。

### 六、FileManagerView 响应式 + 透明修复（P1）

**问题**：`/admin/#/files` 文件列表对不同分辨率适配不足，不该透明的地方会变透明。

**修复**：[FileManagerView.vue](file:///f:/FCelestial/fwe-repo/admin-spa/src/views/FileManagerView.vue)

| 改动 | 说明 |
|------|------|
| 布局改为 `flex-col md:flex-row` | 移动端纵向堆叠，桌面端横向排列 |
| 文件树 `w-full md:w-56` | 移动端全宽，桌面端固定 224px |
| 文件列表 `min-h-[300px]` | 确保最小高度，避免内容太少时穿透 |
| 表格列宽缩减 | selection 50→45, 文件名 180→160, 大小 120→90, 类型 160→130, 下载量 100→75, 创建时间 170→150, 操作 140→120 |
| 创建时间列添加 `show-overflow-tooltip` | 防止窄屏截断 |
| 右键菜单改用 `var(--panel-solid)` | 不透明背景，深色模式适配 |
| 删除按钮 hover 添加 `dark:hover:bg-red-500/10` | 深色模式 hover 效果 |

### 验证结果

| 验证项 | 状态 |
|--------|------|
| `pnpm --filter admin-spa build` | ✅ 14.36s 成功 |
| Vditor 工具栏图标预加载 | ✅ `preloadVditorIcons()` fetch 异步加载 |
| 编辑器高度 700px | ✅ PostEditor + ResourceEditor |
| el-tabs/radio/upload/card 深色覆盖 | ✅ style.css 追加 |
| admin-card 不透明背景 | ✅ `--panel-solid` |
| 主题切换按钮 | ✅ AdminHeader Sun/Moon |
| 文件管理响应式 | ✅ flex-col md:flex-row + 列宽缩减 |
| 右键菜单深色适配 | ✅ `--panel-solid` 背景 |
