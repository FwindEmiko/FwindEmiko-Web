<template>
  <header
    class="fixed top-0 left-0 right-0 z-40 glass-panel border-b-0 transition-all duration-300"
    :class="scrolled ? 'shadow-glass bg-glass/90' : 'bg-glass/60'"
  >
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-14">
        <!-- Logo + site name (left) -->
        <NuxtLink to="/" class="flex items-center gap-2 group flex-shrink-0">
          <div class="w-8 h-8 rounded-lg bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)]">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
          </div>
          <span class="font-bold text-lg text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors">狐风轩汐</span>
        </NuxtLink>

        <!-- Right section: nav + search + actions -->
        <div class="flex items-center gap-2">
          <!-- Desktop Nav links -->
          <nav class="hidden md:flex items-center gap-1">
            <NuxtLink
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
              :class="route.path === item.path || route.path.startsWith(item.path + '/') ? 'text-[var(--accent)] bg-[var(--accent)]/10' : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-glass-hover'"
            >
              {{ item.label }}
            </NuxtLink>
            <!-- 外部文档链接 -->
            <a
              v-for="link in externalLinks"
              :key="link.url"
              :href="link.url"
              target="_blank"
              rel="noopener"
              class="px-3 py-1.5 rounded-lg text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-glass-hover transition-colors flex items-center gap-1"
            >
              {{ link.label }}
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>
            </a>
          </nav>

          <!-- Search -->
          <div class="hidden sm:flex items-center relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索..."
              class="w-0 focus:w-44 opacity-0 focus:opacity-100 bg-glass border border-glass-border rounded-full px-3 py-1.5 pl-9 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] transition-all duration-300 focus:outline-none focus:border-[var(--accent)]/50"
              :class="{ 'w-44 opacity-100': searchOpen }"
              @keydown.enter="handleSearch"
            >
            <button
              class="absolute left-2 p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
              @click="searchOpen = !searchOpen"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
            </button>
          </div>

          <!-- Theme toggle -->
          <button
            class="p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-glass-hover transition-colors"
            aria-label="切换主题"
            :aria-pressed="isDark"
            @click="toggleTheme"
          >
            <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
          </button>

          <!-- User dropdown (logged in) -->
          <div v-if="auth.isLoggedIn && auth.user" class="relative">
            <button
              class="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-glass-hover transition-colors"
              @click="userMenuOpen = !userMenuOpen"
            >
              <img
                v-if="auth.user.avatar_url"
                :src="resolveUploadUrl(auth.user.avatar_url)"
                alt="avatar"
                class="w-7 h-7 rounded-full object-cover border border-glass-border"
              >
              <div v-else class="w-7 h-7 rounded-full bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)] text-xs font-bold">
                {{ auth.user.username.slice(0, 1).toUpperCase() }}
              </div>
              <span class="hidden sm:block text-sm text-[var(--text-secondary)] max-w-[100px] truncate">{{ auth.user.display_name || auth.user.username }}</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="hidden sm:block text-[var(--text-muted)] transition-transform" :class="{ 'rotate-180': userMenuOpen }"><path d="m6 9 6 6 6-6"/></svg>
            </button>

            <!-- Dropdown menu -->
            <Transition name="user-menu">
              <div
                v-if="userMenuOpen"
                ref="userMenuRef"
                class="absolute right-0 top-full mt-2 w-48 rounded-xl glass-panel border border-glass-border shadow-glass overflow-hidden"
              >
                <!-- 管理后台（仅 admin） -->
                <a
                  v-if="auth.user.role === 'admin'"
                  href="/admin/"
                  target="_blank"
                  rel="noopener"
                  class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-[var(--text-secondary)] hover:text-[var(--accent)] hover:bg-glass-hover transition-colors"
                  @click="userMenuOpen = false"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2 2 7l10 5 10-5-10-5Z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/></svg>
                  管理后台
                </a>
                <!-- 个人设置 -->
                <NuxtLink
                  to="/profile"
                  class="flex items-center gap-2.5 px-4 py-2.5 text-sm text-[var(--text-secondary)] hover:text-[var(--accent)] hover:bg-glass-hover transition-colors"
                  @click="userMenuOpen = false"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  个人设置
                </NuxtLink>
                <div class="border-t border-glass-border"></div>
                <!-- 退出登录 -->
                <button
                  class="flex items-center gap-2.5 w-full px-4 py-2.5 text-sm text-[var(--danger)] hover:bg-[var(--danger)]/10 transition-colors"
                  @click="handleLogout"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/></svg>
                  退出登录
                </button>
              </div>
            </Transition>
          </div>

          <!-- Login button (not logged in) -->
          <NuxtLink
            v-else
            to="/login"
            class="hidden sm:inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/30 hover:bg-[var(--accent)]/30 transition-colors"
          >
            登录
          </NuxtLink>

          <!-- Mobile menu button -->
          <button
            class="md:hidden p-2 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-glass-hover transition-colors"
            @click="mobileMenuOpen = !mobileMenuOpen"
          >
            <svg v-if="!mobileMenuOpen" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile drawer -->
    <Transition name="mobile-menu">
      <div v-if="mobileMenuOpen" class="md:hidden absolute top-14 left-0 right-0 bg-[var(--bg-primary)]/95 backdrop-blur-glass border-t border-glass-border shadow-lg">
        <nav class="px-4 py-3 space-y-1">
          <NuxtLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="block px-3 py-2 rounded-lg text-sm font-medium transition-colors text-[var(--text-primary)]"
            :class="route.path === item.path || route.path.startsWith(item.path + '/') ? 'text-[var(--accent)] bg-[var(--accent)]/10' : 'hover:bg-glass-hover'"
            @click="mobileMenuOpen = false"
          >
            {{ item.label }}
          </NuxtLink>
          <!-- 外部文档链接 -->
          <a
            v-for="link in externalLinks"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noopener"
            class="flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium text-[var(--text-primary)] hover:bg-glass-hover transition-colors"
            @click="mobileMenuOpen = false"
          >
            <span class="flex items-center gap-1.5">
              {{ link.label }}
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>
            </span>
          </a>
          <div class="pt-2 border-t border-glass-border mt-2">
            <div class="flex items-center gap-2 px-3 py-2">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索文章或资源..."
                class="flex-1 bg-glass border border-glass-border rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
                @keydown.enter="handleSearch"
              >
              <button class="p-2 text-[var(--text-muted)]" @click="handleSearch">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              </button>
            </div>
            <template v-if="!auth.isLoggedIn">
              <NuxtLink
                to="/login"
                class="block px-3 py-2 mt-1 text-center rounded-lg text-sm font-medium bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/30"
                @click="mobileMenuOpen = false"
              >
                登录 / 注册
              </NuxtLink>
            </template>
            <template v-else>
              <a
                v-if="auth.user?.role === 'admin'"
                href="/admin/"
                target="_blank"
                rel="noopener"
                class="block px-3 py-2 text-sm text-[var(--accent)] border border-[var(--accent)]/30 rounded-lg text-center"
                @click="mobileMenuOpen = false"
              >
                管理后台
              </a>
              <NuxtLink
                to="/profile"
                class="block px-3 py-2 text-sm text-[var(--text-primary)] hover:text-[var(--accent)]"
                @click="mobileMenuOpen = false"
              >
                个人设置
              </NuxtLink>
              <button
                class="block w-full text-left px-3 py-2 text-sm text-[var(--danger)]"
                @click="handleLogout"
              >
                退出登录
              </button>
            </template>
          </div>
        </nav>
      </div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { resolveUploadUrl } from '@windemiko/shared'
