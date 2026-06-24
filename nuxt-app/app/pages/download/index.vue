<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-[var(--text-primary)] mb-2">下载站</h1>
      <p class="text-[var(--text-muted)]">
        {{ auth.isLoggedIn ? '登录用户可访问更多文件夹' : '未登录仅显示公开文件夹，登录后解锁更多内容' }}
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 min-h-[500px]">
      <!-- Folder tree -->
      <div class="lg:col-span-1">
        <GlassCard class="h-full max-h-[70vh] overflow-y-auto">
          <h2 class="text-sm font-bold text-[var(--text-primary)] mb-3 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[var(--accent)]"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
            文件夹
          </h2>
          <div v-if="treePending" class="space-y-2">
            <div v-for="i in 5" :key="i" class="h-8 rounded-lg bg-glass animate-pulse" />
          </div>
          <FolderTree v-else :folders="folders || []" :active-id="currentFolderId" @select="selectFolder" />
        </GlassCard>
      </div>

      <!-- File list -->
      <div class="lg:col-span-3">
        <GlassCard class="h-full">
          <!-- Mobile back button -->
          <button
            v-if="isMobile && currentFolderId"
            class="lg:hidden mb-4 flex items-center gap-1 text-sm text-[var(--text-muted)] hover:text-[var(--accent)]"
            @click="currentFolderId = null"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
            返回文件夹列表
          </button>

          <div v-if="!currentFolderId" class="flex flex-col items-center justify-center h-64 text-[var(--text-muted)]">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="mb-3 opacity-50"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
            <p>请从左侧选择一个文件夹</p>
          </div>

          <div v-else-if="filesPending" class="space-y-3">
            <div v-for="i in 4" :key="i" class="h-16 rounded-lg bg-glass animate-pulse" />
          </div>

          <div v-else-if="folderData">
            <!-- Breadcrumb -->
            <nav class="flex items-center gap-2 text-sm mb-4 flex-wrap">
              <button class="text-[var(--text-muted)] hover:text-[var(--accent)]" @click="currentFolderId = null">下载站</button>
              <span v-for="(crumb, idx) in folderData.breadcrumbs" :key="crumb.id" class="flex items-center gap-2">
                <span class="text-[var(--text-muted)]">/</span>
                <button
                  class="text-[var(--text-muted)] hover:text-[var(--accent)]"
                  :class="{ 'text-[var(--text-primary)] font-medium': idx === folderData.breadcrumbs.length - 1 }"
                  @click="selectFolder(crumb.id)"
                >
                  {{ crumb.name }}
                </button>
              </span>
            </nav>

            <!-- README -->
            <div v-if="folderData.folder.description" class="mb-6 p-4 rounded-xl bg-glass border border-glass-border">
              <h3 class="text-xs font-bold text-[var(--text-muted)] uppercase mb-2">README</h3>
              <article class="prose-custom prose-sm" v-html="render(folderData.folder.description)" />
            </div>

            <!-- Subfolders -->
            <div v-if="folderData.subfolders.length" class="mb-6">
              <h3 class="text-sm font-bold text-[var(--text-primary)] mb-3">子文件夹</h3>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button
                  v-for="sub in folderData.subfolders"
                  :key="sub.id"
                  class="flex items-center gap-3 p-3 rounded-xl bg-glass border border-glass-border hover:border-[var(--accent)]/50 transition-colors text-left"
                  @click="selectFolder(sub.id)"
                >
                  <svg class="text-[var(--accent)]" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
                  <span class="text-sm font-medium text-[var(--text-primary)]">{{ sub.name }}</span>
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
                  class="flex items-center justify-between p-3 rounded-xl bg-glass border border-glass-border hover:bg-glass-hover transition-colors"
                >
                  <div class="flex items-center gap-3 min-w-0">
                    <FileIcon :filename="file.filename" :mime="file.mime_type" />
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-[var(--text-primary)] truncate">{{ file.display_name || file.filename }}</p>
                      <p class="text-xs text-[var(--text-muted)]">{{ formatSize(file.file_size) }} · {{ file.download_count }} 次下载</p>
                    </div>
                  </div>
                  <a
                    :href="downloadApi.downloadFile(file.id)"
                    target="_blank"
                    class="flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/30 hover:bg-[var(--accent)]/30 transition-colors flex items-center gap-1"
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
    </div>
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

const currentFolderId = ref<number | null>(null)
const isMobile = ref(false)

const { data: folders, pending: treePending } = await useAsyncData('download-folders', () => downloadApi.listFolders())
const { data: folderData, pending: filesPending } = await useAsyncData(
  () => `folder-files-${currentFolderId.value}`,
  () => currentFolderId.value ? downloadApi.listFolderFiles(currentFolderId.value) : null,
  { watch: [currentFolderId] },
)

function selectFolder(id: number) {
  currentFolderId.value = id
}

function checkMobile() {
  isMobile.value = typeof window !== 'undefined' && window.innerWidth < 1024
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>
