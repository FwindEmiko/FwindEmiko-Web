<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Shield,
  Save,
  RefreshCw,
  Lock,
  Plus,
  FileText,
  Package,
  FolderOpen,
  Tag,
  User,
  Bot,
  Settings,
} from 'lucide-vue-next'
import { api } from '@/api/client'

interface RolePermission {
  role: string
  // 文章
  can_create_post: boolean
  can_edit_own_post: boolean
  can_delete_own_post: boolean
  can_publish_post: boolean
  can_edit_others_post: boolean
  can_delete_others_post: boolean
  // 资源
  can_create_resource: boolean
  can_edit_own_resource: boolean
  can_delete_own_resource: boolean
  can_publish_resource: boolean
  can_edit_others_resource: boolean
  can_delete_others_resource: boolean
  // 下载/文件
  can_upload_file: boolean
  can_download_file: boolean
  can_delete_file: boolean
  can_manage_folders: boolean
  // 分类/标签
  can_manage_categories: boolean
  can_manage_tags: boolean
  // 用户管理
  can_view_users: boolean
  can_manage_users: boolean
  // AI 对话
  can_use_chat: boolean
  chat_daily_limit: number
  // 管理员
  can_access_admin: boolean
  created_at?: string
  updated_at?: string
}

const loading = ref(false)
const saving = ref(false)
const roles = ref<RolePermission[]>([])
const selectedRoleName = ref<string>('admin')
const newRoleDialogVisible = ref(false)
const newRoleName = ref('')

// 角色中文名
const roleLabels: Record<string, string> = {
  admin: '管理员',
  author: '作者',
  moderator: '版主',
  member: '成员',
  guest: '访客',
}

// 角色描述
const roleDescriptions: Record<string, string> = {
  admin: '系统管理员，拥有全部权限（不可修改）',
  author: '内容创作者，可上传/管理自己的资源',
  moderator: '版主，可管理他人文章 + 分类标签',
  member: '注册成员，可下载授权资源',
  guest: '未登录访客，仅可查看公开内容',
}

// 权限分组定义（用于 UI 分组展示）
const permissionGroups = [
  {
    key: 'post',
    label: '文章权限',
    icon: FileText,
    color: 'text-blue-400',
    permissions: [
      { key: 'can_create_post', label: '创建文章' },
      { key: 'can_edit_own_post', label: '编辑自己的文章' },
      { key: 'can_delete_own_post', label: '删除自己的文章' },
      { key: 'can_publish_post', label: '发布文章' },
      { key: 'can_edit_others_post', label: '编辑他人的文章' },
      { key: 'can_delete_others_post', label: '删除他人的文章' },
    ],
  },
  {
    key: 'resource',
    label: '资源权限',
    icon: Package,
    color: 'text-emerald-400',
    permissions: [
      { key: 'can_create_resource', label: '创建资源' },
      { key: 'can_edit_own_resource', label: '编辑自己的资源' },
      { key: 'can_delete_own_resource', label: '删除自己的资源' },
      { key: 'can_publish_resource', label: '发布资源' },
      { key: 'can_edit_others_resource', label: '编辑他人的资源' },
      { key: 'can_delete_others_resource', label: '删除他人的资源' },
    ],
  },
  {
    key: 'file',
    label: '文件权限',
    icon: FolderOpen,
    color: 'text-amber-400',
    permissions: [
      { key: 'can_upload_file', label: '上传文件' },
      { key: 'can_download_file', label: '下载文件' },
      { key: 'can_delete_file', label: '删除文件' },
      { key: 'can_manage_folders', label: '管理文件夹' },
    ],
  },
  {
    key: 'category',
    label: '分类标签',
    icon: Tag,
    color: 'text-purple-400',
    permissions: [
      { key: 'can_manage_categories', label: '管理分类' },
      { key: 'can_manage_tags', label: '管理标签' },
    ],
  },
  {
    key: 'user',
    label: '用户管理',
    icon: User,
    color: 'text-rose-400',
    permissions: [
      { key: 'can_view_users', label: '查看用户列表' },
      { key: 'can_manage_users', label: '管理用户（改角色/封禁）' },
    ],
  },
  {
    key: 'chat',
    label: 'AI 对话',
    icon: Bot,
    color: 'text-cyan-400',
    permissions: [
      { key: 'can_use_chat', label: '启用 AI 对话' },
    ],
    extra: [
      { key: 'chat_daily_limit', label: '每日对话限额', type: 'number' as const },
    ],
  },
  {
    key: 'admin',
    label: '后台',
    icon: Settings,
    color: 'text-orange-400',
    permissions: [
      { key: 'can_access_admin', label: '可访问管理后台' },
    ],
  },
]

