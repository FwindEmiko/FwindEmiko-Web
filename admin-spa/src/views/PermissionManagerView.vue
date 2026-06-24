<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Shield, Save, RefreshCw, Lock } from 'lucide-vue-next'
import { api } from '@/api/client'

interface PermissionItem {
  folder_id: number
  folder_name: string
  role: string
  can_read: boolean
  can_download: boolean
  can_upload: boolean
  can_delete: boolean
}

interface PermissionFolder {
  folder_id: number
  folder_name: string
  permissions: PermissionItem[]
}

interface PermissionMatrix {
  folders: PermissionFolder[]
  roles: string[]
}

const loading = ref(false)
const saving = ref(false)
const matrix = ref<PermissionMatrix>({ folders: [], roles: [] })
const selectedRole = ref<string>('author')

const roleLabels: Record<string, string> = {
  admin: '管理员',
  author: '作者',
  member: '成员',
  guest: '访客',
}

const roleDescriptions: Record<string, string> = {
  admin: '系统管理员，拥有全部权限（不可修改）',
  author: '内容创作者，可上传/管理自己的资源',
  member: '注册成员，可下载授权资源',
  guest: '未登录访客，仅可查看公开内容',
}

// 当前选中角色的权限列表（按文件夹展示）
const currentRolePermissions = computed(() => {
  return matrix.value.folders.map((folder) => {
    const perm = folder.permissions.find((p) => p.role === selectedRole.value)
    return {
      folder_id: folder.folder_id,
      folder_name: folder.folder_name,
      can_read: perm?.can_read ?? false,
      can_download: perm?.can_download ?? false,
      can_upload: perm?.can_upload ?? false,
      can_delete: perm?.can_delete ?? false,
    }
  })
})

const isAdminRole = computed(() => selectedRole.value === 'admin')

async function loadMatrix() {
  loading.value = true
  try {
    const res = await api.get<PermissionMatrix>('/admin/permissions/folders')
    matrix.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载权限矩阵失败')
  } finally {
    loading.value = false
  }
}

function togglePermission(folderId: number, field: 'can_read' | 'can_download' | 'can_upload' | 'can_delete', value: boolean | string | number) {
  if (isAdminRole.value) return
  const folder = matrix.value.folders.find((f) => f.folder_id === folderId)
  if (!folder) return
  const perm = folder.permissions.find((p) => p.role === selectedRole.value)
  if (perm) {
    perm[field] = Boolean(value)
  }
}

async function savePermissions() {
  if (isAdminRole.value) {
    ElMessage.info('管理员权限不可修改')
    return
  }
  saving.value = true
  try {
    const items = matrix.value.folders.flatMap((folder) =>
      folder.permissions
        .filter((p) => p.role === selectedRole.value)
        .map((p) => ({
          folder_id: p.folder_id,
          role: p.role,
          can_read: p.can_read,
          can_download: p.can_download,
          can_upload: p.can_upload,
          can_delete: p.can_delete,
        })),
    )
    await api.put('/admin/permissions', { items })
    ElMessage.success(`${roleLabels[selectedRole.value]} 权限已保存`)
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

async function resetPermissions() {
  try {
    await ElMessageBox.confirm(
      `确定要重置 ${roleLabels[selectedRole.value]} 的所有权限为默认值吗？`,
      '提示',
      { type: 'warning' },
    )
    // 重置为默认值：read=True, 其余 False
    matrix.value.folders.forEach((folder) => {
      const perm = folder.permissions.find((p) => p.role === selectedRole.value)
      if (perm) {
        perm.can_read = true
        perm.can_download = false
        perm.can_upload = false
        perm.can_delete = false
      }
    })
    ElMessage.success('已重置为默认值，请点击保存生效')
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadMatrix()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="admin-page-title flex items-center gap-2">
        <Shield class="w-5 h-5 text-[var(--accent)]" />
        权限管理
      </h2>
      <div class="flex gap-2">
        <el-button :icon="RefreshCw" @click="loadMatrix" :loading="loading">刷新</el-button>
        <el-button type="primary" :icon="Save" @click="savePermissions" :loading="saving" :disabled="isAdminRole">
          保存当前角色权限
        </el-button>
      </div>
    </div>

    <div class="admin-card p-4 mb-4">
      <div class="text-sm text-[var(--text-secondary)] mb-3">选择角色</div>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="role in matrix.roles"
          :key="role"
          class="px-4 py-2 rounded-lg text-sm font-medium transition-all border"
          :class="selectedRole === role
            ? 'bg-[var(--accent)] text-white border-[var(--accent)]'
            : 'bg-[var(--bg)] text-[var(--text-secondary)] border-[var(--border)] hover:border-[var(--accent)]'"
          @click="selectedRole = role"
        >
          {{ roleLabels[role] || role }}
        </button>
      </div>
      <p class="text-xs text-[var(--text-muted)] mt-2">{{ roleDescriptions[selectedRole] }}</p>
    </div>

    <div class="admin-card p-4">
      <div v-loading="loading">
        <div class="flex items-center justify-between mb-3">
          <span class="font-medium">{{ roleLabels[selectedRole] }} 的文件夹权限</span>
          <el-button
            v-if="!isAdminRole"
            size="small"
            :icon="RefreshCw"
            @click="resetPermissions"
          >
            重置为默认
          </el-button>
        </div>

        <el-table :data="currentRolePermissions" stripe style="width: 100%">
          <el-table-column prop="folder_name" label="文件夹" min-width="200" />
          <el-table-column label="读取" width="100" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-model="row.can_read"
                :disabled="isAdminRole"
                @change="(val) => togglePermission(row.folder_id, 'can_read', val)"
              />
            </template>
          </el-table-column>
          <el-table-column label="下载" width="100" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-model="row.can_download"
                :disabled="isAdminRole"
                @change="(val) => togglePermission(row.folder_id, 'can_download', val)"
              />
            </template>
          </el-table-column>
          <el-table-column label="上传" width="100" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-model="row.can_upload"
                :disabled="isAdminRole"
                @change="(val) => togglePermission(row.folder_id, 'can_upload', val)"
              />
            </template>
          </el-table-column>
          <el-table-column label="删除" width="100" align="center">
            <template #default="{ row }">
              <el-checkbox
                v-model="row.can_delete"
                :disabled="isAdminRole"
                @change="(val) => togglePermission(row.folder_id, 'can_delete', val)"
              />
            </template>
          </el-table-column>
        </el-table>

        <div v-if="isAdminRole" class="mt-4 p-3 rounded-lg bg-[var(--accent-light)] flex items-center gap-2 text-sm text-[var(--accent)]">
          <Lock class="w-4 h-4" />
          管理员角色拥有全部权限且不可修改
        </div>

        <el-empty v-if="!loading && !matrix.folders.length" description="暂无文件夹，请先在文件管理中创建" />
      </div>
    </div>
  </div>
</template>
