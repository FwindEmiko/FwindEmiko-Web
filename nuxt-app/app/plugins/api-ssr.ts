// SSR 环境下修正 axios baseURL
//
// 问题：shared 包的 api 实例默认 baseURL='/api'（相对路径）。
//   - 客户端：浏览器解析 /api → https://f.windemiko.top/api → Nuxt server middleware 代理到后端 ✅
//   - SSR：Node.js 无 host 上下文，axios 用 /api 无法发请求，导致刷新页面时数据为空 ❌
//
// 修复：SSR 时将 baseURL 改为后端绝对 URL（来自 runtimeConfig.backendUrl）。
//   客户端保持 /api 相对路径，继续走 server middleware 代理。
import { api } from '@windemiko/shared'

export default defineNuxtPlugin(() => {
  if (import.meta.server) {
    const config = useRuntimeConfig()
    api.defaults.baseURL = `${config.backendUrl}/api`
  }
})
