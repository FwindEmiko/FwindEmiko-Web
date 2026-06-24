import axios, { AxiosError, type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios'
import { API_BASE_URL } from '@windemiko/shared'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setTokens(access: string, refresh: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access)
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
})

let isRefreshing = false
let refreshQueue: Array<(token: string) => void> = []

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code !== 0) {
        return Promise.reject(new Error(data.message || '请求失败'))
      }
      return { ...response, data: data.data }
    }
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean }
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      if (!getRefreshToken()) {
        clearTokens()
        window.location.href = '/admin/#/login'
        return Promise.reject(error)
      }
      originalRequest._retry = true
      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`
            }
            resolve(api(originalRequest))
          })
        })
      }
      isRefreshing = true
      try {
        const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: getRefreshToken(),
        })
        const wrapper = res.data
        const tokenData = wrapper?.code === 0 ? wrapper.data : wrapper
        const newAccess = tokenData.access_token
        if (!newAccess) throw new Error('刷新失败')
        localStorage.setItem(ACCESS_TOKEN_KEY, newAccess)
        refreshQueue.forEach((cb) => cb(newAccess))
        refreshQueue = []
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccess}`
        }
        return api(originalRequest)
      } catch (refreshError) {
        clearTokens()
        window.location.href = '/admin/#/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    const errData = error.response?.data as { message?: string } | undefined
    const message = errData?.message || error.message || '网络错误'
    return Promise.reject(new Error(message))
  }
)

export function formatBytes(bytes?: number | null): string {
  if (bytes == null || bytes === 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0
  let size = bytes
  while (size >= 1024 && i < units.length - 1) {
    size /= 1024
    i++
  }
  return `${size.toFixed(1)} ${units[i]}`
}

// 本地化时间格式化 (P1-5): YYYY-MM-DD HH:mm
export function formatDateTime(value?: string | null): string {
  if (!value) return '-'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '-'
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
