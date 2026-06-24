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
