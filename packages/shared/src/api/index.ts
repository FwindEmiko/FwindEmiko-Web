// Axios 封装 + 各模块 API 函数
import axios, { AxiosError, type AxiosInstance, type AxiosRequestConfig } from 'axios'
import type {
  ApiResponse,
  UserInfo,
  UserLogin,
  UserRegister,
  LoginResponse,
  UserUpdateMe,
  PaginatedPosts,
  PostDetailResponse,
  CategoryOut,
  TagOut,
  PaginatedResources,
  ResourceDetail,
  FolderTreeNode,
  FolderFilesResponse,
  ChatSessionOut,
  ChatSessionCreate,
  ChatMessageOut,
  ChatMessageCreate,
  ChatQuotaOut,
} from '../types'

// 默认使用相对路径 /api，由各前端代理（Nuxt server middleware / Nginx / Vite devProxy）转发到后端
// 本地开发如需直连后端，可在 .env 中设置 VITE_API_BASE_URL=http://localhost:8000/api
export const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || '/api'
export const UPLOAD_BASE_URL = import.meta.env?.VITE_UPLOAD_BASE_URL || ''

// 浏览器/客户端环境判定
const isClient = typeof window !== 'undefined'

// 统一 API 实例
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Token 读写
function getAccessToken(): string | null {
  if (!isClient) return null
  return localStorage.getItem('access_token')
}

function setTokens(access: string, refresh: string) {
  if (!isClient) return
  localStorage.setItem('access_token', access)
  localStorage.setItem('refresh_token', refresh)
}

