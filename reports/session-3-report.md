# Session 3 报告：Nuxt 3 公网站点前端

## 项目信息

- **项目名称**：FwindEmiko-Web
- **前端框架**：Nuxt 3 (v4.4.8) + Vue 3 + TypeScript
- **UI/样式**：TailwindCSS 3 + Element Plus + 自定义 Glass 组件
- **状态管理**：Pinia
- **后端 API**：http://localhost:8000/api
- **前端 dev server**：http://localhost:3001（3000 被占用）

## 完成内容

### Step 1：共享包

- `packages/shared/src/types/index.ts`：定义了 User、Post、Resource、Category、Tag、Chat 等全部 TypeScript 接口，与后端模型对应。
- `packages/shared/src/api/index.ts`：封装 Axios，包含 JWT 拦截器、统一错误处理、ApiError 类，以及 blog/resource/download/chat/auth 各模块 API 函数。兼容后端 `{code, data, message}` 包装格式与原始返回格式。
- `packages/ui/src/glass/`：提供 GlassCard、GlassButton、GlassModal 三个玻璃磨砂风格组件。

### Step 2：Nuxt3 配置

- `nuxt-app/nuxt.config.ts`：启用 SSR、配置 runtimeConfig（apiBase/uploadBase）、head/titleTemplate、TailwindCSS、Pinia、Element Plus、@nuxtjs/sitemap、@nuxtjs/robots。
- `nuxt-app/tailwind.config.ts`：扩展颜色变量、backdropBlur、圆角、阴影等。
- `nuxt-app/app/assets/css/main.css`：定义深色/浅色 CSS 变量与玻璃工具类。

### Step 3：布局 + 导航

- `layouts/default.vue`：AppHeader + slot + AppFooter + Live2DWidget。
- `components/AppHeader.vue`：Logo、导航链接、搜索框、登录/头像、主题切换、移动端汉堡菜单。
- 导航响应式：桌面端横向导航，移动端折叠为汉堡菜单。

### Step 4：页面实现

- `/`：SSG，精选文章 + 热门资源。
- `/blog`：ISR 1h，列表 + 分类/标签过滤 + 分页。
- `/blog/[slug]`：SSG，详情 + SEO meta + 上一篇/下一篇。
- `/resources`：ISR 24h，列表 + 类型/MC版本过滤。
- `/resources/[slug]`：SSG，详情 + 截图画廊 + 版本列表 + 下载按钮。
- `/download`：SSR，文件浏览器（文件夹树 + 文件列表 + 面包屑），未登录仅公开文件夹。
- `/login`、`/register`、`/profile`：CSR。

### Step 5：AI 对话面板

- `components/ChatPanel.vue`：可折叠面板、SSE 流式渲染占位、消息历史、配额显示。
- 未登录时面板隐藏；dev 模式下自动使用 mock 回复。

### Step 6：响应式适配

- 所有页面使用 `sm/md/lg` 断点：导航折叠、资源卡片 3/2/1 列、文件管理器左右分栏/单栏。

### Step 7：SEO

- `@nuxtjs/sitemap` 自动生成 sitemap。
- 博客/资源详情页使用 `useHead` 注入动态 title、description、og 标签。
- `robots.txt` 由 `@nuxtjs/robots` 管理（开发环境默认 noindex，生产环境按规则开放）。

## 自测结果

| 检查项 | 状态 | 说明 |
|--------|------|------|
| `pnpm dev` 可访问 http://localhost:3001 | 通过 | 因 3000 端口被占用，实际运行在 3001 |
| 首页加载 | 通过 | 精选文章、热门资源正常渲染 |
| 博客列表加载 | 通过 | 分类/标签过滤、分页正常 |
| 博客详情渲染 | 通过 | SSR 渲染，上一篇/下一篇正常 |
| 资源列表 | 通过 | 类型/MC版本过滤正常 |
| 资源详情 + 下载按钮 | 通过 | 截图画廊、版本列表、网盘下载按钮可用 |
| 下载站权限区分 | 通过 | 未登录仅 4 个公开文件夹；登录后显示 8 个（含 VIP） |
| 移动端（F12 模拟） | 通过 | 响应式类已覆盖，汉堡菜单/单列布局生效 |
| 深色/浅色切换 | 通过 | CSS 变量切换正常 |
| SEO meta 标签 | 通过 | 详情页源码中可见 title/og:description/og:type/article:published_time |
| AI 对话面板 mock | 通过 | dev 模式自动走 mock 回复逻辑 |
| sitemap | 通过 | `/sitemap.xml` 可访问，包含静态页面 |

## 自测中修复的问题

### 1. GlassCard 组件 SSR 解析失败

**现象**：Nuxt 终端出现 `Failed to resolve component: GlassCard` 和 `Component <Anonymous> is missing template or render function`，导致详情页 SSR 回退为 CSR。

**原因**：`packages/ui` 的玻璃组件不会被 Nuxt 自动导入，部分页面未显式 import。

**修复**：在 `nuxt.config.ts` 中配置 `components`，将 `packages/ui/src/glass` 加入自动扫描路径：

```ts
components: [
  { path: '~/components', pathPrefix: false },
  { path: '../../packages/ui/src/glass', pathPrefix: false },
],
```

### 2. 博客/资源详情页 SEO meta 未生效

**现象**：详情页 `<title>` 始终为 `狐风轩汐の小屋 - 狐风轩汐の小屋`，og 标签未注入。

**原因**：`useSeoMeta(() => ({...}))` 函数形式在 SSR 时未正确读取异步数据。

**修复**：改为 `useHead(() => ({ title, meta: [...] }))`，明确指定 meta 数组：

- `app/pages/blog/[slug].vue`
- `app/pages/resources/[slug].vue`

### 3. 博客列表空值渲染报错

**现象**：博客列表页在分类/标签为空时出现渲染异常。

**修复**：`v-for` 循环增加空数组保护（`categories || []`、`tags || []`）。

### 4. API 响应格式兼容

**现象**：部分接口返回原始数据而非 `{code, data, message}` 包装。

**修复**：`packages/shared/src/api/index.ts` 的 `unwrap` 函数同时处理两种返回格式。

## 已知问题

1. **sitemap 动态 URL**：开发模式下 `/sitemap.xml` 仅包含 `/`、`/blog`、`/resources`、`/download` 等静态路由。动态 URL（博客详情、资源详情）在生产构建（`nuxt build` 或 `nuxt generate`）时会通过 `sitemap.urls` 函数生成；开发模式下该函数未被调用，属于 @nuxtjs/sitemap 的正常行为。

2. **robots.txt 开发模式**：`@nuxtjs/robots` 在 development 环境下默认输出 `Disallow: /`，生产环境（`NODE_ENV=production`）会按 `nuxt.config.ts` 规则开放索引。

3. **字符编码显示**：PowerShell 终端输出中文偶尔出现转义字符，但浏览器页面与 API 实际返回的中文内容正常。

## 运行方式

```bash
# 根目录安装依赖
pnpm install

# 启动后端（已在 http://localhost:8000）
# cd backend && ...

# 启动前端 dev server
cd nuxt-app
pnpm dev
```

访问：http://localhost:3001

## 测试账号

- admin：`admin_user` / `Password123`
- author：`author_user` / `Password123`
- member：`member_user` / `Password123`

## 下一步建议

- 生产构建验证 `nuxt build` / `nuxt generate`。
- 配置真实 LLM API Key 后移除 ChatPanel 的 mock 分支。
- 根据生产域名调整 `NUXT_PUBLIC_SITE_URL` 与 robots/sitemap 规则。
