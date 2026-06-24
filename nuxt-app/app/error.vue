<template>
  <div class="min-h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)] transition-colors duration-300">
    <AppHeader />
    <main class="flex-1 pt-16 flex items-center justify-center px-4 py-12">
      <div class="max-w-lg w-full">
        <div class="glass-panel p-8 sm:p-12 text-center relative overflow-hidden">
          <!-- 装饰背景 -->
          <div class="absolute inset-0 bg-gradient-to-br from-[var(--accent)]/5 via-transparent to-purple-500/5 pointer-events-none" />

          <!-- 错误码 -->
          <div class="relative z-10">
            <div class="text-7xl sm:text-8xl font-bold mb-2 bg-gradient-to-br from-[var(--accent)] to-purple-500 bg-clip-text text-transparent">
              {{ error.statusCode || 500 }}
            </div>

            <!-- 小狐狸 ASCII art -->
            <pre class="text-[var(--text-muted)] text-xs sm:text-sm mb-6 font-mono leading-tight select-none">{{ foxArt }}</pre>

            <h1 class="text-xl sm:text-2xl font-bold text-[var(--text-primary)] mb-2">
              {{ errorTitle }}
            </h1>
            <p class="text-sm text-[var(--text-muted)] mb-8">
              {{ errorMessage }}
            </p>

            <div class="flex flex-wrap items-center justify-center gap-3">
              <button
                class="px-6 py-2.5 rounded-full bg-[var(--accent)] text-white font-medium hover:bg-[var(--accent-hover)] transition-colors"
                @click="handleError"
              >
                返回首页
              </button>
              <button
                class="px-6 py-2.5 rounded-full glass-panel text-[var(--text-primary)] font-medium hover:bg-glass-hover transition-colors"
                @click="goBack"
              >
                返回上一页
              </button>
            </div>
          </div>
        </div>

        <!-- 终端风格提示 -->
        <div class="mt-6 text-center text-xs text-[var(--text-muted)] font-mono">
          <span class="text-[var(--accent)]">$</span> echo "Error {{ error.statusCode || 500 }} - {{ error.statusCode === 404 ? 'Page Not Found' : 'Server Error' }}"
        </div>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{
  error: NuxtError
}>()

const foxArt = `    /\\_/\\
   ( o.o )
    > ^ <`

const errorTitle = computed(() => {
  const code = props.error.statusCode
  if (code === 404) return '页面走丢了喵~'
  if (code === 403) return '没有权限访问'
  if (code === 500) return '服务器出错了'
  if (code === 503) return '服务暂时不可用'
  return props.error.statusMessage || '出错了'
})

const errorMessage = computed(() => {
  const code = props.error.statusCode
  if (code === 404) return '你访问的页面不存在，可能已被移动或删除。'
  if (code === 403) return '抱歉，你没有权限访问此页面。'
  if (code === 500) return '服务器内部错误，请稍后重试。'
  return props.error.message || '发生了未知错误。'
})

function handleError() {
  clearError({ redirect: '/' })
}

function goBack() {
  if (import.meta.client) {
    history.back()
  }
}
</script>
