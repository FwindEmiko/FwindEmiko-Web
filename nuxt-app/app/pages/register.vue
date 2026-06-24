<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 py-12">
    <GlassCard class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)] mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/></svg>
        </div>
        <h1 class="text-2xl font-bold text-[var(--text-primary)]">创建账号</h1>
        <p class="text-sm text-[var(--text-muted)] mt-1">加入狐风轩汐の小屋</p>
      </div>

      <form class="space-y-4" @submit.prevent="handleRegister">
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">用户名</label>
          <input
            v-model="form.username"
            type="text"
            required
            minlength="3"
            maxlength="30"
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="3-30 位字符"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">邮箱</label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="请输入邮箱"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">密码</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="8"
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="至少 8 位"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">昵称（可选）</label>
          <input
            v-model="form.display_name"
            type="text"
            maxlength="100"
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="怎么称呼你"
          >
        </div>
        <button
          type="submit"
          :disabled="auth.loading"
          class="w-full py-2.5 rounded-lg bg-[var(--accent)] text-white font-medium hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-50 disabled:pointer-events-none"
        >
          {{ auth.loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <div class="mt-6 text-center text-sm text-[var(--text-muted)]">
        已有账号？
        <NuxtLink to="/login" class="text-[var(--accent)] hover:text-[var(--accent-hover)]">立即登录</NuxtLink>
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
  email: '',
  password: '',
  display_name: '',
})

onMounted(() => {
  if (auth.isLoggedIn) {
    navigateTo('/profile')
  }
})

async function handleRegister() {
  try {
    await auth.register({
      username: form.username,
      email: form.email,
      password: form.password,
      display_name: form.display_name || null,
    })
    ElMessage.success('注册成功')
    navigateTo('/profile')
  } catch (err: any) {
    ElMessage.error(err?.message || '注册失败')
  }
}
</script>
