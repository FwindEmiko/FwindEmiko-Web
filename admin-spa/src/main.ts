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

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
