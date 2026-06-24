<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, LogOut, User } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const app = useAppStore()

const breadcrumbs = computed(() => {
  const items = [{ title: '首页', path: '/' }]
  if (route.meta.title && route.path !== '/') {
    items.push({ title: route.meta.title as string, path: route.path })
  }
  return items
})

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <header class="h-14 bg-white border-b border-[var(--border)] flex items-center justify-between px-4 sticky top-0 z-20">
    <div class="flex items-center gap-3">
      <button
        v-if="app.isMobile"
        class="p-2 rounded-lg hover:bg-gray-100 text-[var(--text-secondary)]"
        @click="app.toggleSidebar"
      >
        <Menu class="w-5 h-5" />
      </button>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item v-for="(item, idx) in breadcrumbs" :key="item.path">
          <router-link v-if="idx < breadcrumbs.length - 1" :to="item.path" class="text-[var(--text-secondary)] hover:text-[var(--accent)]">
            {{ item.title }}
          </router-link>
          <span v-else class="text-[var(--text)] font-medium">{{ item.title }}</span>
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="flex items-center gap-3">
      <span class="text-xs text-[var(--text-secondary)] hidden sm:inline">
        {{ auth.user?.display_name || auth.user?.username }}
        <el-tag size="small" class="ml-2">{{ auth.user?.role }}</el-tag>
      </span>
      <el-dropdown trigger="click">
        <div class="w-8 h-8 rounded-full bg-[var(--accent-light)] flex items-center justify-center cursor-pointer text-[var(--accent)]">
          <User class="w-5 h-5" />
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              {{ auth.user?.username }} ({{ auth.user?.role }})
            </el-dropdown-item>
            <el-dropdown-item divided @click="logout">
              <span class="flex items-center gap-2">
                <LogOut class="w-4 h-4" /> 退出登录
              </span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>
