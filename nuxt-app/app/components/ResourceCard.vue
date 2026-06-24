<template>
  <NuxtLink :to="`/resources/${resource.slug}`" class="group block h-full">
    <GlassCard class="h-full flex flex-col overflow-hidden hover:-translate-y-1 post-card-glow">
      <div class="flex items-start gap-4 mb-4">
        <div class="w-14 h-14 rounded-xl overflow-hidden flex-shrink-0 bg-gradient-to-br from-[var(--accent)]/20 to-purple-500/20 flex items-center justify-center">
          <img
            v-if="resource.icon_url"
            :src="resolveUploadUrl(resource.icon_url)"
            :alt="resource.title"
            class="w-full h-full object-cover"
          >
          <svg v-else class="text-[var(--accent)]/60" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-bold text-base text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors line-clamp-2 break-words">
            {{ resource.title }}
          </h3>
          <div class="flex items-center gap-1.5 mt-1 flex-wrap">
            <span class="px-1.5 py-0.5 rounded text-[10px] font-medium uppercase bg-[var(--accent)]/10 text-[var(--accent)]">
              {{ typeLabel(resource.type) }}
            </span>
            <span v-if="resource.latest_version" class="text-xs text-[var(--text-muted)]">
              {{ resource.latest_version.version_string }}
            </span>
          </div>
        </div>
      </div>
      <p class="text-sm text-[var(--text-muted)] line-clamp-2 mb-3 flex-1">
        {{ resource.description }}
      </p>
      <div class="flex flex-wrap gap-1.5 mb-3">
        <span v-for="v in resource.game_versions.slice(0, 3)" :key="v" class="px-1.5 py-0.5 rounded-md text-[10px] bg-glass-hover text-[var(--text-secondary)] border border-glass-border">
          {{ v }}
        </span>
        <span v-if="resource.game_versions.length > 3" class="px-1.5 py-0.5 rounded-md text-[10px] text-[var(--text-muted)]">
          +{{ resource.game_versions.length - 3 }}
        </span>
      </div>
      <div class="flex items-center justify-between text-xs text-[var(--text-muted)] mt-auto pt-3 border-t border-glass-border">
        <span class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          {{ resource.download_count }}
        </span>
        <span>{{ formatDate(resource.created_at) }}</span>
      </div>
    </GlassCard>
  </NuxtLink>
</template>

<script setup lang="ts">
import { GlassCard } from '@windemiko/ui'
import { resolveUploadUrl } from '@windemiko/shared'
import type { ResourceListItem } from '@windemiko/shared'

defineProps<{
  resource: ResourceListItem
}>()

function typeLabel(type: ResourceListItem['type']) {
  const map: Record<string, string> = {
    plugin: '插件',
    mod: 'Mod',
    datapack: '数据包',
    tool: '工具',
  }
  return map[type] || type
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>
