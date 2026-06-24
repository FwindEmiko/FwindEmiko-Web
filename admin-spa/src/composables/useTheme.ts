import { ref } from 'vue'

type Theme = 'dark' | 'light'

const currentTheme = ref<Theme>('dark')

function readCookieTheme(): Theme {
  const match = document.cookie.match(/theme=([^;]+)/)
  const theme = match ? decodeURIComponent(match[1]) : 'dark'
  return theme === 'light' ? 'light' : 'dark'
}

function applyTheme(theme: Theme) {
  currentTheme.value = theme
  const root = document.documentElement
  root.classList.remove('dark', 'light')
  root.classList.add(theme)
  // 写入 cookie，与主站共享（path=/ 确保全站生效）
  const maxAge = 60 * 60 * 24 * 365
  document.cookie = `theme=${encodeURIComponent(theme)};path=/;max-age=${maxAge};SameSite=Lax`
}

function toggleTheme() {
  const next: Theme = currentTheme.value === 'dark' ? 'light' : 'dark'
  applyTheme(next)
}

/** 初始化主题（从 cookie 读取） */
export function initTheme() {
  applyTheme(readCookieTheme())
}

export function useTheme() {
  return {
    currentTheme,
    toggleTheme,
    initTheme,
  }
}
