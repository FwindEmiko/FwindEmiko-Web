<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from 'lucide-vue-next'
import { api, formatDateTime } from '@/api/client'
import type { ResourceListItem } from '@windemiko/shared'

const router = useRouter()

const list = ref<ResourceListItem[]>([])
const loading = ref(false)
const selected = ref<ResourceListItem[]>([])
const pagination = reactive({ page: 1, size: 10, total: 0, pages: 1 })
const filters = reactive({
  status: '',
  type: '',
  q: '',
})

const typeMap: Record<string, string> = {
  plugin: '插件',
  mod: '模组',
  datapack: '数据包',
  tool: '工具',
}

async function loadResources() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      size: pagination.size,
    }
    if (filters.status) params.status = filters.status
    if (filters.type) params.type = filters.type
    if (filters.q) params.q = filters.q
    const res = await api.get<{ items: ResourceListItem[]; total: number; pages: number }>(
      '/admin/resources',
      { params }
    )
    list.value = res.data.items
    pagination.total = res.data.total
    pagination.pages = res.data.pages
  } catch (error: any) {
    ElMessage.error(error.message || '加载资源失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  pagination.page = 1
  loadResources()
}

function onPageChange(page: number) {
  pagination.page = page
  loadResources()
}

async function deleteResource(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该资源吗？', '提示', { type: 'warning' })
    await api.delete(`/resources/${id}`)
    ElMessage.success('已删除')
    loadResources()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

// 发布/下架资源
async function togglePublish(row: ResourceListItem) {
  const target = row.status === 'published' ? 'draft' : 'published'
  const action = target === 'published' ? '发布' : '下架'
  try {
    await api.put(`/resources/${row.id}`, { status: target })
    ElMessage.success(`${action}成功`)
    loadResources()
  } catch (error: any) {
    ElMessage.error(error.message || `${action}失败`)
  }
}

async function batchDelete() {
  if (!selected.value.length) return
  try {
    await ElMessageBox.confirm(`确定删除 ${selected.value.length} 个资源吗？`, '提示', { type: 'warning' })
    await Promise.all(selected.value.map((r) => api.delete(`/resources/${r.id}`)))
    ElMessage.success('已批量删除')
    selected.value = []
    loadResources()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量删除失败')
    }
  }
}

onMounted(loadResources)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="admin-page-title">资源管理</h2>
      <el-button type="primary" @click="router.push('/resources/new')">
        <Plus class="w-4 h-4 mr-1" /> 新建资源
      </el-button>
    </div>

    <div class="admin-card p-4 mb-4">
      <div class="flex flex-wrap items-center gap-3">
        <el-input v-model="filters.q" placeholder="搜索标题" clearable class="w-48" @keyup.enter="onSearch">
          <template #prefix>
            <Search class="w-4 h-4 text-gray-400" />
          </template>
        </el-input>
        <el-select v-model="filters.status" placeholder="状态" clearable class="w-32">
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-select v-model="filters.type" placeholder="类型" clearable class="w-32">
          <el-option label="插件" value="plugin" />
          <el-option label="模组" value="mod" />
          <el-option label="数据包" value="datapack" />
          <el-option label="工具" value="tool" />
        </el-select>
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button v-if="selected.length" type="danger" @click="batchDelete">
          批量删除 ({{ selected.length }})
        </el-button>
      </div>
    </div>

    <div class="admin-card p-4">
      <el-table
        v-loading="loading"
        :data="list"
        @selection-change="(rows: ResourceListItem[]) => (selected = rows)"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">
            {{ typeMap[row.type] || row.type }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'published' ? 'success' : row.status === 'draft' ? 'warning' : 'info'">
              {{ row.status === 'published' ? '已发布' : row.status === 'draft' ? '草稿' : '归档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="最新版本" width="140">
          <template #default="{ row }">
            {{ row.latest_version?.version_string || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="download_count" label="下载量" width="100" />
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="router.push(`/resources/${row.id}`)">编辑</el-button>
            <el-button
              :type="row.status === 'published' ? 'warning' : 'success'"
              size="small"
              text
              @click="togglePublish(row as ResourceListItem)"
            >
              {{ row.status === 'published' ? '下架' : '发布' }}
            </el-button>
            <el-button type="danger" size="small" text @click="deleteResource(row.id)">删除</el-button>
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
