<template>
  <footer class="border-t border-glass-border mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
      <!-- 三列：Brand / 小狐狸 / About -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">

        <!-- Brand -->
        <div class="flex flex-col items-center md:items-start text-center md:text-left">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-6 h-6 rounded-lg bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)]">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
            </div>
            <span class="font-bold text-sm text-[var(--text-primary)]">狐风轩汐の小屋</span>
          </div>
          <p class="text-xs text-[var(--text-muted)] leading-relaxed">
            代码 · 游戏 · 创作<br>
            记录技术与生活的碎片，分享 Minecraft 资源与工具。
          </p>
        </div>

        <!-- ASCII fox — 居中代替导航 -->
        <div
          class="select-none cursor-pointer transition-opacity hover:opacity-100 opacity-60 flex justify-center"
          title="点击 5 次解锁彩蛋"
          @click="handleFoxClick"
        >
          <pre class="text-[var(--color-terminal)] text-xs font-mono leading-tight">{{ asciiFox }}</pre>
        </div>

        <!-- About -->
        <div class="flex flex-col items-center md:items-start text-center md:text-left">
          <h3 class="font-medium text-xs text-[var(--text-primary)] mb-2">关于</h3>
          <p class="text-xs text-[var(--text-muted)] leading-relaxed">
            本站采用 Nuxt 3 + FastAPI 构建<br>
            玻璃拟态 × 二次元 × 代码极客风格
          </p>
        </div>
      </div>

      <!-- 版权 + 备案号 -->
      <div class="mt-6 pt-4 border-t border-glass-border flex flex-col items-center gap-1.5 text-xs text-[var(--text-muted)]">
        <p>© {{ new Date().getFullYear() }} 狐风轩汐の小屋. All rights reserved.</p>
        <p>
          <a
            href="https://beian.miit.gov.cn/"
            target="_blank"
            rel="noopener"
            class="text-[11px] hover:text-[var(--accent)] transition-colors"
          >
            苏ICP备2024133820号-2
          </a>
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const asciiFox = `    /\\_/\\\n   ( o.o )\n    > ^ <\n  狐风轩汐の小屋 © 2026`

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
  if (isOn) {
    console.log('%c[HACKER MODE] 暗绿终端主题已激活喵~', 'color: #00FF41; font-family: monospace;')
  }
}
</script>
