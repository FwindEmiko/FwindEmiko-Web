<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { api, getAccessToken } from '@/api/client'
import { preloadVditorIcons } from '@/utils/vditor-icons'
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

// ========== 分类/标签自定义创建 ==========
const categoryDialogVisible = ref(false)
const newCategoryName = ref('')
const newCategoryDesc = ref('')

const tagDialogVisible = ref(false)
const newTagName = ref('')

function openCategoryDialog() {
  newCategoryName.value = ''
  newCategoryDesc.value = ''
  categoryDialogVisible.value = true
}

async function createCategory() {
  const name = newCategoryName.value.trim()
  if (!name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    const res = await api.post<CategoryOut>('/categories', {
      name,
      description: newCategoryDesc.value || undefined,
    })
    categories.value.push(res.data)
    form.category_id = res.data.id
    categoryDialogVisible.value = false
    ElMessage.success('分类已创建')
  } catch (error: any) {
    ElMessage.error(error.message || '创建分类失败')
  }
}

function openTagDialog() {
  newTagName.value = ''
  tagDialogVisible.value = true
}

async function createTag() {
  const name = newTagName.value.trim()
  if (!name) {
    ElMessage.warning('请输入标签名称')
    return
  }
  try {
    const res = await api.post<TagOut>('/tags', { name })
    tags.value.push(res.data)
    form.tag_ids.push(res.data.id)
    tagDialogVisible.value = false
    ElMessage.success('标签已创建')
  } catch (error: any) {
    ElMessage.error(error.message || '创建标签失败')
  }
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

// 监听分类/标签选择"新建"选项
watch(() => form.category_id, (val) => {
  if (val === '__new_cat' as any) {
    form.category_id = null
    openCategoryDialog()
  }
})

watch(() => form.tag_ids, (val) => {
  const idx = val.indexOf('__new_tag' as any)
  if (idx > -1) {
    form.tag_ids.splice(idx, 1)
    openTagDialog()
  }
}, { deep: true })

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
  // 预加载 Vditor 图标（避免同步 XHR 加载失败导致工具栏图标不显示）
  const cdnBase = import.meta.env.BASE_URL + 'vditor'
  await preloadVditorIcons(cdnBase)
  vditorInstance = new Vditor(editorId, {
    mode: 'wysiwyg',
    height: 700,
    placeholder: '开始写作...',
    value: form.content,
    cache: { enable: false },
    // 使用国内可访问的 CDN 加载 Vditor 动态资源（mode 脚本/图标/emoji）
    // 自托管 Vditor 资源（cdn 被墙）
    cdn: cdnBase,
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
    <el-form label-position="left" label-width="80px">
      <el-form-item label="标题">
        <el-input v-model="form.title" size="large" placeholder="文章标题" />
      </el-form-item>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <el-form-item label="分类">
          <el-select v-model="form.category_id" placeholder="选择分类" clearable class="w-full">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
            <el-option key="__new_cat" label="➕ 新建分类..." :value="'__new_cat' as any" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签" class="md:col-span-3">
          <el-select v-model="form.tag_ids" multiple placeholder="选择标签" class="w-full">
            <el-option
              v-for="tag in tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            />
            <el-option key="__new_tag" label="➕ 新建标签..." :value="'__new_tag' as any" />
          </el-select>
        </el-form-item>
      </div>

      <el-form-item label="摘要">
        <el-input v-model="form.summary" type="textarea" :rows="2" placeholder="留空自动取正文前 200 字" />
      </el-form-item>

      <!-- 封面图 URL + 缩略图预览直接显示在输入框下方 -->
      <el-form-item label="封面图">
        <div class="w-full">
          <el-input v-model="form.cover_url" placeholder="https://..." />
          <div v-if="form.cover_url" class="mt-2">
            <img :src="form.cover_url" alt="封面预览" class="w-full max-w-sm rounded-lg border border-[var(--border)]" />
          </div>
        </div>
      </el-form-item>

      <div class="flex items-center gap-4 mb-2">
        <el-checkbox v-model="form.is_pinned">置顶</el-checkbox>
        <span class="text-xs text-[var(--text-secondary)]">快捷键：Ctrl+S 保存草稿，Ctrl+Enter 发布，Esc 关闭弹窗</span>
      </div>

      <!-- 正文编辑器：移出 form-item，占满全宽 -->
      <div class="mb-4">
        <div class="text-sm text-[var(--text-secondary)] mb-2">正文</div>
        <div :id="editorId" class="w-full" />
      </div>

      <div class="flex gap-3 sticky bottom-0 backdrop-blur-xl py-3 z-10 px-4 -mx-4 border-t border-[var(--border)]" style="background: var(--panel);">
        <el-button @click="submit('draft')">存草稿</el-button>
        <el-button type="primary" @click="submit('published')">发布</el-button>
        <el-button text @click="saveDraft">保存本地草稿</el-button>
      </div>
    </el-form>

    <!-- 新建分类对话框 -->
    <el-dialog v-model="categoryDialogVisible" title="新建分类" width="400px">
      <el-form label-position="top">
        <el-form-item label="分类名称">
          <el-input v-model="newCategoryName" placeholder="如：技术教程" @keyup.enter="createCategory" />
        </el-form-item>
        <el-form-item label="描述（可选）">
          <el-input v-model="newCategoryDesc" type="textarea" :rows="2" placeholder="分类描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="categoryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createCategory">创建</el-button>
      </template>
    </el-dialog>

    <!-- 新建标签对话框 -->
    <el-dialog v-model="tagDialogVisible" title="新建标签" width="400px">
      <el-form label-position="top">
        <el-form-item label="标签名称">
          <el-input v-model="newTagName" placeholder="如：Vue3" @keyup.enter="createTag" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createTag">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
