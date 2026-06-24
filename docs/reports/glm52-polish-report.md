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
