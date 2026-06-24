# 06 — Nuxt3 公网站点

> **依赖**: 所有后端模块 API 就绪  
> **目标**: SSR/SSG 渲染的博客 + 资源展示 + 下载站 + AI 对话面板 + Live2D  
> **验证**: 浏览器能访问所有页面，SEO meta 正确，移动端正常显示

---

## 1. 页面清单 & 渲染策略

| 路由 | 组件 | 渲染 | 内容 |
|------|------|------|------|
| `/` | `pages/index.vue` | SSG | 首页：精选文章 + 热门资源 + 简介 |
| `/blog` | `pages/blog/index.vue` | ISR 1h | 文章列表 + 分类/标签过滤 |
| `/blog/[slug]` | `pages/blog/[slug].vue` | SSG | 文章详情 |
| `/resources` | `pages/resources/index.vue` | ISR 24h | 资源列表 + 类型/版本过滤 |
| `/resources/[slug]` | `pages/resources/[slug].vue` | SSG | 资源详情 + 版本 + 截图 |
| `/download` | `pages/download/index.vue` | SSR | 文件浏览器 + 权限隔离 |
| `/login` | `pages/login.vue` | CSR | 登录表单 |
| `/register` | `pages/register.vue` | CSR | 注册表单 |
| `/profile` | `pages/profile.vue` | CSR | 个人中心（需登录） |

---

## 2. 布局组件

```
layouts/default.vue
├── AppHeader.vue          # 顶部导航（Glassmorphism 底栏）
│   ├── Logo + 站点名
│   ├── Nav: 首页 | 博客 | 资源 | 下载
│   ├── 搜索框（可折叠）
│   ├── 登录/头像按钮
│   └── 主题切换（深色/浅色）
├── <slot />               # 页面内容
├── AppFooter.vue
│   ├── 备案号
│   ├── 主题信息
│   └── 社交媒体链接
└── Live2DWidget.vue       # 右下角固定
```

### 移动端适配

- 导航切换：桌面端（≥ 768px）横向菜单，移动端（< 768px）汉堡按钮 + 抽屉面板
- 内容区域：桌面端 `max-w-6xl mx-auto`，移动端 `px-4`
- 资源卡片：3 列 → 2 列 → 1 列（`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`）
- 文件管理器：桌面端左右分栏，移动端单栏 + 返回按钮

---

## 3. Glassmorphism 组件 (`packages/ui/src/glass/`)

这些组件供 Nuxt3 和 Admin SPA 共用。

```vue
<!-- GlassCard.vue -->
<template>
  <div class="rounded-glass bg-glass backdrop-blur-glass 
              border border-glass-border shadow-glass 
              p-6 transition-all duration-300 hover:bg-opacity-[0.06]">
    <slot />
  </div>
</template>

<!-- GlassButton.vue -->
<!-- GlassModal.vue -->
```

TailwindCSS 扩展：
```ts
// nuxt.config.ts / tailwind.config.ts
theme: {
  extend: {
    colors: {
      glass: 'rgba(255, 255, 255, 0.04)',
      'glass-hover': 'rgba(255, 255, 255, 0.08)',
      'glass-border': 'rgba(255, 255, 255, 0.06)',
    },
    backdropBlur: { glass: '14px' },
    borderRadius: { glass: '14px' },
    boxShadow: { 
      glass: '0 8px 32px rgba(0, 0, 0, 0.12)',
      card: '0 4px 16px rgba(0, 0, 0, 0.08)',
    },
  },
}
```

---

## 4. 关键页面设计

### 4.1 首页 (`pages/index.vue`)

```
┌─────────────────────────────────────────────┐
│  Hero Banner (可切换的 ACG 插画 + 站点简介)   │
│  玻璃磨砂卡片: "狐风轩汐の小屋"               │
│  副标题: "代码 | 游戏 | 创作"                │
├─────────────────────────────────────────────┤
│  精选文章 (3-4 篇, PostCard 网格)            │
│  热门资源 (3-4 个, ResourceCard 网格)        │
└─────────────────────────────────────────────┘
```

### 4.2 文章列表 (`pages/blog/index.vue`)

```
┌──────────────────────────────────────────────┐
│  搜索框 + 分类下拉 + 标签云                   │
│  ┌──────────┬──────────┬──────────┐         │
│  │ PostCard │ PostCard │ PostCard │         │
│  │ [封面]   │ [封面]   │ [封面]   │         │
│  │ 标题     │ 标题     │ 标题     │         │
│  │ 日期 · 分类 · 阅读量 │         │         │
│  └──────────┴──────────┴──────────┘         │
│  [分页]                                     │
└──────────────────────────────────────────────┘
```

### 4.3 资源详情 (`pages/resources/[slug].vue`)

