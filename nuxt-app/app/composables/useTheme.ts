export function useTheme() {
  const theme = useCookie('theme', { default: () => 'dark', maxAge: 60 * 60 * 24 * 365 })
  const isDark = computed(() => theme.value === 'dark')

  function applyTheme() {
    if (import.meta.server) return
    if (isDark.value) {
      document.documentElement.classList.remove('light')
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
      document.documentElement.classList.add('light')
    }
  }

  function toggle() {
    theme.value = isDark.value ? 'light' : 'dark'
    applyTheme()
  }

  function set(value: 'dark' | 'light') {
    theme.value = value
    applyTheme()
  }

  onMounted(() => {
    applyTheme()
  })

  return { theme, isDark, toggle, set, applyTheme }
}
