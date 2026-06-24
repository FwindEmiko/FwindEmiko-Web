<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox, type UploadRequestOptions } from 'element-plus'
import { Folder, FolderOpen, Plus, Upload, Download, Link2, Trash2, MoreVertical } from 'lucide-vue-next'
import { api, formatBytes, formatDateTime } from '@/api/client'
import type { FileItem, FolderTreeNode, BreadcrumbItem } from '@windemiko/shared'

interface SubFolder {
  id: number
  name: string
  slug: string
}

const loading = ref(false)
const folders = ref<FolderTreeNode[]>([])
const currentFolderId = ref<number | null>(null)
const folderName = ref('')
const breadcrumbs = ref<BreadcrumbItem[]>([])
const subfolders = ref<SubFolder[]>([])
const files = ref<FileItem[]>([])
const selectedFiles = ref<FileItem[]>([])

const contextMenu = reactive({
  show: false,
  x: 0,
  y: 0,
  file: null as FileItem | null,
})

const newFolderDialogVisible = ref(false)
const newFolderForm = reactive({
  name: '',
  slug: '',
  parent_id: null as number | null,
})

const treeProps = {
  children: 'children',
  label: 'name',
}

const folderTree = computed(() => folders.value)
const tableFiles = computed(() => files.value as any[])

async function loadFolders() {
  try {
    const res = await api.get<FolderTreeNode[]>('/downloads/folders')
    folders.value = res.data
  } catch (error: any) {
    ElMessage.error(error.message || '加载文件夹失败')
  }
}

async function loadFolder(folderId: number) {
  loading.value = true
  try {
    const res = await api.get<{
      folder: { id: number; name: string; slug: string }
      breadcrumbs: BreadcrumbItem[]
      subfolders: SubFolder[]
      files: FileItem[]
    }>(`/downloads/folders/${folderId}/files`)
    currentFolderId.value = folderId
    folderName.value = res.data.folder.name
    breadcrumbs.value = res.data.breadcrumbs
    subfolders.value = res.data.subfolders
    files.value = res.data.files
    selectedFiles.value = []
  } catch (error: any) {
    ElMessage.error(error.message || '加载文件失败')
  } finally {
    loading.value = false
  }
}

function onNodeClick(data: FolderTreeNode) {
  loadFolder(data.id)
}

function openNewFolderDialog() {
  newFolderForm.name = ''
  newFolderForm.slug = ''
  newFolderForm.parent_id = currentFolderId.value
  newFolderDialogVisible.value = true
}

async function createFolder() {
  if (!newFolderForm.name.trim()) {
    ElMessage.warning('请输入文件夹名称')
    return
  }
  try {
    await api.post('/downloads/folders', {
      name: newFolderForm.name,
      slug: newFolderForm.slug || undefined,
      parent_id: newFolderForm.parent_id,
    })
    ElMessage.success('文件夹已创建')
    newFolderDialogVisible.value = false
    await loadFolders()
  } catch (error: any) {
    ElMessage.error(error.message || '创建失败')
  }
}

async function handleUpload(options: UploadRequestOptions) {
  if (!currentFolderId.value) {
    ElMessage.warning('请先选择文件夹')
    return options.onError?.(new Error('未选择文件夹') as any)
  }
  const formData = new FormData()
  formData.append('files', options.file)
  try {
    await api.post('/downloads/files', formData, {
      params: { folder_id: currentFolderId.value },
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const percent = progressEvent.total
          ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
          : 0
        options.onProgress?.({ percent } as any)
      },
    })
    options.onSuccess?.(undefined)
    ElMessage.success('上传成功')
    await loadFolder(currentFolderId.value)
  } catch (error: any) {
    options.onError?.(error)
    ElMessage.error(error.message || '上传失败')
  }
}

