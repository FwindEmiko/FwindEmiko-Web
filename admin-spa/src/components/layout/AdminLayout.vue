<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { useAppStore } from '@/stores/app'
import AdminSidebar from './AdminSidebar.vue'
import AdminHeader from './AdminHeader.vue'

const app = useAppStore()

function handleResize() {
  app.setMobile(window.innerWidth < 768)
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-[var(--bg)]">
    <!-- desktop sidebar -->
    <AdminSidebar class="hidden md:flex" />

    <!-- mobile sidebar overlay -->
    <div
      v-if="app.isMobile && !app.sidebarCollapsed"
      class="fixed inset-0 z-40 bg-black/40 md:hidden"
      @click="app.setSidebarCollapsed(true)"
    />
    <AdminSidebar
      v-if="app.isMobile"
      class="fixed left-0 top-0 z-50 h-full md:hidden"
      :class="app.sidebarCollapsed ? '-translate-x-full' : 'translate-x-0'"
    />

    <div class="flex flex-col flex-1 min-w-0">
      <AdminHeader />
      <main class="flex-1 overflow-auto p-4 md:p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>
