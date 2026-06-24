import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const isMobile = ref(false)

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setSidebarCollapsed(value: boolean) {
    sidebarCollapsed.value = value
  }

  function setMobile(value: boolean) {
    isMobile.value = value
    if (value) {
      sidebarCollapsed.value = true
    }
  }

  return {
    sidebarCollapsed,
    isMobile,
    toggleSidebar,
    setSidebarCollapsed,
    setMobile,
  }
})
