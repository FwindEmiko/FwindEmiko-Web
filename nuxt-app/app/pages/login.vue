<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12">
    <GlassCard class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)] mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <h1 class="text-2xl font-bold text-[var(--text-primary)]">欢迎回来</h1>
        <p class="text-sm text-[var(--text-muted)] mt-1">登录狐风轩汐の小屋</p>
      </div>

      <form class="space-y-4" @submit.prevent="handleLogin">
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">用户名</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="请输入用户名"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">密码</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="请输入密码"
          >
        </div>
        <button
          type="submit"
          :disabled="auth.loading"
          class="w-full py-2.5 rounded-lg bg-[var(--accent)] text-white font-medium hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-50 disabled:pointer-events-none"
        >
          {{ auth.loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="mt-6 text-center text-sm text-[var(--text-muted)]">
        还没有账号？
        <NuxtLink to="/register" class="text-[var(--accent)] hover:text-[var(--accent-hover)]">立即注册</NuxtLink>
      </div>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { GlassCard } from '@windemiko/ui'
import { useAuthStore } from '~~/stores/auth'

definePageMeta({
  layout: 'default',
})

const auth = useAuthStore()
const form = reactive({
  username: '',
  password: '',
})

onMounted(() => {
  if (auth.isLoggedIn) {
    navigateTo('/profile')
  }
})

async function handleLogin() {
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    navigateTo('/profile')
  } catch (err: any) {
    ElMessage.error(err?.message || '登录失败')
  }
}
</script>
