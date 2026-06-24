<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { FileText, Box, FolderOpen, Download } from 'lucide-vue-next'
import { api } from '@/api/client'
import type { AdminStats } from '@windemiko/shared'

const router = useRouter()
const stats = ref<AdminStats | null>(null)
const loading = ref(false)

const cards = [
  { key: 'posts', label: '文章', icon: FileText, color: 'text-blue-600', bg: 'bg-blue-50' },
  { key: 'resources', label: '资源', icon: Box, color: 'text-violet-600', bg: 'bg-violet-50' },
  { key: 'files', label: '文件', icon: FolderOpen, color: 'text-amber-600', bg: 'bg-amber-50' },
  { key: 'downloads', label: '下载量', icon: Download, color: 'text-emerald-600', bg: 'bg-emerald-50' },
] as const

async function loadStats() {
  loading.value = true
  try {
    const res = await api.get<AdminStats>('/admin/stats')
    stats.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载统计数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div>
    <h2 class="admin-page-title">仪表盘</h2>

    <div v-loading="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div
        v-for="card in cards"
        :key="card.key"
        class="admin-card p-4 flex items-center gap-4"
      >
        <div class="w-12 h-12 rounded-xl flex items-center justify-center" :class="card.bg">
          <component :is="card.icon" class="w-6 h-6" :class="card.color" />
        </div>
        <div>
          <div class="text-2xl font-bold">{{ stats ? (stats[card.key] as number) : 0 }}</div>
          <div class="text-sm text-[var(--text-secondary)]">{{ card.label }}</div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="admin-card lg:col-span-2 p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold">最近文章</h3>
          <el-button type="primary" size="small" @click="router.push('/posts/new')">+ 新文章</el-button>
        </div>
        <el-table :data="stats?.recent_posts || []" size="small" :empty-text="'暂无文章'">
          <el-table-column prop="title" label="标题" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="90">
            <template #default="{ row }">
              <el-tag size="small" :type="row.status === 'published' ? 'success' : 'info'">
                {{ row.status === 'published' ? '已发布' : row.status === 'draft' ? '草稿' : '归档' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="author" label="作者" width="120" />
        </el-table>
      </div>

      <div class="admin-card p-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-semibold">最近上传</h3>
          <el-button size="small" @click="router.push('/files')">文件管理</el-button>
        </div>
        <el-table :data="stats?.recent_uploads || []" size="small" :empty-text="'暂无上传'">
          <el-table-column prop="filename" label="文件名" show-overflow-tooltip />
          <el-table-column prop="folder_id" label="目录 ID" width="90" />
        </el-table>

        <div class="mt-4 flex gap-2">
          <el-button type="primary" class="flex-1" @click="router.push('/posts/new')">+ 新文章</el-button>
          <el-button class="flex-1" @click="router.push('/resources/new')">+ 新资源</el-button>
        </div>
      </div>
    </div>
  </div>
</template>
