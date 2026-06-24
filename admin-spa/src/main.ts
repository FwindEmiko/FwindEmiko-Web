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

// 主题管理：从主站 cookie 读取 theme，应用到 html 根元素
// 主站使用 useCookie 写入 theme=dark|light，admin-spa 读取同一 cookie 同步主题
import { initTheme } from '@/composables/useTheme'

initTheme()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