import { useAuthStore } from '~~/stores/auth'
import { onClickOutside } from '@vueuse/core'

const route = useRoute()
const auth = useAuthStore()
const { isDark, toggle: toggleTheme } = useTheme()

const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)
const searchOpen = ref(false)
const searchQuery = ref('')
const scrolled = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

const navItems = [
  { label: '首页', path: '/' },
  { label: '博客', path: '/blog' },
  { label: '资源', path: '/resources' },
  { label: '下载', path: '/download' },
]

// 外部链接（新标签页打开）
const externalLinks = [
  { label: '文档', url: 'https://miragedge.top' },
]

// 点击外部关闭用户下拉菜单
onClickOutside(userMenuRef, () => {
  userMenuOpen.value = false
})

function handleLogout() {
  auth.logout()
  userMenuOpen.value = false
  mobileMenuOpen.value = false
}

function handleSearch() {
  if (!searchQuery.value.trim()) return
  const q = encodeURIComponent(searchQuery.value.trim())
  navigateTo(`/blog?q=${q}`)
  searchOpen.value = false
  mobileMenuOpen.value = false
}

function onScroll() {
  scrolled.value = window.scrollY > 20
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<style scoped>
/* 移动端菜单过渡 */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.2s ease;
}
.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* 用户下拉菜单过渡 */
.user-menu-enter-active,
.user-menu-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.user-menu-enter-from,
.user-menu-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
