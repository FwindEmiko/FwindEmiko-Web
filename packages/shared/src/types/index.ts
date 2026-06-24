export interface ApiResponse<T = unknown> {
  code: number
  data: T
  message: string
}

export interface UserInfo {
  id: number
  username: string
  email: string
  display_name?: string | null
  avatar_url?: string | null
  bio?: string | null
  role: string
  is_active: boolean
  is_verified?: boolean
  created_at: string
  updated_at?: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface UserRegister {
  username: string
  email: string
  password: string
  display_name?: string | null
}

export interface UserUpdateMe {
  display_name?: string | null
  bio?: string | null
  avatar_url?: string | null
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type?: string
  user: UserInfo
}

export interface CategoryOut {
  id: number
  name: string
  slug: string
  description?: string | null
  created_at: string
  post_count?: number
}

export interface TagOut {
  id: number
  name: string
  slug: string
  created_at: string
  post_count?: number
}

export interface AuthorBrief {
  id: number
  username: string
  display_name?: string | null
}

export interface PostListItem {
  id: number
  title: string
  slug: string
  summary?: string | null
  cover_url?: string | null
  status: 'draft' | 'published' | 'archived'
  is_pinned: boolean
  view_count: number
  published_at?: string | null
  created_at: string
  updated_at: string
  author: AuthorBrief
  category?: CategoryOut | null
  tags: TagOut[]
}

export interface PostDetail extends PostListItem {
  content_md: string
  content_html?: string
}

export interface PostDetailResponse {
  post: PostDetail
  prev_post: { id: number; title: string; slug: string } | null
  next_post: { id: number; title: string; slug: string } | null
}

export interface PaginatedPosts {
  items: PostListItem[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ResourceVersionOut {
  id: number
  resource_id: number
  version_string: string
  changelog?: string | null
  file_url?: string | null
  external_url?: string | null
  /** 下载方式：local=本站上传 / external=外链网盘 */
  download_type?: 'local' | 'external'
  /** 外链网盘标签（如 "百度网盘"），仅 external 时使用 */
  external_label?: string | null
  file_size?: number | null
  file_hash?: string | null
  downloads: number
  is_prerelease: boolean
  created_at: string
}

export interface ScreenshotOut {
  id: number
  resource_id: number
  image_url: string
  thumb_url?: string | null
  caption?: string | null
  sort_order: number
}

export interface ResourceListItem {
  id: number
  title: string
  slug: string
  description: string
  type: 'plugin' | 'mod' | 'datapack' | 'tool'
  game_versions: string[]
  loaders: string[]
  icon_url?: string | null
  cover_url?: string | null
  download_count: number
  status: 'draft' | 'published'
  created_at: string
  updated_at: string
  latest_version?: ResourceVersionOut | null
}

export interface ResourceDetail extends ResourceListItem {
  versions: ResourceVersionOut[]
  screenshots: ScreenshotOut[]
}

export interface PaginatedResources {
  items: ResourceListItem[]
  total: number
  page: number
  size: number
  pages: number
}

export interface FolderPermissionRule {
  role: 'admin' | 'author' | 'member' | 'guest'
  can_read: boolean
  can_download: boolean
}

export interface FolderTreeNode {
  id: number
  name: string
  slug: string
  description?: string | null
  is_visible: boolean
  sort_order: number
  children: FolderTreeNode[]
}

export interface BreadcrumbItem {
  id: number
  name: string
}

export interface SubFolderItem {
  id: number
  name: string
  slug: string
}

export interface FileItem {
  id: number
  filename: string
  display_name?: string | null
  file_size: number
  mime_type?: string | null
  download_count: number
  has_external: boolean
  created_at: string
}

export interface FolderFilesResponse {
  folder: FolderTreeNode
  breadcrumbs: BreadcrumbItem[]
  subfolders: SubFolderItem[]
  files: FileItem[]
}

export interface AdminStats {
  posts: number
  resources: number
  files: number
  downloads: number
  recent_posts: {
    id: number
    title: string
    status: string
    author?: string | null
    created_at?: string | null
  }[]
  recent_uploads: {
    id: number
    filename: string
    folder_id: number
    created_at?: string | null
  }[]
}

export interface PaginatedUsers {
  items: UserInfo[]
  total: number
  page: number
  size: number
}

export interface ChatSessionOut {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface ChatSessionCreate {
  title?: string
}

export interface ChatMessageOut {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ChatMessageCreate {
  content: string
}

export interface ChatQuotaOut {
  used: number
  limit: number | null
  remaining: number
}
