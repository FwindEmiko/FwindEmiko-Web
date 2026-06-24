<template>
  <footer class="border-t border-glass-border mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- Brand -->
        <div>
          <div class="flex items-center gap-2 mb-3">
            <div class="w-7 h-7 rounded-lg bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)]">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
            </div>
            <span class="font-bold text-[var(--text-primary)]">狐风轩汐の小屋</span>
          </div>
          <p class="text-sm text-[var(--text-muted)] leading-relaxed">
            代码 · 游戏 · 创作<br>
            记录技术与生活的碎片，分享 Minecraft 资源与工具。
          </p>
        </div>

        <!-- Links -->
        <div>
          <h3 class="font-medium text-[var(--text-primary)] mb-3">导航</h3>
          <ul class="space-y-2 text-sm">
            <li><NuxtLink to="/" class="text-[var(--text-muted)] hover:text-[var(--accent)]">首页</NuxtLink></li>
            <li><NuxtLink to="/blog" class="text-[var(--text-muted)] hover:text-[var(--accent)]">博客</NuxtLink></li>
            <li><NuxtLink to="/resources" class="text-[var(--text-muted)] hover:text-[var(--accent)]">资源</NuxtLink></li>
            <li><NuxtLink to="/download" class="text-[var(--text-muted)] hover:text-[var(--accent)]">下载</NuxtLink></li>
          </ul>
        </div>

        <!-- Social -->
        <div>
          <h3 class="font-medium text-[var(--text-primary)] mb-3">关注我</h3>
          <div class="flex items-center gap-3">
            <a href="#" class="w-9 h-9 rounded-lg glass-panel flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--accent)] transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
            </a>
            <a href="#" class="w-9 h-9 rounded-lg glass-panel flex items-center justify-center text-[var(--text-muted)] hover:text-[var(--accent)] transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            </a>
          </div>
        </div>
      </div>

      <!-- ASCII art fox (P1-2) -->
      <div
        class="mt-8 mb-6 select-none cursor-pointer transition-opacity hover:opacity-100 opacity-60"
        title="点击 5 次解锁彩蛋"
        @click="handleFoxClick"
      >
        <pre class="text-[var(--color-terminal)] text-xs sm:text-sm font-mono leading-tight">{{ asciiFox }}</pre>
      </div>

      <div class="pt-6 border-t border-glass-border flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-[var(--text-muted)]">
        <p>© {{ new Date().getFullYear() }} 狐风轩汐の小屋. All rights reserved.</p>
        <p>京ICP备XXXXXXXX号-1 | 仅供学习交流使用</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const asciiFox = `    /\\_/\\
   ( o.o )
    > ^ <
  狐风轩汐の小屋 © 2026`

// Hacker mode easter egg: 5 clicks toggles terminal theme (P1-2)
let clickCount = 0
let clickTimer: ReturnType<typeof setTimeout> | null = null

function handleFoxClick() {
  clickCount++
  if (clickTimer) clearTimeout(clickTimer)
  clickTimer = setTimeout(() => {
    clickCount = 0
  }, 2000)

  if (clickCount >= 5) {
    clickCount = 0
    toggleHackerMode()
  }
}

function toggleHackerMode() {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.classList.toggle('hacker-mode')
  const isOn = root.classList.contains('hacker-mode')
  // Show a quick visual feedback
  if (isOn) {
    console.log('%c[HACKER MODE] 暗绿终端主题已激活喵~', 'color: #00FF41; font-family: monospace;')
  }
}
</script>
