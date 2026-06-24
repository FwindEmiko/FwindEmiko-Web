<template>
  <ul class="space-y-1">
    <li v-for="folder in folders" :key="folder.id">
      <button
        class="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-sm transition-colors text-left"
        :class="activeId === folder.id ? 'bg-[var(--accent)]/10 text-[var(--accent)]' : 'text-[var(--text-secondary)] hover:bg-glass-hover hover:text-[var(--text-primary)]'"
        :style="{ paddingLeft: `${depth * 12 + 8}px` }"
        @click="$emit('select', folder.id)"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>
        <span class="truncate">{{ folder.name }}</span>
      </button>
      <FolderTree
        v-if="folder.children?.length"
        :folders="folder.children"
        :active-id="activeId"
        :depth="depth + 1"
        @select="$emit('select', $event)"
      />
    </li>
  </ul>
</template>

<script setup lang="ts">
import type { FolderTreeNode } from '@windemiko/shared'

defineProps<{
  folders: FolderTreeNode[]
  activeId: number | null
  depth?: number
}>()

defineEmits<{
  select: [id: number]
}>()
</script>
