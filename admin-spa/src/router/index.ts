import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { guest: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { auth: true, title: '仪表盘' },
  },
  {
    path: '/posts',
    name: 'PostList',
    component: () => import('@/views/posts/PostListView.vue'),
    meta: { auth: true, title: '文章管理' },
  },
  {
    path: '/posts/new',
    name: 'PostNew',
    component: () => import('@/views/posts/PostEditView.vue'),
    meta: { auth: true, title: '新建文章' },
  },
  {
    path: '/posts/:id',
    name: 'PostEdit',
    component: () => import('@/views/posts/PostEditView.vue'),
    meta: { auth: true, title: '编辑文章' },
  },
  {
    path: '/resources',
    name: 'ResourceList',
    component: () => import('@/views/resources/ResourceListView.vue'),
    meta: { auth: true, title: '资源管理' },
  },
  {
    path: '/resources/new',
    name: 'ResourceNew',
    component: () => import('@/views/resources/ResourceEditView.vue'),
    meta: { auth: true, title: '新建资源' },
  },
  {
    path: '/resources/:id',
    name: 'ResourceEdit',
    component: () => import('@/views/resources/ResourceEditView.vue'),
    meta: { auth: true, title: '编辑资源' },
  },
  {
    path: '/files',
    name: 'Files',
    component: () => import('@/views/FileManagerView.vue'),
    meta: { auth: true, role: 'admin', title: '文件管理' },
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/UserManagerView.vue'),
    meta: { auth: true, role: 'admin', title: '用户管理' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach(async (to, _from, next) => {
  const auth = useAuthStore()
  if (!auth.isLoggedIn) {
    await auth.restore()
  }

  if (to.meta.auth && !auth.isLoggedIn) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (to.meta.role && auth.user?.role !== to.meta.role) {
    return next({ path: '/' })
  }

  if (to.meta.guest && auth.isLoggedIn) {
    return next({ path: '/' })
  }

  next()
})

export default router
