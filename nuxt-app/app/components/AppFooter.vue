<template>
  <footer class="border-t border-glass-border mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
      <!-- 三列对称布局 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">

        <!-- Brand -->
        <div class="flex flex-col items-center md:items-start text-center md:text-left">
          <h3 class="font-medium text-xs text-[var(--text-primary)] mb-2">狐风轩汐の小屋</h3>
          <p class="text-xs text-[var(--text-muted)] leading-relaxed">
            代码 · 游戏 · 创作<br>
            记录技术与生活的碎片，分享 Minecraft 资源与工具。
          </p>
        </div>

        <!-- ASCII fox — 居中代替导航 -->
        <div
          class="select-none cursor-pointer transition-opacity hover:opacity-100 opacity-60 flex justify-center items-center"
          title="点击 5 次解锁彩蛋"
          @click="handleFoxClick"
        >
          <pre class="text-[var(--color-terminal)] text-xs font-mono leading-tight">{{ asciiFox }}</pre>
        </div>

        <!-- About -->
        <div class="flex flex-col items-center md:items-end text-center md:text-right">
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

let clickCount = 0
let clickTimer: ReturnType<typeof setTimeout> | null = null

function handleFoxClick() {
  clickCount++
  if (clickTimer) clearTimeout(clickTimer)
  clickTimer = setTimeout(() => { clickCount = 0 }, 2000)
  if (clickCount >= 5) {
    clickCount = 0
    toggleHackerMode()
  }
}

function toggleHackerMode() {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  root.classList.toggle('hacker-mode')
  if (root.classList.contains('hacker-mode')) {
    console.log('%c[HACKER MODE] 暗绿终端主题已激活喵~', 'color: #00FF41; font-family: monospace;')
  }
}
</script>