const selectedRole = computed<RolePermission | undefined>(() =>
  roles.value.find((r) => r.role === selectedRoleName.value),
)

const isAdminRole = computed(() => selectedRoleName.value === 'admin')

async function loadRoles() {
  loading.value = true
  try {
    const res = await api.get<RolePermission[]>('/admin/role-permissions')
    roles.value = res.data
    // 如果当前选中的角色不在列表中，回退到第一个
    if (!roles.value.find((r) => r.role === selectedRoleName.value)) {
      selectedRoleName.value = roles.value[0]?.role || 'admin'
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载角色权限失败')
  } finally {
    loading.value = false
  }
}

function togglePermission(field: string, value: boolean | string | number | undefined) {
  if (isAdminRole.value) return
  const role = selectedRole.value
  if (!role) return
  if (typeof value === 'boolean') {
    ;(role as any)[field] = value
  } else if (typeof value === 'number') {
    ;(role as any)[field] = value
  } else if (typeof value === 'string') {
    ;(role as any)[field] = value
  }
  // undefined 忽略
}

async function savePermissions() {
  if (isAdminRole.value) {
    ElMessage.info('管理员权限不可修改')
    return
  }
  saving.value = true
  try {
    // 提交全部角色（admin 行后端会忽略）
    await api.put('/admin/role-permissions', { items: roles.value })
    ElMessage.success(`${roleLabels[selectedRoleName.value] || selectedRoleName.value} 权限已保存`)
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function createRole() {
  const name = newRoleName.value.trim().toLowerCase()
  if (!name) {
    ElMessage.warning('请输入角色名')
    return
  }
  if (!/^[a-z0-9_]+$/.test(name)) {
    ElMessage.warning('角色名只能包含小写字母、数字和下划线')
    return
  }
  if (roles.value.find((r) => r.role === name)) {
    ElMessage.warning('角色已存在')
    return
  }
  try {
    const res = await api.post<RolePermission>('/admin/role-permissions', { role: name })
    roles.value.push(res.data)
    selectedRoleName.value = name
    newRoleDialogVisible.value = false
    newRoleName.value = ''
    ElMessage.success('角色已创建')
  } catch (error: any) {
    ElMessage.error(error.message || '创建角色失败')
  }
}

function roleLabel(role: string): string {
  return roleLabels[role] || role
}

function roleDescription(role: string): string {
  return roleDescriptions[role] || '自定义角色'
}

onMounted(() => {
  loadRoles()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="admin-page-title flex items-center gap-2">
        <Shield class="w-5 h-5 text-[var(--accent)]" />
        角色权限管理
      </h2>
      <div class="flex gap-2">
        <el-button :icon="Plus" @click="newRoleDialogVisible = true">新建角色</el-button>
        <el-button :icon="RefreshCw" @click="loadRoles" :loading="loading">刷新</el-button>
        <el-button
          type="primary"
          :icon="Save"
          @click="savePermissions"
          :loading="saving"
          :disabled="isAdminRole"
        >
          保存当前角色权限
        </el-button>
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-4">
      <!-- 左侧：角色列表 -->
      <div class="admin-card p-4 md:w-56 shrink-0">
        <div class="text-sm text-[var(--text-secondary)] mb-3">角色列表</div>
        <div class="flex flex-col gap-1" v-loading="loading">
          <button
            v-for="role in roles"
            :key="role.role"
            class="px-3 py-2 rounded-lg text-sm font-medium transition-all text-left border"
            :class="selectedRoleName === role.role
              ? 'bg-[var(--accent)] text-white border-[var(--accent)]'
              : 'bg-transparent text-[var(--text-secondary)] border-transparent hover:border-[var(--accent)] hover:text-[var(--text-primary)]'"
            @click="selectedRoleName = role.role"
          >
            <div class="flex items-center justify-between">
              <span>{{ roleLabel(role.role) }}</span>
              <Lock v-if="role.role === 'admin'" class="w-3.5 h-3.5 opacity-70" />
            </div>
          </button>
          <el-empty
            v-if="!loading && !roles.length"
            description="暂无角色"
            :image-size="60"
          />
        </div>
      </div>

      <!-- 右侧：权限分组卡片 -->
      <div class="flex-1 min-w-0">
        <div v-if="selectedRole" class="admin-card p-4 mb-4">
          <div class="flex items-center gap-2">
            <span class="text-lg font-semibold">{{ roleLabel(selectedRole.role) }}</span>
            <span class="text-xs px-2 py-0.5 rounded bg-[var(--bg-tertiary)] text-[var(--text-secondary)]">
              {{ selectedRole.role }}
            </span>
          </div>
          <p class="text-xs text-[var(--text-muted)] mt-1">{{ roleDescription(selectedRole.role) }}</p>
        </div>

        <div v-if="isAdminRole" class="mb-4 p-3 rounded-lg bg-[var(--accent-light)] flex items-center gap-2 text-sm text-[var(--accent)]">
          <Lock class="w-4 h-4" />
          管理员角色拥有全部权限且不可修改
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4" v-loading="loading">
          <div
            v-for="group in permissionGroups"
            :key="group.key"
            class="admin-card p-4"
          >
            <div class="flex items-center gap-2 mb-3 pb-3 border-b border-[var(--border)]">
              <component :is="group.icon" class="w-4 h-4" :class="group.color" />
              <span class="font-medium">{{ group.label }}</span>
            </div>

            <div class="flex flex-col gap-3">
              <div
                v-for="perm in group.permissions"
                :key="perm.key"
                class="flex items-center justify-between"
              >
                <span class="text-sm">{{ perm.label }}</span>
                <el-switch
                  :model-value="Boolean((selectedRole as any)[perm.key])"
                  :disabled="isAdminRole"
                  @update:model-value="(val: boolean | string | number) => togglePermission(perm.key, val)"
                />
              </div>

              <template v-if="group.extra">
                <div
                  v-for="extra in group.extra"
                  :key="extra.key"
                  class="flex items-center justify-between"
                >
                  <span class="text-sm">{{ extra.label }}</span>
                  <el-input-number
                    v-if="extra.type === 'number'"
                    :model-value="Number((selectedRole as any)[extra.key])"
                    :disabled="isAdminRole"
                    :min="0"
                    :max="100000"
                    size="small"
                    class="!w-32"
                    @update:model-value="(val: number | undefined) => togglePermission(extra.key, val as number)"
                  />
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建角色对话框 -->
    <el-dialog v-model="newRoleDialogVisible" title="新建角色" width="400px">
      <div class="flex flex-col gap-3">
        <div>
          <label class="block text-sm mb-1">角色名</label>
          <el-input
            v-model="newRoleName"
            placeholder="例如：editor、reviewer（小写字母+数字+下划线）"
            @keyup.enter="createRole"
          />
          <p class="text-xs text-[var(--text-muted)] mt-1">
            新角色默认无任何权限，创建后请在右侧权限卡片中配置
          </p>
        </div>
      </div>
      <template #footer>
        <el-button @click="newRoleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createRole">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