async function deleteFile(file: FileItem) {
  try {
    await ElMessageBox.confirm(`确定删除文件 ${file.filename} 吗？`, '提示', { type: 'warning' })
    await api.delete(`/downloads/files/${file.id}`)
    ElMessage.success('已删除')
    if (currentFolderId.value) await loadFolder(currentFolderId.value)
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error(error.message || '删除失败')
  }
}

async function downloadFile(file: FileItem) {
  try {
    const res = await api.get(`/downloads/files/${file.id}/download`, {
      responseType: 'blob',
    })
    const blob = new Blob([res.data])
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.display_name || file.filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch (error: any) {
    ElMessage.error(error.message || '下载失败')
  }
}

function copyFileLink(file: FileItem) {
  const url = `${window.location.origin}/api/downloads/files/${file.id}/download`
  navigator.clipboard.writeText(url).then(() => {
    ElMessage.success('链接已复制')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
  contextMenu.show = false
}

function showContextMenu(row: FileItem, _column: any, e: MouseEvent) {
  e.preventDefault()
  contextMenu.file = row
  contextMenu.x = e.clientX
  contextMenu.y = e.clientY
  contextMenu.show = true
}

function hideContextMenu() {
  contextMenu.show = false
}

function batchDelete() {
  if (!selectedFiles.value.length) return
  ElMessageBox.confirm(`确定删除 ${selectedFiles.value.length} 个文件吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await Promise.all(selectedFiles.value.map((f) => api.delete(`/downloads/files/${f.id}`)))
      ElMessage.success('已批量删除')
      selectedFiles.value = []
      if (currentFolderId.value) await loadFolder(currentFolderId.value)
    })
    .catch((error: any) => {
      if (error !== 'cancel') ElMessage.error(error.message || '删除失败')
    })
}

onMounted(() => {
  loadFolders()
  window.addEventListener('click', hideContextMenu)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', hideContextMenu)
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <h2 class="admin-page-title">文件管理</h2>
      <div class="flex gap-2">
        <el-button @click="openNewFolderDialog">
          <Plus class="w-4 h-4 mr-1" /> 新建文件夹
        </el-button>
      </div>
    </div>

    <div class="flex gap-4 flex-col md:flex-row md:h-[calc(100vh-12rem)]">
      <!-- Folder Tree -->
      <aside class="admin-card w-full md:w-56 flex-shrink-0 p-3 overflow-auto md:block hidden">
        <div class="text-sm font-medium text-[var(--text-secondary)] mb-2">文件夹</div>
        <el-tree
          :data="folderTree"
          :props="treeProps"
          :indent="24"
          default-expand-all
          highlight-current
          node-key="id"
          @node-click="onNodeClick"
        >
          <template #default="{ node, data }">
            <span class="flex items-center gap-1.5 text-sm" :style="{ paddingLeft: `${(node.level - 1) * 4}px` }">
              <FolderOpen v-if="node.expanded" class="w-4 h-4 text-[var(--accent)]" />
              <Folder v-else class="w-4 h-4 text-[var(--text-secondary)]" />
              <span :class="node.level === 1 ? 'font-medium text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'">{{ data.name }}</span>
            </span>
          </template>
        </el-tree>
      </aside>

      <!-- Main Area -->
      <div class="flex-1 min-w-0 flex flex-col gap-4">
        <!-- Breadcrumb + Upload Zone -->
        <div class="admin-card p-4">
          <div class="flex flex-wrap items-center gap-2 mb-3">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item
                v-for="item in breadcrumbs"
                :key="item.id"
              >
                <a @click="loadFolder(item.id)">{{ item.name }}</a>
              </el-breadcrumb-item>
            </el-breadcrumb>
            <span v-if="!breadcrumbs.length" class="text-sm text-[var(--text-secondary)]">请选择左侧文件夹</span>
          </div>

          <el-upload
            drag
            multiple
            :http-request="handleUpload"
            :disabled="!currentFolderId"
            :show-file-list="false"
            class="w-full"
          >
            <div class="py-6">
              <Upload class="w-8 h-8 mx-auto text-[var(--text-secondary)] mb-2" />
              <div class="text-[var(--text-secondary)]">拖拽文件到此处上传</div>
              <div class="text-xs text-[var(--text-secondary)] mt-1">或点击选择文件</div>
            </div>
          </el-upload>
        </div>

        <!-- File Table -->
        <div class="admin-card flex-1 p-4 overflow-hidden flex flex-col min-h-[300px]">
          <div class="flex items-center justify-between mb-3">
            <span class="font-medium">{{ folderName || '文件列表' }}</span>
            <el-button v-if="selectedFiles.length" type="danger" size="small" @click="batchDelete">
              批量删除 ({{ selectedFiles.length }})
            </el-button>
          </div>
          <div class="flex-1 overflow-auto">
            <el-table
              v-loading="loading"
              :data="tableFiles"
              height="100%"
              @selection-change="(rows: FileItem[]) => (selectedFiles = rows)"
              @row-contextmenu="showContextMenu"
            >
              <el-table-column type="selection" width="45" />
              <el-table-column prop="filename" label="文件名" min-width="160" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ row.display_name || row.filename }}
                </template>
              </el-table-column>
              <el-table-column label="大小" width="90">
                <template #default="{ row }">
                  {{ formatBytes(row.file_size) }}
                </template>
              </el-table-column>
              <el-table-column prop="mime_type" label="类型" width="130" show-overflow-tooltip />
              <el-table-column prop="download_count" label="下载量" width="75" />
              <el-table-column label="创建时间" width="150" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" size="small" text @click="downloadFile(row as FileItem)">下载</el-button>
                  <el-dropdown trigger="click" @command="(cmd: string) => { if (cmd === 'copy') copyFileLink(row as FileItem); if (cmd === 'delete') deleteFile(row as FileItem); }">
                    <el-button size="small" text>
                      <MoreVertical class="w-4 h-4" />
                    </el-button>
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="copy">
                          <span class="flex items-center gap-2"><Link2 class="w-4 h-4" /> 复制链接</span>
                        </el-dropdown-item>
                        <el-dropdown-item command="delete" divided>
                          <span class="flex items-center gap-2 text-red-500"><Trash2 class="w-4 h-4" /> 删除</span>
                        </el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-if="!loading && !files.length" description="该文件夹暂无文件" />
        </div>
      </div>
    </div>

    <!-- Context Menu -->
    <div
      v-if="contextMenu.show"
      class="fixed z-50 border rounded-lg shadow-lg py-1 min-w-[140px] context-menu-dark"
      :style="{ top: contextMenu.y + 'px', left: contextMenu.x + 'px', background: 'var(--panel-solid)', borderColor: 'var(--border)' }"
    >
      <button
        class="w-full px-4 py-2 text-left text-sm hover:bg-[var(--accent-light)] flex items-center gap-2"
        @click="contextMenu.file && downloadFile(contextMenu.file)"
      >
        <Download class="w-4 h-4" /> 下载
      </button>
      <button
        class="w-full px-4 py-2 text-left text-sm hover:bg-[var(--accent-light)] flex items-center gap-2"
        @click="contextMenu.file && copyFileLink(contextMenu.file)"
      >
        <Link2 class="w-4 h-4" /> 复制链接
      </button>
      <div class="border-t my-1" style="border-color: var(--border);" />
      <button
        class="w-full px-4 py-2 text-left text-sm text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 flex items-center gap-2"
        @click="contextMenu.file && deleteFile(contextMenu.file)"
      >
        <Trash2 class="w-4 h-4" /> 删除
      </button>
    </div>

    <!-- New Folder Dialog -->
    <el-dialog v-model="newFolderDialogVisible" title="新建文件夹" width="400px">
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input v-model="newFolderForm.name" placeholder="文件夹名称" />
        </el-form-item>
        <el-form-item label="Slug（可选）">
          <el-input v-model="newFolderForm.slug" placeholder="留空自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newFolderDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createFolder">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
