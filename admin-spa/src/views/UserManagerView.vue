<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from 'lucide-vue-next'
import { api, formatDateTime } from '@/api/client'
import type { UserInfo } from '@windemiko/shared'

const loading = ref(false)
const users = ref<UserInfo[]>([])
const tableUsers = computed(() => users.value as any[])
const pagination = reactive({ page: 1, size: 20, total: 0 })
const filters = reactive({ q: '' })

const roleOptions = [
  { label: '管理员', value: 'admin' },
  { label: '作者', value: 'author' },
  { label: '会员', value: 'member' },
]

async function loadUsers() {
  loading.value = true
  try {
    const params: Record<string, any> = { page: pagination.page, size: pagination.size }
    if (filters.q.trim()) params.q = filters.q.trim()
    const res = await api.get<{ items: UserInfo[]; total: number; page: number; size: number }>(
      '/admin/users',
      { params }
    )
    users.value = res.data.items
    pagination.total = res.data.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载用户失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  pagination.page = 1
  loadUsers()
}

async function updateRole(user: UserInfo, role: string) {
  try {
    await api.put(`/admin/users/${user.id}/role`, null, { params: { role } })
    user.role = role
    ElMessage.success('角色已更新')
  } catch (error: any) {
    ElMessage.error(error.message || '更新失败')
    loadUsers()
  }
}

async function toggleStatus(user: UserInfo) {
  const next = !user.is_active
  try {
    await ElMessageBox.confirm(
      `确定${next ? '启用' : '禁用'}用户 ${user.username} 吗？`,
      '提示',
      { type: 'warning' }
    )
    await api.put(`/admin/users/${user.id}/status`, null, { params: { is_active: next } })
    user.is_active = next
    ElMessage.success(`已${next ? '启用' : '禁用'}`)
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '操作失败')
      loadUsers()
    }
  }
}

function onPageChange(page: number) {
  pagination.page = page
  loadUsers()
}

onMounted(loadUsers)
</script>

<template>
  <div>
    <h2 class="admin-page-title">用户管理</h2>

    <!-- Search bar (P1-5) -->
    <div class="admin-card p-4 mb-4 flex items-center gap-3">
      <el-input
        v-model="filters.q"
        placeholder="搜索用户名..."
        class="max-w-xs"
        clearable
        @keydown.enter="onSearch"
        @clear="onSearch"
      >
        <template #prefix>
          <Search class="w-4 h-4 text-[var(--text-muted)]" />
        </template>
      </el-input>
      <el-button type="primary" @click="onSearch">搜索</el-button>
    </div>

    <div class="admin-card p-4">
      <el-table v-loading="loading" :data="tableUsers">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" min-width="120" />
        <el-table-column label="昵称" min-width="120">
          <template #default="{ row }">
            {{ row.display_name || row.username }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column label="角色" width="140">
          <template #default="{ row }">
            <el-select
              :model-value="row.role"
              size="small"
              class="w-full"
              @change="(val: string) => updateRole(row as UserInfo, val)"
            >
              <el-option
                v-for="opt in roleOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.is_active"
              @change="() => toggleStatus(row as UserInfo)"
            />
          </template>
        </el-table-column>
        <el-table-column label="注册时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <div class="flex justify-end mt-4">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.size"
          :total="pagination.total"
          layout="prev, pager, next"
          @current-change="onPageChange"
        />
      </div>
    </div>
  </div>
</template>
