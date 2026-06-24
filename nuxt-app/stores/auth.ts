import { defineStore } from 'pinia'
import type { UserInfo, UserLogin, UserRegister } from '@windemiko/shared'
import { authApi } from '@windemiko/shared'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!user.value && !!token.value)

  async function init() {
    if (import.meta.server) return
    const saved = localStorage.getItem('access_token')
    if (saved) {
      token.value = saved
      try {
        user.value = await authApi.me()
      } catch {
        token.value = null
        user.value = null
        authApi.logout()
      }
    }
  }

  async function login(payload: UserLogin) {
    loading.value = true
    try {
      const res = await authApi.login(payload)
      user.value = res.user
      token.value = res.access_token
      return res.user
    } finally {
      loading.value = false
    }
  }

  async function register(payload: UserRegister) {
    loading.value = true
    try {
      const res = await authApi.register(payload)
      user.value = res.user
      token.value = res.access_token
      return res.user
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    authApi.logout()
    navigateTo('/')
  }

  async function updateProfile(payload: { display_name?: string | null; bio?: string | null; avatar_url?: string | null }) {
    if (!isLoggedIn.value) return
    const updated = await authApi.updateMe(payload)
    user.value = updated
    return updated
  }

  return {
    user,
    token,
    loading,
    isLoggedIn,
    init,
    login,
    register,
    logout,
    updateProfile,
  }
})
