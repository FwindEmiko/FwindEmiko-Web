<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <GlassCard class="mb-6">
      <div class="flex flex-col sm:flex-row items-center gap-6">
        <div class="relative">
          <img
            v-if="auth.user?.avatar_url"
            :src="resolveUploadUrl(auth.user.avatar_url)"
            alt="avatar"
            class="w-24 h-24 rounded-full object-cover border-2 border-glass-border"
          >
          <div v-else class="w-24 h-24 rounded-full bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)] text-3xl font-bold border-2 border-glass-border">
            {{ auth.user?.username.slice(0, 1).toUpperCase() }}
          </div>
        </div>
        <div class="text-center sm:text-left flex-1">
          <h1 class="text-2xl font-bold text-[var(--text-primary)]">
            {{ auth.user?.display_name || auth.user?.username }}
          </h1>
          <p class="text-[var(--text-muted)] mt-1">@{{ auth.user?.username }}</p>
          <div class="flex flex-wrap items-center justify-center sm:justify-start gap-2 mt-3">
            <span class="px-2.5 py-1 rounded-full text-xs bg-[var(--accent)]/10 text-[var(--accent)] border border-[var(--accent)]/20">
              {{ roleLabel(auth.user?.role) }}
            </span>
            <span class="px-2.5 py-1 rounded-full text-xs bg-glass-hover text-[var(--text-secondary)] border border-glass-border">
              {{ auth.user?.email }}
            </span>
          </div>
        </div>
        <button
          class="px-4 py-2 rounded-lg text-sm font-medium bg-[var(--danger)]/10 text-[var(--danger)] border border-[var(--danger)]/20 hover:bg-[var(--danger)]/20 transition-colors"
          @click="auth.logout"
        >
          退出登录
        </button>
      </div>
    </GlassCard>

    <GlassCard>
      <h2 class="text-lg font-bold text-[var(--text-primary)] mb-6">编辑资料</h2>
      <form class="space-y-4" @submit.prevent="handleUpdate">
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">昵称</label>
          <input
            v-model="form.display_name"
            type="text"
            maxlength="100"
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
          >
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">个人简介</label>
          <textarea
            v-model="form.bio"
            rows="4"
            maxlength="2000"
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] resize-none focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="写点什么介绍自己..."
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-[var(--text-secondary)] mb-1">头像 URL</label>
          <input
            v-model="form.avatar_url"
            type="url"
            maxlength="500"
            class="w-full bg-glass border border-glass-border rounded-lg px-4 py-2.5 text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            placeholder="https://..."
          >
        </div>
        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="updating"
            class="px-6 py-2.5 rounded-lg bg-[var(--accent)] text-white font-medium hover:bg-[var(--accent-hover)] transition-colors disabled:opacity-50 disabled:pointer-events-none"
          >
            {{ updating ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </form>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { GlassCard } from '@windemiko/ui'
import { resolveUploadUrl } from '@windemiko/shared'
import { useAuthStore } from '~~/stores/auth'

definePageMeta({
  layout: 'default',
  middleware: () => {
    const auth = useAuthStore()
    if (import.meta.client && !auth.isLoggedIn) {
      return navigateTo('/login')
    }
  },
})

const auth = useAuthStore()
const updating = ref(false)

const form = reactive({
  display_name: auth.user?.display_name || '',
  bio: auth.user?.bio || '',
  avatar_url: auth.user?.avatar_url || '',
})

watch(() => auth.user, (user) => {
  if (user) {
    form.display_name = user.display_name || ''
    form.bio = user.bio || ''
    form.avatar_url = user.avatar_url || ''
  }
}, { immediate: true })

function roleLabel(role?: string) {
  const map: Record<string, string> = {
    admin: '管理员',
    author: '作者',
    member: '会员',
    guest: '访客',
  }
  return map[role || 'guest'] || role
}

async function handleUpdate() {
  updating.value = true
  try {
    await auth.updateProfile({
      display_name: form.display_name || null,
      bio: form.bio || null,
      avatar_url: form.avatar_url || null,
    })
    ElMessage.success('资料已更新')
  } catch (err: any) {
    ElMessage.error(err?.message || '更新失败')
  } finally {
    updating.value = false
  }
}
</script>
