<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from 'lucide-vue-next'
import { api, formatDateTime } from '@/api/client'
import type { CategoryOut, PostListItem } from '@windemiko/shared'

const router = useRouter()

const list = ref<PostListItem[]>([])
const categories = ref<CategoryOut[]>([])
const loading = ref(false)
const selected = ref<PostListItem[]>([])
const pagination = reactive({ page: 1, size: 10, total: 0, pages: 1 })
const filters = reactive({
  status: '',
  category_id: undefined as number | undefined,
  q: '',
})

async function loadCategories() {
  const res = await api.get<CategoryOut[]>('/categories')
  categories.value = res.data
}

async function loadPosts() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: pagination.page,
      size: pagination.size,
    }
    if (filters.status) params.status = filters.status
    if (filters.category_id != null) params.category_id = filters.category_id
    if (filters.q) params.q = filters.q
    const res = await api.get<{ items: PostListItem[]; total: number; pages: number }>(
      '/admin/posts',
      { params }
    )
    list.value = res.data.items
    pagination.total = res.data.total
    pagination.pages = res.data.pages
  } catch (error: any) {
    ElMessage.error(error.message || '加载文章失败')
  } finally {
    loading.value = false
  }
}

function onSearch() {
  pagination.page = 1
  loadPosts()
}

function onPageChange(page: number) {
  pagination.page = page
  loadPosts()
}

async function deletePost(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该文章吗？', '提示', { type: 'warning' })
    await api.delete(`/posts/${id}`)
    ElMessage.success('已删除')
    loadPosts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

async function batchDelete() {
  if (!selected.value.length) return
  try {
    await ElMessageBox.confirm(`确定删除 ${selected.value.length} 篇文章吗？`, '提示', { type: 'warning' })
    await Promise.all(selected.value.map((p) => api.delete(`/posts/${p.id}`)))
    ElMessage.success('已批量删除')
    selected.value = []
    loadPosts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量删除失败')
    }
  }
}

onMounted(() => {
  loadCategories()
  loadPosts()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="admin-page-title">文章管理</h2>
      <el-button type="primary" @click="router.push('/posts/new')">
        <Plus class="w-4 h-4 mr-1" /> 新建文章
      </el-button>
    </div>

    <div class="admin-card p-4 mb-4">
      <div class="flex flex-wrap items-center gap-3">
        <el-input v-model="filters.q" placeholder="搜索标题/内容" clearable class="w-48" @keyup.enter="onSearch">
          <template #prefix>
            <Search class="w-4 h-4 text-gray-400" />
          </template>
        </el-input>
        <el-select v-model="filters.status" placeholder="状态" clearable class="w-32">
          <el-option label="草稿" value="draft" />
          <el-option label="已发布" value="published" />
          <el-option label="已归档" value="archived" />
        </el-select>
        <el-select v-model="filters.category_id" placeholder="分类" clearable class="w-40">
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
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
        @selection-change="(rows: PostListItem[]) => (selected = rows)"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="title" label="标题" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.status === 'published' ? 'success' : row.status === 'draft' ? 'info' : 'warning'">
              {{ row.status === 'published' ? '已发布' : row.status === 'draft' ? '草稿' : '归档' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分类" width="120">
          <template #default="{ row }">
            {{ row.category?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="作者" width="120">
          <template #default="{ row }">
            {{ row.author.display_name || row.author.username }}
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="router.push(`/posts/${row.id}`)">编辑</el-button>
            <el-button type="danger" size="small" text @click="deletePost(row.id)">删除</el-button>
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
