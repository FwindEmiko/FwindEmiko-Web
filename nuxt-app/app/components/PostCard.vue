<template>
  <NuxtLink :to="`/blog/${post.slug}`" class="group block h-full">
    <GlassCard class="h-full flex flex-col overflow-hidden hover:-translate-y-1 post-card-glow">
      <div class="relative aspect-[16/10] overflow-hidden rounded-lg mb-4 -mx-2 -mt-2">
        <img
          v-if="post.cover_url"
          :src="resolveUploadUrl(post.cover_url)"
          :alt="post.title"
          class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        >
        <div v-else class="w-full h-full bg-gradient-to-br from-[var(--accent)]/20 to-purple-500/20 flex items-center justify-center">
          <svg class="text-[var(--accent)]/60" xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>
        </div>
        <div v-if="post.is_pinned" class="absolute top-2 left-2 px-2 py-0.5 rounded-full text-xs font-medium bg-[var(--accent)]/80 text-white backdrop-blur-sm">
          置顶
        </div>
      </div>
      <h3 class="font-bold text-lg text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors line-clamp-2 mb-2">
        {{ post.title }}
      </h3>
      <p class="text-sm text-[var(--text-muted)] line-clamp-2 mb-3 flex-1">
        {{ post.summary || post.content_md?.slice(0, 120) || '暂无摘要' }}
      </p>
      <div class="flex items-center justify-between text-xs text-[var(--text-muted)] mt-auto">
        <div class="flex items-center gap-2">
          <span v-if="post.category" class="px-2 py-0.5 rounded-full bg-[var(--accent)]/10 text-[var(--accent)]">
            {{ post.category.name }}
          </span>
          <span>{{ formatDate(post.published_at || post.created_at) }}</span>
        </div>
        <span class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
          {{ post.view_count }}
        </span>
      </div>
    </GlassCard>
  </NuxtLink>
</template>

<script setup lang="ts">
import { GlassCard } from '@windemiko/ui'
import { resolveUploadUrl } from '@windemiko/shared'
import type { PostListItem } from '@windemiko/shared'

defineProps<{
  post: PostListItem
}>()

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>