function clearTokens() {
  if (!isClient) return
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

// 请求拦截器：注入 JWT
api.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 统一错误处理
export class ApiError extends Error {
  code: number
  status?: number

  constructor(code: number, message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

async function unwrap<T>(promise: Promise<{ data: T | ApiResponse<T> }>): Promise<T> {
  const { data } = await promise
  // 兼容后端统一包装格式 { code, data, message } 与原始返回格式
  if (data && typeof data === 'object' && 'code' in data && 'data' in data) {
    if (data.code !== 0) {
      throw new ApiError(data.code, data.message || '请求失败')
    }
    return data.data as T
  }
  return data as T
}

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiResponse<unknown>>) => {
    if (error.response?.status === 401) {
      clearTokens()
      if (isClient && !window.location.pathname.startsWith('/login')) {
        window.location.href = '/login'
      }
    }
    const message = error.response?.data?.message || error.message || '网络错误'
    return Promise.reject(new ApiError(error.response?.data?.code || error.response?.status || 500, message, error.response?.status))
  },
)

// ===== Auth =====
export const authApi = {
  async login(payload: UserLogin): Promise<LoginResponse> {
    const res = await unwrap(api.post<ApiResponse<LoginResponse>>('/auth/login', payload))
    setTokens(res.access_token, res.refresh_token)
    return res
  },
  async register(payload: UserRegister): Promise<LoginResponse> {
    const res = await unwrap(api.post<ApiResponse<LoginResponse>>('/auth/register', payload))
    setTokens(res.access_token, res.refresh_token)
    return res
  },
  async me(): Promise<UserInfo> {
    return unwrap(api.get<ApiResponse<UserInfo>>('/auth/me'))
  },
  async updateMe(payload: UserUpdateMe): Promise<UserInfo> {
    return unwrap(api.put<ApiResponse<UserInfo>>('/auth/me', payload))
  },
  async refresh(refreshToken: string): Promise<{ access_token: string; token_type: string }> {
    return unwrap(api.post<ApiResponse<{ access_token: string; token_type: string }>>('/auth/refresh', { refresh_token: refreshToken }))
  },
  logout() {
    clearTokens()
  },
  getToken: getAccessToken,
}

// ===== Blog =====
export const blogApi = {
  listPosts(params?: { page?: number; size?: number; category?: string; tag?: string; q?: string }) {
    return unwrap(api.get<ApiResponse<PaginatedPosts>>('/posts', { params }))
  },
  getPost(slug: string) {
    return unwrap(api.get<ApiResponse<PostDetailResponse>>(`/posts/${slug}`))
  },
  listCategories() {
    return unwrap(api.get<ApiResponse<CategoryOut[]>>('/categories'))
  },
  listTags() {
    return unwrap(api.get<ApiResponse<TagOut[]>>('/tags'))
  },
}

// ===== Resources =====
export const resourceApi = {
  listResources(params?: {
    page?: number
    size?: number
    type?: string
    version?: string
    loader?: string
    q?: string
    sort?: 'downloads' | 'newest'
  }) {
    return unwrap(api.get<ApiResponse<PaginatedResources>>('/resources', { params }))
  },
  getResource(slug: string) {
    return unwrap(api.get<ApiResponse<ResourceDetail>>(`/resources/${slug}`))
  },
  downloadVersion(resourceId: number, versionId: number) {
    return `${API_BASE_URL}/resources/${resourceId}/versions/${versionId}/download`
  },
}

// ===== Downloads =====
export const downloadApi = {
  listFolders() {
    return unwrap(api.get<ApiResponse<FolderTreeNode[]>>('/downloads/folders'))
  },
  listFolderFiles(folderId: number) {
    return unwrap(api.get<ApiResponse<FolderFilesResponse>>(`/downloads/folders/${folderId}/files`))
  },
  downloadFile(fileId: number) {
    return `${API_BASE_URL}/downloads/files/${fileId}/download`
  },
}

// ===== Chat =====
export const chatApi = {
  listSessions() {
    return unwrap(api.get<ApiResponse<ChatSessionOut[]>>('/chat/sessions'))
  },
  createSession(payload?: ChatSessionCreate) {
    return unwrap(api.post<ApiResponse<ChatSessionOut>>('/chat/sessions', payload || {}))
  },
  listMessages(sessionId: number) {
    return unwrap(api.get<ApiResponse<ChatMessageOut[]>>(`/chat/sessions/${sessionId}/messages`))
  },
  sendMessageStream(
    sessionId: number,
    payload: ChatMessageCreate,
    onEvent: (event: { type: 'chunk'; content: string } | { type: 'done'; message_id?: number } | { type: 'error'; message: string }) => void,
  ) {
    const url = `${API_BASE_URL}/chat/sessions/${sessionId}/messages`
    const eventSource = new EventSource(url, {
      withCredentials: true,
    } as EventSourceInit)

    // EventSource 不支持 POST + body，需使用 fetch SSE
    // 这里 fallback 到 fetch 以支持 POST body
    const controller = new AbortController()
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${getAccessToken() || ''}`,
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    })
      .then(async (res) => {
        if (!res.ok || !res.body) {
          onEvent({ type: 'error', message: 'SSE 连接失败' })
          return
        }
        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n\n')
          buffer = lines.pop() || ''
          for (const chunk of lines) {
            const line = chunk.trim()
            if (!line.startsWith('data:')) continue
            try {
              const event = JSON.parse(line.slice(5).trim())
              onEvent(event)
            } catch {
              // ignore malformed
            }
          }
        }
      })
      .catch((err) => {
        onEvent({ type: 'error', message: err.message || 'SSE 请求异常' })
      })

    return () => controller.abort()
  },
  getQuota() {
    return unwrap(api.get<ApiResponse<ChatQuotaOut>>('/chat/quota'))
  },
  deleteSession(sessionId: number) {
    return unwrap(api.delete<ApiResponse<null>>(`/chat/sessions/${sessionId}`))
  },
}

// 通用请求工具
export async function request<T>(config: AxiosRequestConfig): Promise<T> {
  return unwrap(api.request<ApiResponse<T>>(config))
}

export function resolveUploadUrl(path?: string | null): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${UPLOAD_BASE_URL}${path.startsWith('/') ? '' : '/'}${path}`
}
