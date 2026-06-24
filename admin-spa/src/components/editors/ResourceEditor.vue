<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Trash2, GripVertical, Upload, FileCode, Save, FolderOpen } from 'lucide-vue-next'
import Sortable from 'sortablejs'
import { api, getAccessToken } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import type { ResourceDetail, ResourceVersionOut, ScreenshotOut } from '@windemiko/shared'

type ResourceType = 'plugin' | 'mod' | 'datapack' | 'tool'
type ResourceStatus = 'draft' | 'published'

interface ResourceForm {
  title: string
  description: string
  type: ResourceType
  game_versions: string[]
  loaders: string[]
  icon_url: string
  cover_url: string
  status: ResourceStatus
}

interface PendingScreenshot {
  _uid: string
  file: File
  preview: string
  caption: string
}

interface VersionForm {
  id?: number
  version_string: string
  changelog: string
  file_url: string
  external_url: string
  file_size: number | null
  file_hash: string
  is_prerelease: boolean
}

interface TemplateItem {
  name: string
  content: string
  createdAt: string
}

const props = defineProps<{
  resourceId?: number
}>()

const emit = defineEmits<{
  (e: 'saved', id: number): void
}>()

const auth = useAuthStore()
const editorId = `vditor-resource-${props.resourceId || 'new'}-${Date.now()}`

const form = reactive<ResourceForm>({
  title: '',
  description: '',
  type: 'plugin',
  game_versions: [],
  loaders: [],
  icon_url: '',
  cover_url: '',
  status: 'draft',
})

const activeTab = ref('basic')
const loading = ref(false)
const saving = ref(false)
let vditorInstance: any = null
let autoSaveTimer: ReturnType<typeof setInterval> | null = null
const objectUrls: string[] = []

const screenshots = ref<ScreenshotOut[]>([])
const pendingScreenshots = ref<PendingScreenshot[]>([])
const versions = ref<ResourceVersionOut[]>([])
const pendingVersions = ref<VersionForm[]>([])

const versionDialogVisible = ref(false)
const versionForm = reactive<VersionForm>({
  version_string: '',
  changelog: '',
  file_url: '',
  external_url: '',
  file_size: null,
  file_hash: '',
  is_prerelease: false,
})
const editingVersionIndex = ref<number>(-1)

const templateDialogVisible = ref(false)
const templateName = ref('')
const templates = ref<TemplateItem[]>([])

const gameVersionInput = ref('')
const loaderInput = ref('')

const draftKey = computed(() => `resource-draft-${props.resourceId || 'new'}`)
const templateKey = 'resource-description-templates'
const isNew = computed(() => !props.resourceId)

const typeOptions: { label: string; value: ResourceType }[] = [
  { label: '插件', value: 'plugin' },
  { label: '模组', value: 'mod' },
  { label: '数据包', value: 'datapack' },
  { label: '工具', value: 'tool' },
]

function typeLabel(type: string) {
  return typeOptions.find((t) => t.value === type)?.label || type
}

function applyInitial(data?: Record<string, any>) {
  if (data) {
    form.title = data.title ?? ''
    form.description = data.description ?? ''
    form.type = (data.type as ResourceType) || 'plugin'
    form.game_versions = data.game_versions ? [...data.game_versions] : []
    form.loaders = data.loaders ? [...data.loaders] : []
    form.icon_url = data.icon_url ?? ''
    form.cover_url = data.cover_url ?? ''
    form.status = (data.status as ResourceStatus) || 'draft'
  }
  if (isNew.value) {
    const lastType = localStorage.getItem('resource-last-type') as ResourceType | null
    if (lastType && typeOptions.some((t) => t.value === lastType) && form.type === 'plugin') {
      form.type = lastType
    }
    const lastVersions = localStorage.getItem('resource-last-game-versions')
    if (lastVersions && form.game_versions.length === 0) {
      try { form.game_versions = JSON.parse(lastVersions) } catch {}
    }
    const lastLoaders = localStorage.getItem('resource-last-loaders')
    if (lastLoaders && form.loaders.length === 0) {
      try { form.loaders = JSON.parse(lastLoaders) } catch {}
    }
  }
}

function restoreDraft() {
  const raw = localStorage.getItem(draftKey.value)
  if (!raw) return
  try {
    const draft = JSON.parse(raw)
    form.title = draft.title ?? form.title
    form.description = draft.description ?? form.description
    form.type = draft.type ?? form.type
    form.game_versions = draft.game_versions ?? form.game_versions
    form.loaders = draft.loaders ?? form.loaders
    form.icon_url = draft.icon_url ?? form.icon_url
    form.cover_url = draft.cover_url ?? form.cover_url
    form.status = draft.status ?? form.status
    pendingVersions.value = draft.pendingVersions ?? []
  } catch {}
}

