# 07 — Admin SPA

> **依赖**: `06-frontend-nuxt.md` 中的 `packages/shared` 和 `packages/ui`  
> **目标**: 独立单页应用，CSR only，提供全部后台管理功能  
> **核心用户**: 星玖（维护者）、汐汐酱  
> **验证**: 能创建/编辑文章和资源、上传文件、管理用户

---

## 1. 架构决策

- **独立构建**: `admin-spa/` 使用 Vite + Vue3，不依赖 Nuxt3
- **共享包**: 引用 `packages/shared`（API 客户端）和 `packages/ui`（玻璃磨砂组件）
- **部署**: `vite build` → 静态文件 → Nginx `location /admin` serve
- **路由**: Hash 模式（`createWebHashHistory`），与 Nuxt3 路由不冲突

---

## 2. 目录结构

```
admin-spa/
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/index.ts
│   ├── stores/
│   │   ├── auth.ts          # 登录状态
│   │   └── app.ts           # 全局 UI 状态（侧边栏折叠等）
│   ├── api/
│   │   └── client.ts        # Axios 实例（JWT 拦截器）
│   ├── composables/
│   │   ├── useAuth.ts
│   │   └── useUpload.ts     # 上传进度 Hook
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AdminLayout.vue      # 侧边栏 + 主内容区
│   │   │   ├── AdminSidebar.vue     # 导航菜单
│   │   │   └── AdminHeader.vue      # 顶部面包屑 + 用户信息
│   │   ├── editors/
│   │   │   ├── PostEditor.vue       # Vditor 封装
│   │   │   └── ResourceEditor.vue   # 资源表单 + 版本管理
│   │   └── file-manager/
│   │       ├── FileTree.vue         # 文件夹树 (el-tree)
│   │       ├── FileTable.vue        # 文件列表 (el-table)
│   │       ├── FileContextMenu.vue  # 右键菜单
│   │       └── UploadZone.vue       # 拖拽上传区域
│   │
│   └── views/
│       ├── LoginView.vue
│       ├── DashboardView.vue        # 统计面板
│       ├── posts/
│       │   ├── PostListView.vue     # 文章列表 + 筛选
│       │   └── PostEditView.vue     # 新建/编辑文章
│       ├── resources/
│       │   ├── ResourceListView.vue
│       │   └── ResourceEditView.vue
│       ├── FileManagerView.vue      # 文件管理器
│       └── UserManagerView.vue      # 用户管理（admin only）
│
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 3. 路由表

```ts
// router/index.ts
const routes = [
  { path: '/login',      component: LoginView,      meta: { guest: true } },
  { path: '/',           component: DashboardView,   meta: { auth: true } },
  { path: '/posts',      component: PostListView,    meta: { auth: true } },
  { path: '/posts/new',  component: PostEditView,    meta: { auth: true } },
  { path: '/posts/:id',  component: PostEditView,    meta: { auth: true } },
  { path: '/resources',     component: ResourceListView,  meta: { auth: true } },
  { path: '/resources/new', component: ResourceEditView,  meta: { auth: true } },
  { path: '/resources/:id', component: ResourceEditView,  meta: { auth: true } },
  { path: '/files',      component: FileManagerView, meta: { auth: true, role: 'admin' } },
  { path: '/users',      component: UserManagerView, meta: { auth: true, role: 'admin' } },
]
```

路由守卫：
```ts
router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.auth && !auth.isLoggedIn) return next('/login')
  if (to.meta.role && auth.user?.role !== 'admin') return next('/')
  if (to.meta.guest && auth.isLoggedIn) return next('/')
  next()
})
```

---

## 4. AdminLayout 布局

```
┌──────────────────────────────────────────────────┐
│  AdminHeader: Logo + 面包屑 + 用户头像(下拉菜单)   │
├──────────┬───────────────────────────────────────┤
│ Sidebar  │  <router-view />                      │
│          │                                       │
│ 📊 仪表盘 │                                       │
│ ✏️ 文章   │                                       │
│ 🎮 资源   │                                       │
│ 📁 文件   │  (admin only, 侧边栏条件渲染)         │
│ 👤 用户   │  (admin only)                         │
│          │                                       │
└──────────┴───────────────────────────────────────┘
```

- 侧边栏折叠：桌面端默认展开，移动端自动折叠
- Sidebar 菜单项根据用户 `role` 条件渲染

---

## 5. DashboardView 统计面板

```
┌─────────────────────────────────────────────────┐
│  [统计卡片 × 4：文章数 | 资源数 | 文件数 | 下载量]  │
├─────────────────────────────────────────────────┤
│  最近文章 (5 条)          │  最近上传 (5 条)       │
│  快速操作: [+新文章]      │  [+新资源] [+上传文件] │
└─────────────────────────────────────────────────┘
```

统计 API：`GET /api/admin/stats` → `{posts, resources, files, downloads, recent_posts: [...], recent_uploads: [...]}`

---

## 6. PostEditor — 核心组件

封装 Vditor：

```vue
<!-- components/editors/PostEditor.vue -->
<template>
  <div class="editor-container">
    <el-form :model="form">
      <el-input v-model="form.title" placeholder="文章标题" size="large" />
      <div class="flex gap-4 mt-4">
        <el-select v-model="form.category_id" placeholder="分类" />
        <el-select v-model="form.tag_ids" multiple placeholder="标签" />
      </div>
      <!-- Vditor 挂载点 -->
      <div id="vditor" class="mt-4" />
      <div class="flex gap-2 mt-4">
        <el-button @click="save('draft')">存草稿</el-button>
        <el-button type="primary" @click="save('published')">发布</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