参考设计：Modrinth 项目页的简洁风格。

```
┌──────────────────────────────────────────────┐
│  [封面横幅]                                   │
│  ┌────┐  标题    版本标签  MC版本标签         │
│  │图标│  类型徽标  加载器标签                  │
│  └────┘                                      │
├──────────────────────────────────────────────┤
│  [截图 Gallery - 横向滚动，点击放大]          │
├──────────────────────────────────────────────┤
│  描述 (Markdown)                              │
├──────────────────────────────────────────────┤
│  版本历史                                     │
│  ┌────────────────────────────────────┐      │
│  │ v1.2.0 (最新)          5 MB       │      │
│  │ 更新日志...             [下载▼]    │      │
│  │            → 本地下载 / 网盘跳转   │      │
│  ├────────────────────────────────────┤      │
│  │ v1.1.0                 3 MB       │      │
│  │ ...                     [下载▼]    │      │
│  └────────────────────────────────────┘      │
└──────────────────────────────────────────────┘
```

下载按钮逻辑：
- 如果 `file_url` 非空 → "本地下载" 
- 如果 `external_url` 非空 → "网盘下载"（新标签页）
- 两者都有 → 下拉菜单二选一

### 4.4 下载站 (`pages/download/index.vue`)

- 访客（未登录）：只显示公开文件夹
- 登录用户：根据角色显示更多
- Folder.description 渲染为 Markdown（文件夹 README）
- 文件图标根据扩展名自动匹配：`.jar` → Java 图标，`.zip` → 压缩包图标，图片 → 缩略图

---

## 5. SEO 配置

```vue
<!-- pages/blog/[slug].vue -->
<script setup lang="ts">
const route = useRoute()
const { data: post } = await useAsyncData(
  `post-${route.params.slug}`,
  () => $fetch(`/api/posts/${route.params.slug}`)
)

useSeoMeta({
  title: post.value.title,
  ogTitle: post.value.title,
  description: post.value.summary,
  ogDescription: post.value.summary,
  ogImage: post.value.cover_url,
  ogType: 'article',
  articlePublishedTime: post.value.published_at,
})
</script>
```

- `nuxt.config.ts` 中配置全局 `head` 默认值
- 生成 `sitemap.xml`（使用 `@nuxtjs/sitemap`）
- `robots.txt` 允许抓取公网页面，禁止 `/admin`、`/api`

---

## 6. AI 对话面板

右下角可折叠面板，点击 Live2D 角色或独立按钮打开：

```
┌──────────────────────┐
│  AI 对话       [_]   │
├──────────────────────┤
│  历史消息...          │
│                      │
│  用户: 你好          │
│  AI: 你好！有什么... │
├──────────────────────┤
│  [输入框]      [发送] │
└──────────────────────┘
```

- 调用 `POST /api/chat/sessions/{id}/messages` SSE
- 流式渲染：逐字显示 AI 回复
- 未登录时对话面板隐藏，Live2D 只做基础交互（点击触发动作 + 气泡文本）

---

## 7. 主题系统

- 默认深色模式
- 用户可在 Header 切换浅色
- 通过 `useTheme` composable + `localStorage` 持久化
- CSS 变量在 `:root` 和 `:root.light` 中双向定义

```ts
// composables/useTheme.ts
export function useTheme() {
  const theme = useCookie('theme', { default: () => 'dark' })
  const isDark = computed(() => theme.value === 'dark')
  function toggle() { theme.value = isDark.value ? 'light' : 'dark' }
  return { theme, isDark, toggle }
}
```

---

## 8. 验证方式

```bash
cd nuxt-app
pnpm dev
# 访问 http://localhost:3000

# 验证清单:
# [ ] 首页正常渲染（SSG）
# [ ] /blog 列表可加载
# [ ] /blog/{slug} 详情正常，meta 标签正确
# [ ] /resources 列表可加载
# [ ] /resources/{slug} 详情正常，下载按钮可用
# [ ] /download 文件树显示，权限隔离正确
# [ ] 移动端汉堡菜单可用
# [ ] 深色/浅色切换正常
# [ ] Live2D 组件在右下角显示
# [ ] AI 对话面板可打开（需登录）
```

---

## 9. 灵活性留白

- 首页 Hero Banner 插画：先放一张静态图占位，后续可换成汐汐酱的插画或 MC 渲染图。
- PostCard / ResourceCard 组件的设计：不必完全照搬上述 ASCII 布局，参考 Modrinth / Dev.to 的卡片设计自由发挥即可。
- 搜索：可以先用客户端过滤（已获取的数据），后续再切到服务端搜索。
- 图片优化：`@nuxt/image` 自动优化、懒加载。封面图建议同时提供 webp 格式。

---

> **下一份**: `07-frontend-admin.md` — Admin SPA