function saveDraft() {
  localStorage.setItem(
    draftKey.value,
    JSON.stringify({
      title: form.title,
      description: vditorInstance?.getValue() ?? form.description,
      type: form.type,
      game_versions: form.game_versions,
      loaders: form.loaders,
      icon_url: form.icon_url,
      cover_url: form.cover_url,
      status: form.status,
      pendingVersions: pendingVersions.value,
      savedAt: new Date().toISOString(),
    })
  )
}

function rememberChoices() {
  localStorage.setItem('resource-last-type', form.type)
  localStorage.setItem('resource-last-game-versions', JSON.stringify(form.game_versions))
  localStorage.setItem('resource-last-loaders', JSON.stringify(form.loaders))
}

async function loadResource() {
  if (!props.resourceId) return
  loading.value = true
  try {
    const res = await api.get<ResourceDetail>(`/admin/resources/${props.resourceId}`)
    const data = res.data
    applyInitial(data)
    screenshots.value = data.screenshots || []
    versions.value = data.versions || []
    await nextTick()
    vditorInstance?.setValue(form.description)
  } catch (error: any) {
    ElMessage.error(error.message || '加载资源失败')
  } finally {
    loading.value = false
  }
}

async function initVditor() {
  const Vditor = (await import('vditor')).default
  vditorInstance = new Vditor(editorId, {
    mode: 'wysiwyg',
    height: 360,
    placeholder: '开始编写资源描述...',
    value: form.description,
    cache: { enable: false },
    // 使用国内可访问的 CDN 加载 Vditor 动态资源（mode 脚本/图标/emoji）
    // 自托管 Vditor 资源（cdn 被墙）
    cdn: import.meta.env.BASE_URL + 'vditor',
    toolbar: [
      'headings', 'bold', 'italic', 'strike', '|',
      'link', 'code', 'inline-code', '|',
      'list', 'ordered-list', 'check', '|',
      'upload', 'table', '|',
      'undo', 'redo', '|',
      'preview', 'edit-mode',
    ],
    upload: {
      url: '/api/files/upload',
      headers: { Authorization: `Bearer ${getAccessToken() || ''}` },
      format: (_files: File[], responseText: string) => {
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

// ========== Tags ==========
function addGameVersion() {
  const v = gameVersionInput.value.trim()
  if (v && !form.game_versions.includes(v)) {
    form.game_versions.push(v)
  }
  gameVersionInput.value = ''
}

function removeGameVersion(idx: number) {
  form.game_versions.splice(idx, 1)
}

function addLoader() {
  const v = loaderInput.value.trim()
  if (v && !form.loaders.includes(v)) {
    form.loaders.push(v)
  }
  loaderInput.value = ''
}

function removeLoader(idx: number) {
  form.loaders.splice(idx, 1)
}

// ========== Screenshots ==========
const screenshotListRef = ref<HTMLElement | null>(null)
let sortableInstance: Sortable | null = null

function initSortable() {
  if (!screenshotListRef.value) return
  sortableInstance?.destroy()
  sortableInstance = new Sortable(screenshotListRef.value, {
    handle: '.sort-handle',
    animation: 150,
    onEnd: async (evt) => {
      if (evt.oldIndex === evt.newIndex) return
      const item = screenshots.value.splice(evt.oldIndex ?? 0, 1)[0]
      screenshots.value.splice(evt.newIndex ?? 0, 0, item)
      if (props.resourceId) {
        try {
          await api.put(`/resources/${props.resourceId}/screenshots/reorder`, {
            screenshot_ids: screenshots.value.map((s) => s.id),
          })
          ElMessage.success('排序已保存')
        } catch (error: any) {
          ElMessage.error(error.message || '排序保存失败')
        }
      }
    },
  })
}

function onScreenshotFilesSelected(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  for (const file of Array.from(input.files)) {
    const url = URL.createObjectURL(file)
    objectUrls.push(url)
    pendingScreenshots.value.push({
      _uid: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      file,
      preview: url,
      caption: '',
    })
  }
  input.value = ''
}

async function uploadPendingScreenshots(resourceId: number) {
  if (!pendingScreenshots.value.length) return
  const data = new FormData()
  pendingScreenshots.value.forEach((s) => data.append('files', s.file))
  const captions = pendingScreenshots.value.map((s) => s.caption || '')
  await api.post(`/resources/${resourceId}/screenshots`, data, {
    params: { captions },
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  pendingScreenshots.value.forEach((s) => {
    const idx = objectUrls.indexOf(s.preview)
    if (idx > -1) {
      URL.revokeObjectURL(s.preview)
      objectUrls.splice(idx, 1)
    }
  })
  pendingScreenshots.value = []
}

async function deleteScreenshot(item: ScreenshotOut) {
  try {
    await ElMessageBox.confirm('确定删除这张截图吗？', '提示', { type: 'warning' })
    if (props.resourceId) {
      await api.delete(`/resources/${props.resourceId}/screenshots/${item.id}`)
    }
    screenshots.value = screenshots.value.filter((s) => s.id !== item.id)
    ElMessage.success('已删除')
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.message || '删除失败')
  }
}

function removePendingScreenshot(uid: string) {
  const idx = pendingScreenshots.value.findIndex((s) => s._uid === uid)
  if (idx > -1) {
    const s = pendingScreenshots.value[idx]
    const urlIdx = objectUrls.indexOf(s.preview)
    if (urlIdx > -1) {
      URL.revokeObjectURL(s.preview)
      objectUrls.splice(urlIdx, 1)
    }
    pendingScreenshots.value.splice(idx, 1)
  }
}

// ========== Versions ==========
function openVersionDialog(existing?: ResourceVersionOut | VersionForm) {
  editingVersionIndex.value = -1
  versionForm.version_string = ''
  versionForm.changelog = ''
  versionForm.file_url = ''
  versionForm.external_url = ''
  versionForm.file_size = null
  versionForm.file_hash = ''
  versionForm.is_prerelease = false
  if (existing && 'id' in existing) {
    editingVersionIndex.value = versions.value.findIndex((v) => v.id === existing.id)
    versionForm.version_string = existing.version_string
    versionForm.changelog = existing.changelog || ''
    versionForm.file_url = existing.file_url || ''
    versionForm.external_url = existing.external_url || ''
    versionForm.file_size = existing.file_size ?? null
    versionForm.file_hash = existing.file_hash || ''
    versionForm.is_prerelease = existing.is_prerelease
  } else if (existing) {
    editingVersionIndex.value = pendingVersions.value.indexOf(existing)
    Object.assign(versionForm, existing)
  }
  versionDialogVisible.value = true
}

async function saveVersion() {
  if (!versionForm.version_string.trim()) {
    ElMessage.warning('请输入版本号')
    return
  }
  if (!versionForm.file_url.trim() && !versionForm.external_url.trim()) {
    ElMessage.warning('文件地址和外部链接至少填写一个')
    return
  }
  const payload = { ...versionForm }
  if (props.resourceId && editingVersionIndex.value === -1) {
    try {
      await api.post(`/resources/${props.resourceId}/versions`, payload)
      ElMessage.success('版本已添加')
      await loadResource()
    } catch (error: any) {
      ElMessage.error(error.message || '添加版本失败')
      return
    }
  } else if (props.resourceId && editingVersionIndex.value > -1) {
    const version = versions.value[editingVersionIndex.value]
    try {
      await api.put(`/resources/${props.resourceId}/versions/${version.id}`, payload)
      ElMessage.success('版本已更新')
      await loadResource()
    } catch (error: any) {
      ElMessage.error(error.message || '更新版本失败')
      return
    }
  } else {
    if (editingVersionIndex.value > -1) {
      pendingVersions.value[editingVersionIndex.value] = { ...payload }
    } else {
      pendingVersions.value.push({ ...payload })
    }
  }
  versionDialogVisible.value = false
}

async function deleteVersion(version: ResourceVersionOut) {
  if (!auth.isAdmin) {
    ElMessage.warning('只有管理员可以删除版本')
    return
  }
  try {
    await ElMessageBox.confirm(`确定删除版本 ${version.version_string} 吗？`, '提示', { type: 'warning' })
    await api.delete(`/resources/${props.resourceId}/versions/${version.id}`)
    versions.value = versions.value.filter((v) => v.id !== version.id)
    ElMessage.success('已删除')
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.message || '删除失败')
  }
}

function removePendingVersion(idx: number) {
  pendingVersions.value.splice(idx, 1)
}

async function createPendingVersions(resourceId: number) {
  for (const v of pendingVersions.value) {
    await api.post(`/resources/${resourceId}/versions`, v)
  }
  pendingVersions.value = []
}

// ========== Templates ==========
function loadTemplates() {
  const raw = localStorage.getItem(templateKey)
  if (!raw) return
  try { templates.value = JSON.parse(raw) } catch {}
}

function saveTemplate() {
  const name = templateName.value.trim()
  if (!name) {
    ElMessage.warning('请输入模板名称')
    return
  }
  const content = vditorInstance?.getValue() ?? form.description
  const list = [...templates.value.filter((t) => t.name !== name), { name, content, createdAt: new Date().toISOString() }]
  localStorage.setItem(templateKey, JSON.stringify(list))
  templates.value = list
  templateDialogVisible.value = false
  templateName.value = ''
  ElMessage.success('模板已保存')
}

function applyTemplate(name: string) {
  const t = templates.value.find((x) => x.name === name)
  if (!t) return
  form.description = t.content
  vditorInstance?.setValue(t.content)
  ElMessage.success(`已加载模板：${t.name}`)
}

function deleteTemplate(name: string) {
  templates.value = templates.value.filter((t) => t.name !== name)
  localStorage.setItem(templateKey, JSON.stringify(templates.value))
}

// ========== Save / Publish ==========
async function submit(status: ResourceStatus) {
  if (!form.title.trim()) {
    ElMessage.warning('请输入标题')
    return
  }
  const description = vditorInstance?.getValue() ?? form.description
  if (!description.trim()) {
    ElMessage.warning('请输入资源描述')
    return
  }
  form.description = description
  form.status = status
  saving.value = true
  try {
    let resourceId = props.resourceId
    const payload = {
      title: form.title,
      description: form.description,
      type: form.type,
      game_versions: form.game_versions,
      loaders: form.loaders,
      icon_url: form.icon_url || undefined,
      cover_url: form.cover_url || undefined,
      status: form.status,
    }
    if (resourceId) {
      await api.put(`/resources/${resourceId}`, payload)
    } else {
      const res = await api.post<ResourceDetail>('/resources', payload)
      resourceId = res.data.id
    }
    if (resourceId) {
      await uploadPendingScreenshots(resourceId)
      await createPendingVersions(resourceId)
    }
    rememberChoices()
    saveDraft()
    localStorage.removeItem(draftKey.value)
    ElMessage.success(status === 'published' ? '资源已发布' : '草稿已保存')
    emit('saved', resourceId || 0)
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
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
  if (e.key === 'Escape') {
    versionDialogVisible.value = false
    templateDialogVisible.value = false
  }
}

onMounted(async () => {
  applyInitial()
  loadTemplates()
  if (props.resourceId) {
    await loadResource()
  }
  restoreDraft()
  await nextTick()
  await initVditor()
  initSortable()
  autoSaveTimer = setInterval(saveDraft, 30000)
  window.addEventListener('keydown', onKeydown)
})

onBeforeUnmount(() => {
  if (autoSaveTimer) clearInterval(autoSaveTimer)
  window.removeEventListener('keydown', onKeydown)
  vditorInstance?.destroy()
  sortableInstance?.destroy()
  objectUrls.forEach((url) => URL.revokeObjectURL(url))
  objectUrls.length = 0
})

watch(() => props.resourceId, (id, oldId) => {
  if (id && id !== oldId) {
    loadResource()
  }
})
</script>

<template>
  <div v-loading="loading" class="resource-editor">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- Tab 1: 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <el-form label-position="top">
          <el-form-item label="标题">
            <el-input v-model="form.title" size="large" placeholder="资源标题" />
          </el-form-item>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <el-form-item label="类型">
              <el-select v-model="form.type" class="w-full">
                <el-option
                  v-for="opt in typeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="状态">
              <el-radio-group v-model="form.status">
                <el-radio-button label="draft">草稿</el-radio-button>
                <el-radio-button label="published">已发布</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </div>

          <el-form-item label="Minecraft 版本">
            <div class="flex flex-wrap gap-2 mb-2">
              <el-tag
                v-for="(v, idx) in form.game_versions"
                :key="v"
                closable
                @close="removeGameVersion(idx)"
              >
                {{ v }}
              </el-tag>
            </div>
            <div class="flex gap-2">
              <el-input v-model="gameVersionInput" placeholder="输入后回车添加，如 1.20.1" @keyup.enter="addGameVersion" />
              <el-button @click="addGameVersion">添加</el-button>
            </div>
          </el-form-item>

          <el-form-item label="加载器">
            <div class="flex flex-wrap gap-2 mb-2">
              <el-tag
                v-for="(v, idx) in form.loaders"
                :key="v"
                closable
                @close="removeLoader(idx)"
              >
                {{ v }}
              </el-tag>
            </div>
            <div class="flex gap-2">
              <el-input v-model="loaderInput" placeholder="如 Paper、Forge、Fabric" @keyup.enter="addLoader" />
              <el-button @click="addLoader">添加</el-button>
            </div>
          </el-form-item>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <el-form-item label="图标 URL">
              <div class="flex items-center gap-2 w-full">
                <el-input v-model="form.icon_url" placeholder="https://..." />
                <el-popover v-if="form.icon_url" trigger="hover" placement="bottom" :width="120">
                  <template #reference>
                    <el-button size="default" plain>预览</el-button>
                  </template>
                  <img :src="form.icon_url" alt="图标预览" class="w-16 h-16 rounded-lg mx-auto object-cover" />
                </el-popover>
              </div>
            </el-form-item>
            <el-form-item label="封面 URL">
              <div class="flex items-center gap-2 w-full">
                <el-input v-model="form.cover_url" placeholder="https://..." />
                <el-popover v-if="form.cover_url" trigger="hover" placement="bottom" :width="320">
                  <template #reference>
                    <el-button size="default" plain>预览</el-button>
                  </template>
                  <img :src="form.cover_url" alt="封面预览" class="w-full rounded-lg" />
                </el-popover>
              </div>
            </el-form-item>
          </div>

          <el-form-item label="描述">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-[var(--text-secondary)]">支持 Markdown，可保存为模板复用</span>
              <div class="flex gap-2">
                <el-select
                  v-if="templates.length"
                  placeholder="加载模板"
                  clearable
                  class="w-40"
                  @change="applyTemplate"
                >
                  <el-option
                    v-for="t in templates"
                    :key="t.name"
                    :label="t.name"
                    :value="t.name"
                  />
                </el-select>
                <el-button text @click="templateDialogVisible = true">
                  <Save class="w-4 h-4 mr-1" /> 保存为模板
                </el-button>
              </div>
            </div>
            <div :id="editorId" class="w-full" />
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- Tab 2: 截图管理 -->
      <el-tab-pane label="截图管理" name="screenshots">
        <div class="mb-4">
          <label
            class="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-[var(--border)] rounded-xl cursor-pointer hover:border-[var(--accent)] hover:bg-[var(--accent-light)] transition-colors"
          >
            <Upload class="w-8 h-8 text-[var(--text-secondary)] mb-2" />
            <span class="text-sm text-[var(--text-secondary)]">点击或拖拽上传截图</span>
            <input type="file" accept="image/*" multiple class="hidden" @change="onScreenshotFilesSelected">
          </label>
        </div>

        <div ref="screenshotListRef" class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div
            v-for="item in screenshots"
            :key="item.id"
            class="group relative border border-[var(--border)] rounded-lg overflow-hidden bg-white"
          >
            <img :src="item.image_url" class="w-full h-32 object-cover" />
            <div class="absolute top-1 left-1 sort-handle cursor-move p-1 rounded bg-black/40 text-white opacity-0 group-hover:opacity-100 transition-opacity">
              <GripVertical class="w-4 h-4" />
            </div>
            <button
              class="absolute top-1 right-1 p-1 rounded bg-red-500 text-white opacity-0 group-hover:opacity-100 transition-opacity"
              @click="deleteScreenshot(item)"
            >
              <Trash2 class="w-4 h-4" />
            </button>
            <div class="p-2">
              <el-input v-model="item.caption" size="small" placeholder="说明" />
            </div>
          </div>

          <div
            v-for="item in pendingScreenshots"
            :key="item._uid"
            class="group relative border border-dashed border-[var(--accent)] rounded-lg overflow-hidden bg-[var(--accent-light)]"
          >
            <img :src="item.preview" class="w-full h-32 object-cover" />
            <span class="absolute top-1 left-1 text-xs bg-[var(--accent)] text-white px-1.5 rounded">待上传</span>
            <button
              class="absolute top-1 right-1 p-1 rounded bg-red-500 text-white opacity-0 group-hover:opacity-100 transition-opacity"
              @click="removePendingScreenshot(item._uid)"
            >
              <Trash2 class="w-4 h-4" />
            </button>
            <div class="p-2">
              <el-input v-model="item.caption" size="small" placeholder="说明" />
            </div>
          </div>
        </div>

        <el-empty v-if="!screenshots.length && !pendingScreenshots.length" description="暂无截图" />
      </el-tab-pane>

      <!-- Tab 3: 版本管理 -->
      <el-tab-pane label="版本管理" name="versions">
        <div class="flex justify-end mb-3">
          <el-button type="primary" @click="openVersionDialog()">
            <Plus class="w-4 h-4 mr-1" /> 添加版本
          </el-button>
        </div>

        <div class="space-y-3">
          <div
            v-for="version in versions"
            :key="version.id"
            class="admin-card p-4 flex items-start justify-between gap-4"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <el-tag size="small" type="primary">{{ version.version_string }}</el-tag>
                <el-tag v-if="version.is_prerelease" size="small" type="warning">预发布</el-tag>
                <span class="text-xs text-[var(--text-secondary)]">下载量 {{ version.downloads }}</span>
              </div>
              <div class="text-sm text-[var(--text-secondary)] line-clamp-2">{{ version.changelog || '无更新日志' }}</div>
              <div class="text-xs text-[var(--text-secondary)] mt-1 truncate">
                <span v-if="version.file_url" class="mr-3">文件：{{ version.file_url }}</span>
                <span v-if="version.external_url">外链：{{ version.external_url }}</span>
              </div>
            </div>
            <div class="flex gap-2">
              <el-button size="small" text @click="openVersionDialog(version)">编辑</el-button>
              <el-button size="small" type="danger" text @click="deleteVersion(version)">删除</el-button>
            </div>
          </div>

          <div
            v-for="(version, idx) in pendingVersions"
            :key="idx"
            class="border border-dashed border-[var(--accent)] bg-[var(--accent-light)] rounded-xl p-4 flex items-start justify-between gap-4"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <el-tag size="small" type="primary">{{ version.version_string }}</el-tag>
                <el-tag v-if="version.is_prerelease" size="small" type="warning">预发布</el-tag>
                <span class="text-xs text-[var(--accent)]">待保存</span>
              </div>
              <div class="text-sm text-[var(--text-secondary)] line-clamp-2">{{ version.changelog || '无更新日志' }}</div>
            </div>
            <div class="flex gap-2">
              <el-button size="small" text @click="openVersionDialog(version)">编辑</el-button>
              <el-button size="small" type="danger" text @click="removePendingVersion(idx)">删除</el-button>
            </div>
          </div>
        </div>

        <el-empty v-if="!versions.length && !pendingVersions.length" description="暂无版本" />
      </el-tab-pane>
    </el-tabs>

    <div class="flex gap-3 sticky bottom-0 bg-[var(--bg)] py-3 z-10 mt-4">
      <el-button :loading="saving" @click="submit('draft')">存草稿</el-button>
      <el-button :loading="saving" type="primary" @click="submit('published')">发布</el-button>
      <el-button text @click="saveDraft">保存本地草稿</el-button>
      <span class="text-xs text-[var(--text-secondary)] self-center ml-auto">快捷键：Ctrl+S 保存草稿，Ctrl+Enter 发布，Esc 关闭弹窗</span>
    </div>

    <!-- Version Dialog -->
    <el-dialog v-model="versionDialogVisible" title="版本信息" width="600px" @close="editingVersionIndex = -1">
      <el-form label-position="top">
        <el-form-item label="版本号">
          <el-input v-model="versionForm.version_string" placeholder="如 1.2.0" />
        </el-form-item>
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="文件地址">
            <el-input v-model="versionForm.file_url" placeholder="https://... 或 /uploads/..." />
          </el-form-item>
          <el-form-item label="外部链接">
            <el-input v-model="versionForm.external_url" placeholder="https://..." />
          </el-form-item>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="文件大小（字节）">
            <el-input-number v-model="versionForm.file_size" :min="0" class="w-full" controls-position="right" />
          </el-form-item>
          <el-form-item label="文件哈希">
            <el-input v-model="versionForm.file_hash" placeholder="SHA256" />
          </el-form-item>
        </div>
        <el-form-item label="更新日志">
          <el-input v-model="versionForm.changelog" type="textarea" :rows="4" placeholder="支持 Markdown" />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="versionForm.is_prerelease">预发布版本</el-checkbox>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="versionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveVersion">确定</el-button>
      </template>
    </el-dialog>

    <!-- Template Dialog -->
    <el-dialog v-model="templateDialogVisible" title="保存描述模板" width="400px">
      <el-form label-position="top">
        <el-form-item label="模板名称">
          <el-input v-model="templateName" placeholder="如 插件介绍模板" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="templateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
