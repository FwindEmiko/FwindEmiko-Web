import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api, clearTokens, setTokens } from '@/api/client'
import type { LoginResponse, UserInfo } from '@windemiko/shared'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref<string | null>(null)
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username: string, password: string) {
    const res = await api.post<LoginResponse>('/auth/login', { username, password })
    const data = res.data
    token.value = data.access_token
    user.value = data.user
    setTokens(data.access_token, data.refresh_token)
    return data.user
  }

  function logout() {
    user.value = null
    token.value = null
    clearTokens()
  }

  async function restore() {
    const access = localStorage.getItem('admin_access_token')
    if (!access) return false
    token.value = access
    try {
      const res = await api.get<UserInfo>('/auth/me')
      user.value = res.data
      return true
    } catch {
      logout()
      return false
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    restore,
  }
})
