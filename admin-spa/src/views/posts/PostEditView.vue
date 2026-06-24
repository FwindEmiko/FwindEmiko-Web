<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '@/api/client'
import PostEditor from '@/components/editors/PostEditor.vue'

interface PostForm {
  title: string
  content: string
  summary: string
  cover_url: string
  category_id: number | null
  tag_ids: number[]
  status: 'draft' | 'published' | 'archived'
  is_pinned: boolean
}

const route = useRoute()
const router = useRouter()
const isNew = route.path.endsWith('/new')
const postId = isNew ? undefined : Number(route.params.id)

const initial = ref<Partial<PostForm>>({})
const loading = ref(false)

async function loadPost() {
  if (isNew || !postId) return
  loading.value = true
  try {
    const res = await api.get<PostForm & { tags: { id: number }[] }>(`/admin/posts/${postId}`)
    const data = res.data
    initial.value = {
      title: data.title,
      content: data.content,
      summary: data.summary || '',
      cover_url: data.cover_url || '',
      category_id: data.category_id,
      tag_ids: data.tags.map((t) => t.id),
      status: data.status,
      is_pinned: data.is_pinned,
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载文章失败')
  } finally {
    loading.value = false
  }
}

async function onSave(form: PostForm) {
  try {
    if (isNew) {
      await api.post('/posts', form)
      ElMessage.success('文章已创建')
    } else {
      await api.put(`/posts/${postId}`, form)
      ElMessage.success('文章已更新')
    }
    router.push('/posts')
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

onMounted(loadPost)
</script>

<template>
  <div v-loading="loading">
    <h2 class="admin-page-title">{{ isNew ? '新建文章' : '编辑文章' }}</h2>
    <div class="admin-card p-3 md:p-4">
      <PostEditor :post-id="postId" :initial="initial" @save="onSave" />
    </div>
  </div>
</template>
