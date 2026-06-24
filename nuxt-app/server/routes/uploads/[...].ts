// Nuxt server middleware: 将 /uploads/** 请求代理到后端
// 生产环境通过 BACKEND_URL=http://backend:8000 (Docker 内部网络)
// 开发环境默认 http://localhost:8000
export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  const target = config.backendUrl + event.path
  return proxyRequest(event, target)
})