// Vditor 初始化：mode: 'wysiwyg'（所见即所得）
// 工具栏精简：标题、加粗、链接、图片、代码、表格、预览切换
// Ctrl+S → 保存草稿，Ctrl+Enter → 发布
// 自动保存：每 30 秒写 localStorage，编辑器加载时恢复

const vditor = ref<Vditor>()
onMounted(() => {
  vditor.value = new Vditor('vditor', {
    mode: 'wysiwyg',
    height: 500,
    placeholder: '开始写作...',
    cache: { enable: true, id: `post-${route.params.id || 'new'}` },
    toolbar: [
      'headings', 'bold', 'italic', 'strike', '|',
      'link', 'code', 'inline-code', '|',
      'list', 'ordered-list', 'check', '|',
      'upload', 'table', '|',
      'undo', 'redo', '|',
      'preview', 'edit-mode',
    ],
    upload: {
      url: '/api/files/upload',          // 图片上传端点
      headers: { Authorization: `Bearer ${token}` },
    },
  })
})

async function save(status: string) {
  const content = vditor.value?.getValue()  // Markdown
  // POST /api/posts 或 PUT /api/posts/{id}
}
</script>
```

---

## 7. ResourceEditor — 资源编辑器

三 Tab 结构：

```
┌─────────────────────────────────────────────────┐
│  [基本信息]  [截图管理]  [版本管理]               │
├─────────────────────────────────────────────────┤
│  Tab 1: 基本信息                                  │
│  ┌──────────────────┐                           │
│  │ 标题             │                           │
│  │ 类型: ☐插件 ☐模组 ☐数据包                     │
│  │ MC版本: [多选标签]                             │
│  │ 加载器: [多选标签]                             │
│  │ 图标上传 / 封面图上传                          │
│  │ 描述 (Vditor Markdown)                        │
│  └──────────────────┘                           │
│                                                 │
│  Tab 2: 截图管理                                  │
│  [拖拽上传区 → 自动生成缩略图]                     │
│  [已上传截图列表：拖拽排序 × 删除]                  │
│                                                 │
│  Tab 3: 版本管理                                  │
│  [+ 添加版本]                                     │
│  ┌─────────────────────────────────────────┐    │
│  │ v1.2.0  更新日志(MD)  文件/外链  [删除]  │    │
│  │ v1.1.0  更新日志(MD)  文件/外链  [删除]  │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

截图排序：拖拽 → `PUT /api/resources/{id}/screenshots/reorder`

---

## 8. FileManagerView — 文件管理器

基于 `n1crack/vuefinder` 交互理念：

```
┌─────────────┬────────────────────────────────────┐
│ el-tree     │ 面包屑: / 公开资源 / MC插件          │
│ (文件夹树)   │ ┌────────────────────────────────┐ │
│             │ │ el-table: 文件名 | 大小 | 日期   │ │
│ 📁 公开资源  │ │ SkyIsland-v1.2.jar  2.3MB  ... │ │
│  ├📁 MC插件 │ │ BentoBox-v3.16.jar   5.1MB  ... │ │
│  ├📁 模组   │ │ ...                            │ │
│  └📁 工具   │ └────────────────────────────────┘ │
│ 🔒 VIP资源  │ [拖拽文件到此处上传]                 │
│ 🔒 内部资料  │                                     │
│             │ 右键菜单: 下载 | 重命名 | 删除       │
│ [+新文件夹]  │                                     │
└─────────────┴────────────────────────────────────┘
```

- `el-tree` 文件夹树：点击节点 → 加载该文件夹的文件列表
- `el-table`：排序、右键菜单
- `UploadZone`：el-upload 的 drag 模式
- `BreadcrumbBar`：每级可点击跳转

---

## 9. 编辑器优化（单人易用性）

| 功能 | 实现 |
|------|------|
| 快捷键 | `Ctrl+S` 保存，`Ctrl+Enter` 发布，`Esc` 关闭弹窗 |
| 自动保存 | 文章编辑器 30s 自动存 localStorage |
| 记忆选项 | 上次选择的分类/标签/版本默认选中 |
| 模板功能 | 资源描述可保存为 Markdown 模板 → 新建时下拉选择加载 |
| 快速发布 | 文章填写标题+内容 → 一键 "发布"，省略中间步骤 |
| 批量操作 | 资源列表多选 → 批量改标签/分类 |

---

## 10. 验证方式

```bash
cd admin-spa
pnpm dev
# 访问 http://localhost:5173

# 验证清单:
# [ ] 登录页 → JWT 获取 → 保存到 store
# [ ] 仪表盘统计数据显示
# [ ] 文章新建 → Vditor 加载 → 存草稿 → 发布
# [ ] 资源新建 → 三 Tab 正常切换 → 截图拖拽上传
# [ ] 文件管理 → 文件夹树展开 → 文件上传 → 拖拽 → 右键菜单
# [ ] 路由守卫 → 未登录跳转 → admin only 页面禁止非 admin 访问
# [ ] 移动端 → 侧边栏自动折叠 → 表格横向滚动
```

---

> **下一份**: `08-live2d-integration.md` — Live2D 组件
