<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api, getAccessToken } from '@/api/client'
import type { CategoryOut, TagOut } from '@windemiko/shared'

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

const props = defineProps<{
  postId?: number
  initial?: Partial<PostForm>
}>()

const emit = defineEmits<{
  (e: 'save', form: PostForm): void
}>()

const editorId = `vditor-${props.postId || 'new'}-${Date.now()}`
const draftKey = computed(() => `post-draft-${props.postId || 'new'}`)

const form = reactive<PostForm>({
  title: '',
  content: '',
  summary: '',
  cover_url: '',
  category_id: null,
  tag_ids: [],
  status: 'draft',
  is_pinned: false,
})

const categories = ref<CategoryOut[]>([])
const tags = ref<TagOut[]>([])
const loading = ref(false)
let vditorInstance: any = null
let autoSaveTimer: ReturnType<typeof setInterval> | null = null

async function loadMeta() {
  const [catRes, tagRes] = await Promise.all([
    api.get<CategoryOut[]>('/categories'),
    api.get<TagOut[]>('/tags'),
  ])
  categories.value = catRes.data
  tags.value = tagRes.data
}

function applyInitial() {
  if (props.initial) {
    form.title = props.initial.title ?? ''
    form.content = props.initial.content ?? ''
    form.summary = props.initial.summary ?? ''
    form.cover_url = props.initial.cover_url ?? ''
    form.category_id = props.initial.category_id ?? null
    form.tag_ids = props.initial.tag_ids ? [...props.initial.tag_ids] : []
    form.status = props.initial.status ?? 'draft'
    form.is_pinned = props.initial.is_pinned ?? false
  }
  const lastCat = localStorage.getItem('post-last-category')
  if (lastCat && form.category_id == null) {
    form.category_id = Number(lastCat)
  }
  const lastTags = localStorage.getItem('post-last-tags')
  if (lastTags && form.tag_ids.length === 0) {
    try {
      form.tag_ids = JSON.parse(lastTags)
    } catch {
      // ignore
    }
  }
}

function restoreDraft() {
  const raw = localStorage.getItem(draftKey.value)
  if (!raw) return false
  try {
    const draft = JSON.parse(raw)
    form.title = draft.title ?? form.title
    form.summary = draft.summary ?? form.summary
    form.cover_url = draft.cover_url ?? form.cover_url
    form.category_id = draft.category_id ?? form.category_id
    form.tag_ids = draft.tag_ids ?? form.tag_ids
    form.status = draft.status ?? form.status
    form.is_pinned = draft.is_pinned ?? form.is_pinned
    form.content = draft.content ?? form.content
    return true
  } catch {
    return false
  }
}

function saveDraft() {
  localStorage.setItem(
    draftKey.value,
    JSON.stringify({
      title: form.title,
      content: vditorInstance?.getValue() ?? form.content,
      summary: form.summary,
      cover_url: form.cover_url,
      category_id: form.category_id,
      tag_ids: form.tag_ids,
      status: form.status,
      is_pinned: form.is_pinned,
      savedAt: new Date().toISOString(),
    })
  )
}

function rememberChoices() {
  if (form.category_id != null) {
    localStorage.setItem('post-last-category', String(form.category_id))
  }
  localStorage.setItem('post-last-tags', JSON.stringify(form.tag_ids))
}

async function initVditor() {
  const Vditor = (await import('vditor')).default
  vditorInstance = new Vditor(editorId, {
    mode: 'wysiwyg',
    height: 480,
    placeholder: '开始写作...',
    value: form.content,
    cache: { enable: false },
    toolbar: [
      'headings',
      'bold',
      'italic',
      'strike',
      '|',
      'link',
      'code',
      'inline-code',
      '|',
      'list',
      'ordered-list',
      'check',
      '|',
      'upload',
      'table',
      '|',
      'undo',
      'redo',
      '|',
      'preview',
      'edit-mode',
    ],
    upload: {
      url: '/api/files/upload',
      headers: { Authorization: `Bearer ${getAccessToken() || ''}` },
      format: (files: File[], responseText: string) => {
        try {
          const res = JSON.parse(responseText)
          return JSON.stringify({
            msg: res.message || '',
            code: res.code === 0 ? 0 : res.code,
            data: {
              errFiles: res.data?.errFiles || [],
              succMap: res.data?.succMap || {},
            },
          })
        } catch {
          return responseText
        }
      },
    },
  })
}

function submit(status: 'draft' | 'published') {
  form.status = status
  const content = vditorInstance?.getValue() ?? form.content
  if (!form.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!content.trim()) {
    ElMessage.warning('请输入正文')
    return
  }
  form.content = content
  if (!form.summary.trim()) {
    form.summary = content.slice(0, 200)
  }
  rememberChoices()
  emit('save', { ...form })
}

function onKeydown(e: KeyboardEvent) {
  if (e.ctrlKey && e.key.toLowerCase() === 's') {
    e.preventDefault()
    saveDraft()
    ElMessage.success('草稿已保存到本地')
  }
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    submit('published')
  }
}

onMounted(async () => {
  applyInitial()
  restoreDraft()
  try {
    await loadMeta()
    await nextTick()
    await initVditor()
  } catch (error: any) {
    ElMessage.error(error.message || '编辑器初始化失败')
  }
  autoSaveTimer = setInterval(() => {
    saveDraft()
  }, 30000)
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  if (autoSaveTimer) clearInterval(autoSaveTimer)
  window.removeEventListener('keydown', onKeydown)
  vditorInstance?.destroy()
})

watch(
  () => props.initial,
  () => {
    applyInitial()
    if (vditorInstance && props.initial?.content) {
      vditorInstance.setValue(props.initial.content)
    }
  },
  { deep: true }
)
</script>

<template>
  <div>
    <el-form label-position="top">
      <el-form-item label="标题">
        <el-input v-model="form.title" size="large" placeholder="文章标题" />
      </el-form-item>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable class="w-full">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="标签" class="md:col-span-2">
          <el-select v-model="form.tag_ids" multiple placeholder="选择标签" class="w-full">
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
          </el-select>
        </el-form-item>
      </div>

      <el-form-item label="摘要">
        <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="留空自动取正文前 200 字" />
      </el-form-item>

      <el-form-item label="封面图 URL">
        <div class="flex items-center gap-2 w-full">
          <el-input v-model="form.cover_url" placeholder="https://..." />
          <el-popover v-if="form.cover_url" trigger="hover" placement="left" :width="320">
            <template #reference>
              <el-button size="default" plain>预览</el-button>
            </template>
            <img :src="form.cover_url" alt="封面预览" class="w-full rounded-lg" />
          </el-popover>
        </div>
      </el-form-item>

      <div class="flex items-center gap-4 mb-2">
        <el-checkbox v-model="form.is_pinned">置顶</el-checkbox>
        <span class="text-xs text-[var(--text-secondary)]">快捷键：Ctrl+S 保存草稿，Ctrl+Enter 发布，Esc 关闭弹窗</span>
      </div>

      <el-form-item label="正文">
        <div :id="editorId" class="w-full" />
      </el-form-item>

      <div class="flex gap-3 sticky bottom-0 bg-[var(--bg)] py-3 z-10">
        <el-button @click="submit('draft')">存草稿</el-button>
        <el-button type="primary" @click="submit('published')">发布</el-button>
        <el-button text @click="saveDraft">保存本地草稿</el-button>
      </div>
    </el-form>
  </div>
</template>
