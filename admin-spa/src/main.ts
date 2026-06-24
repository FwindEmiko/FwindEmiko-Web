import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from '@/router'
import App from './App.vue'
import './style.css'

// Element Plus 函数式组件样式
import 'element-plus/theme-chalk/el-message.css'
import 'element-plus/theme-chalk/el-message-box.css'
import 'element-plus/theme-chalk/el-notification.css'

// Vditor 编辑器样式（避免依赖 CDN 加载 CSS 导致编辑器不可用）
import 'vditor/dist/index.css'

// 主题同步：从主站 cookie 读取 theme，应用到 html 根元素
// 主站使用 useCookie 写入 theme=dark|light，admin-spa 读取同一 cookie 同步主题
function applyThemeFromCookie() {
  const match = document.cookie.match(/theme=([^;]+)/)
  const theme = match ? decodeURIComponent(match[1]) : 'dark'
  const root = document.documentElement
  root.classList.remove('dark', 'light')
  if (theme === 'light') {
    root.classList.add('light')
  } else {
    root.classList.add('dark')
  }
}

applyThemeFromCookie()

// 监听 cookie 变化（主站切换主题时同步）
let lastTheme = document.cookie.match(/theme=([^;]+)/)?.[1] || 'dark'
setInterval(() => {
  const current = document.cookie.match(/theme=([^;]+)/)?.[1] || 'dark'
  if (current !== lastTheme) {
    lastTheme = current
    applyThemeFromCookie()
  }
}, 1000)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
