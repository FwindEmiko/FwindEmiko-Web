export function useTheme() {
  // 显式设置 path 和 sameSite，确保移动端 Cookie 正确写入
  const theme = useCookie<'dark' | 'light'>('theme', {
    default: () => 'dark',
    maxAge: 60 * 60 * 24 * 365,
    path: '/',
    sameSite: 'lax',
  })
  const isDark = computed(() => theme.value === 'dark')

  function applyTheme() {
    if (import.meta.server) return
    const root = document.documentElement
    if (isDark.value) {
      root.classList.remove('light')
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
      root.classList.add('light')
    }
    // 移动端兜底：直接写 document.cookie，防止 useCookie 同步失败
    document.cookie = `theme=${theme.value}; path=/; max-age=31536000; samesite=lax`
  }

  function toggle() {
    theme.value = isDark.value ? 'light' : 'dark'
    applyTheme()
  }

  function set(value: 'dark' | 'light') {
    theme.value = value
    applyTheme()
  }

  // 客户端首次挂载时应用主题
  onMounted(() => {
    applyTheme()
  })

  // 监听 theme 变化，确保任何来源的修改都能触发 class 更新
  watch(theme, () => {
    applyTheme()
  })

  return { theme, isDark, toggle, set, applyTheme }
}
