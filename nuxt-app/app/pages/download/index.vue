<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-[var(--text-primary)] mb-2">下载站</h1>
      <p class="text-[var(--text-muted)]">
        {{ auth.isLoggedIn ? '登录用户可访问更多文件夹' : '未登录仅显示公开文件夹，登录后解锁更多内容' }}
      </p>
    </div>

    <GlassCard class="min-h-[500px] p-4 sm:p-6">
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-1.5 text-sm mb-5 flex-wrap px-4 pb-4 border-b border-glass-border">
        <button
          class="flex items-center gap-1 text-[var(--text-muted)] hover:text-[var(--accent)] transition-colors"
          @click="goToFolder(null)"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
          下载站
        </button>
        <template v-for="(crumb, idx) in breadcrumbs" :key="crumb.id">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[var(--text-muted)]"><path d="m9 18 6-6-6-6"/></svg>
          <button
            class="transition-colors"
            :class="idx === breadcrumbs.length - 1 ? 'text-[var(--text-primary)] font-medium' : 'text-[var(--text-muted)] hover:text-[var(--accent)]'"
            @click="goToFolder(crumb.id)"
          >
            {{ crumb.name }}
          </button>
        </template>
      </nav>

      <!-- Root: folder grid -->
      <div v-if="!currentFolderId" class="space-y-4">
        <div v-if="treePending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <div v-for="i in 6" :key="i" class="h-16 rounded-xl bg-glass animate-pulse" />
        </div>
        <div v-else-if="rootFolders.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <button
            v-for="folder in rootFolders"
            :key="folder.id"
            class="flex items-center gap-3 p-4 rounded-xl bg-glass border border-glass-border hover:border-[var(--accent)]/50 hover:bg-glass-hover transition-all group"
            @click="goToFolder(folder.id)"
          >
            <svg class="text-[var(--accent)] flex-shrink-0" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
            <div class="min-w-0 text-left">
              <p class="text-sm font-medium text-[var(--text-primary)] truncate group-hover:text-[var(--accent)] transition-colors">{{ folder.name }}</p>
              <p v-if="folder.description" class="text-xs text-[var(--text-muted)] truncate">{{ folder.description }}</p>
            </div>
          </button>
        </div>
        <div v-else class="flex flex-col items-center justify-center h-64 text-[var(--text-muted)]">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="mb-3 opacity-50"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
          <p>暂无可访问的文件夹</p>
        </div>
      </div>

      <!-- Folder content -->
      <div v-else-if="filesPending" class="space-y-2">
        <div v-for="i in 5" :key="i" class="h-14 rounded-xl bg-glass animate-pulse" />
      </div>

      <div v-else-if="folderData" class="space-y-5">
        <!-- README -->
        <div v-if="folderData.folder.description" class="p-4 rounded-xl bg-glass border border-glass-border">
          <h3 class="text-xs font-bold text-[var(--text-muted)] uppercase mb-2">README</h3>
          <article class="prose-custom prose-sm" v-html="render(folderData.folder.description)" />
        </div>

        <!-- Subfolders -->
        <div v-if="folderData.subfolders.length">
          <h3 class="text-sm font-bold text-[var(--text-primary)] mb-3">子文件夹</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            <button
              v-for="sub in folderData.subfolders"
              :key="sub.id"
              class="flex items-center gap-3 p-4 rounded-xl bg-glass border border-glass-border hover:border-[var(--accent)]/50 hover:bg-glass-hover transition-all group"
              @click="goToFolder(sub.id)"
            >
              <svg class="text-[var(--accent)] flex-shrink-0" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
              <span class="text-sm font-medium text-[var(--text-primary)] truncate group-hover:text-[var(--accent)] transition-colors">{{ sub.name }}</span>
            </button>
          </div>
        </div>

        <!-- Files -->
        <div>
          <h3 class="text-sm font-bold text-[var(--text-primary)] mb-3">文件列表</h3>
          <div v-if="folderData.files.length" class="space-y-2">
            <div
              v-for="file in folderData.files"
              :key="file.id"
              class="flex items-center justify-between gap-3 px-4 py-3 rounded-xl bg-glass border border-glass-border hover:bg-glass-hover transition-colors"
            >
              <div class="flex items-center gap-3 min-w-0 flex-1">
                <FileIcon :filename="file.filename" :mime="file.mime_type" />
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-[var(--text-primary)] truncate">{{ file.display_name || file.filename }}</p>
                  <p class="text-xs text-[var(--text-muted)] flex items-center gap-2 flex-wrap">
                    <span class="inline-flex items-center gap-1">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                      {{ formatSize(file.file_size) }}
                    </span>
                    <span class="text-[var(--text-muted)]/50">·</span>
                    <span>{{ file.download_count }} 次下载</span>
                  </p>
                </div>
              </div>
              <a
                :href="downloadApi.downloadFile(file.id)"
                target="_blank"
                class="flex-shrink-0 inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-medium bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                下载
              </a>
            </div>
          </div>
          <div v-else class="text-center py-10 text-[var(--text-muted)] text-sm">
            该文件夹暂无文件
          </div>
        </div>
      </div>
    </GlassCard>
  </div>
</template>

<script setup lang="ts">
import { downloadApi } from '@windemiko/shared'
import type { FolderTreeNode } from '@windemiko/shared'
import { useAuthStore } from '~~/stores/auth'

useSeoMeta({
  title: '下载站',
  description: '狐风轩汐の小屋下载站，提供公开与会员文件下载。',
})

const auth = useAuthStore()
const { render } = useMarkdown()
const route = useRoute()
const router = useRouter()

// 从 URL query 恢复文件夹 ID，刷新不丢状态
const currentFolderId = computed<number | null>(() => {
  const raw = route.query.folder
  if (!raw) return null
  const id = Number(raw)
  return Number.isFinite(id) && id > 0 ? id : null
})

const { data: folders, pending: treePending } = await useAsyncData('download-folders', () => downloadApi.listFolders())

const rootFolders = computed(() => folders.value || [])

const { data: folderData, pending: filesPending } = await useAsyncData(
  () => `folder-files-${currentFolderId.value}`,
  () => currentFolderId.value ? downloadApi.listFolderFiles(currentFolderId.value) : null,
  { watch: [currentFolderId] },
)

const breadcrumbs = computed(() => folderData.value?.breadcrumbs || [])

function goToFolder(id: number | null) {
  router.push({ query: id ? { folder: id } : {} })
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>
