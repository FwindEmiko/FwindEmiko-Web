<script setup lang="ts">
import {
  LayoutDashboard,
  FileText,
  Box,
  FolderOpen,
  Users,
  Shield,
  ChevronLeft,
  ChevronRight,
  Home,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const auth = useAuthStore()
const app = useAppStore()

const menu = [
  { name: 'Dashboard', label: '仪表盘', icon: LayoutDashboard, path: '/' },
  { name: 'PostList', label: '文章', icon: FileText, path: '/posts' },
  { name: 'ResourceList', label: '资源', icon: Box, path: '/resources' },
  { name: 'Files', label: '文件', icon: FolderOpen, path: '/files', admin: true },
  { name: 'Users', label: '用户', icon: Users, path: '/users', admin: true },
  { name: 'Permissions', label: '权限', icon: Shield, path: '/permissions', admin: true },
]

const visibleMenu = menu.filter((item) => !item.admin || auth.isAdmin)

// 返回主站
const homeUrl = 'https://f.windemiko.top'
</script>

<template>
  <aside
    class="flex flex-col border-r border-[var(--border)] backdrop-blur-xl transition-all duration-300"
    :class="app.sidebarCollapsed ? 'w-16' : 'w-56'"
    style="background: var(--panel);"
  >
    <div class="h-14 flex items-center justify-center border-b border-[var(--border)]">
      <span v-if="!app.sidebarCollapsed" class="font-semibold text-lg text-[var(--text-primary)]">FwindAdmin</span>
      <span v-else class="font-bold text-xl text-[var(--accent)]">F</span>
    </div>

    <nav class="flex-1 py-4 space-y-1">
      <router-link
        v-for="item in visibleMenu"
        :key="item.name"
        :to="item.path"
        class="flex items-center gap-3 px-4 py-3 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--accent-light)] hover:text-[var(--accent)] transition-colors"
        :class="{ 'justify-center': app.sidebarCollapsed }"
        active-class="bg-[var(--accent-light)] text-[var(--accent)] border-r-2 border-[var(--accent)]"
      >
        <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
        <span v-if="!app.sidebarCollapsed">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- 返回主站链接 -->
    <div class="px-3 py-2 border-t border-[var(--border)]">
      <a
        :href="homeUrl"
        class="flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--accent)] hover:bg-[var(--accent-light)] rounded-lg transition-colors"
        :class="{ 'justify-center': app.sidebarCollapsed }"
        title="返回主站"
      >
        <Home class="w-5 h-5 flex-shrink-0" />
        <span v-if="!app.sidebarCollapsed">返回主页</span>
      </a>
    </div>

    <div class="p-3 border-t border-[var(--border)]">
      <button
        class="w-full flex items-center justify-center gap-2 p-2 rounded-lg hover:bg-[var(--accent-light)] text-[var(--text-secondary)]"
        @click="app.toggleSidebar"
      >
        <ChevronLeft v-if="!app.sidebarCollapsed" class="w-4 h-4" />
        <ChevronRight v-else class="w-4 h-4" />
      </button>
    </div>
  </aside>
</template>
