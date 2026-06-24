<template>
  <div v-if="resource" class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <!-- Cover -->
    <div v-if="resource.cover_url" class="aspect-[21/9] rounded-glass overflow-hidden mb-8">
      <img :src="resolveUploadUrl(resource.cover_url)" :alt="resource.title" class="w-full h-full object-cover">
    </div>

    <!-- Header -->
    <div class="flex flex-col md:flex-row gap-6 mb-8">
      <div class="w-20 h-20 md:w-24 md:h-24 rounded-2xl overflow-hidden flex-shrink-0 bg-gradient-to-br from-[var(--accent)]/20 to-purple-500/20 flex items-center justify-center">
        <img v-if="resource.icon_url" :src="resolveUploadUrl(resource.icon_url)" :alt="resource.title" class="w-full h-full object-cover">
        <svg v-else class="text-[var(--accent)]/60" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
      </div>
      <div class="flex-1">
        <div class="flex flex-wrap items-center gap-2 mb-2">
          <span class="px-2.5 py-0.5 rounded-full text-xs font-medium uppercase bg-[var(--accent)]/10 text-[var(--accent)]">{{ typeLabel(resource.type) }}</span>
          <span v-for="v in resource.game_versions" :key="v" class="px-2 py-0.5 rounded-full text-xs bg-glass-hover text-[var(--text-secondary)] border border-glass-border">{{ v }}</span>
          <span v-for="loader in resource.loaders" :key="loader" class="px-2 py-0.5 rounded-full text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20">{{ loader }}</span>
        </div>
        <h1 class="text-2xl sm:text-4xl font-bold text-[var(--text-primary)] mb-2">{{ resource.title }}</h1>
        <div class="flex flex-wrap items-center gap-4 text-sm text-[var(--text-muted)]">
          <span class="flex items-center gap-1">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
            {{ resource.download_count }} 下载
          </span>
          <span>{{ formatDate(resource.created_at) }}</span>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div class="lg:col-span-2 space-y-8">
        <!-- Screenshots -->
        <GlassCard v-if="resource.screenshots.length">
          <h2 class="text-lg font-bold text-[var(--text-primary)] mb-4">截图展示</h2>
          <div class="flex gap-3 overflow-x-auto pb-2 snap-x">
            <button
              v-for="shot in resource.screenshots"
              :key="shot.id"
              class="flex-shrink-0 snap-start rounded-lg overflow-hidden border border-glass-border hover:border-[var(--accent)]/50 transition-colors"
              @click="openLightbox(shot.image_url)"
            >
              <img :src="resolveUploadUrl(shot.thumb_url || shot.image_url)" :alt="shot.caption || ''" class="w-48 h-28 object-cover">
            </button>
          </div>
        </GlassCard>

        <!-- Description -->
        <GlassCard>
          <h2 class="text-lg font-bold text-[var(--text-primary)] mb-4">资源介绍</h2>
          <article class="prose-custom" v-html="render(resource.description)" />
        </GlassCard>
      </div>

      <!-- Versions -->
      <div>
        <GlassCard class="sticky top-24">
          <h2 class="text-lg font-bold text-[var(--text-primary)] mb-4 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[var(--accent)]"><path d="M12 5v14M5 12h14"/></svg>
            版本历史
          </h2>
          <div v-if="resource.versions.length" class="space-y-3">
            <div
              v-for="(version, idx) in resource.versions"
              :key="version.id"
              class="p-3 rounded-xl bg-glass border border-glass-border"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <span class="font-bold text-[var(--text-primary)]">{{ version.version_string }}</span>
                  <span v-if="idx === 0" class="px-1.5 py-0.5 rounded text-[10px] bg-[var(--success)]/20 text-[var(--success)]">最新</span>
                  <span v-if="version.is_prerelease" class="px-1.5 py-0.5 rounded text-[10px] bg-[var(--warning)]/20 text-[var(--warning)]">预发布</span>
                </div>
                <span class="text-xs text-[var(--text-muted)]">{{ formatSize(version.file_size) }}</span>
              </div>
              <p v-if="version.changelog" class="text-xs text-[var(--text-muted)] line-clamp-2 mb-3">{{ version.changelog }}</p>
              <div class="flex flex-wrap gap-2">
                <a
                  v-if="version.file_url"
                  :href="resourceApi.downloadVersion(resource.id, version.id)"
                  target="_blank"
                  class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-[var(--accent)] text-white hover:bg-[var(--accent-hover)] transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
                  本地下载
                </a>
                <a
                  v-if="version.external_url"
                  :href="version.external_url"
                  target="_blank"
                  class="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-glass-hover text-[var(--text-secondary)] border border-glass-border hover:text-[var(--accent)] transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>
                  网盘下载
                </a>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-6 text-[var(--text-muted)] text-sm">
            暂无版本
          </div>
        </GlassCard>
      </div>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <div v-if="lightboxUrl" class="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4" @click.self="lightboxUrl = null">
        <img :src="resolveUploadUrl(lightboxUrl)" alt="screenshot" class="max-w-full max-h-[85vh] rounded-lg shadow-2xl">
      </div>
    </Teleport>
  </div>

  <div v-else-if="loadError" class="max-w-4xl mx-auto px-4 py-20 text-center text-[var(--text-muted)]">
    {{ loadError }}
  </div>

  <div v-else class="max-w-4xl mx-auto px-4 py-20 text-center text-[var(--text-muted)]">
    资源不存在或已被删除
  </div>
</template>

<script setup lang="ts">
import { resourceApi, resolveUploadUrl } from '@windemiko/shared'
import type { ResourceListItem } from '@windemiko/shared'

const route = useRoute()
const slug = route.params.slug as string
const { render } = useMarkdown()

const { data: resource, error } = await useAsyncData(`resource-${slug}`, () => resourceApi.getResource(slug), {
  default: () => null,
})

const loadError = computed(() => error.value ? '加载资源失败，请稍后重试' : '')

useHead(() => ({
  title: resource.value?.title || '资源详情',
  meta: [
    { name: 'description', content: resource.value?.description?.slice(0, 200) || '狐风轩汐の小屋资源详情' },
    { property: 'og:title', content: resource.value?.title || '资源详情' },
    { property: 'og:description', content: resource.value?.description?.slice(0, 200) || '狐风轩汐の小屋资源详情' },
    { property: 'og:image', content: resource.value?.cover_url ? resolveUploadUrl(resource.value.cover_url) : '' },
    { property: 'og:type', content: 'website' },
  ],
}))

const lightboxUrl = ref<string | null>(null)

function typeLabel(type: ResourceListItem['type']) {
  const map: Record<string, string> = { plugin: '插件', mod: 'Mod', datapack: '数据包', tool: '工具' }
  return map[type] || type
}

function openLightbox(url: string) {
  lightboxUrl.value = url
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatSize(bytes?: number | null) {
  if (!bytes) return ''
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>
