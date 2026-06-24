<template>
  <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" :class="iconClass">
    <svg v-if="isImage" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
    <svg v-else-if="ext === 'jar'" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h14a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v4"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="m5 12-3 3 3 3"/><path d="m9 18 3-3-3-3"/></svg>
    <svg v-else-if="['zip', 'rar', '7z', 'tar', 'gz'].includes(ext)" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h14a2 2 0 0 0 2-2V7l-5-5H6a2 2 0 0 0-2 2v4"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M2 15h10"/><path d="M5 12v6"/><path d="M8 12v6"/></svg>
    <svg v-else-if="['pdf', 'doc', 'docx', 'txt'].includes(ext)" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>
    <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  filename: string
  mime?: string | null
}>()

const ext = computed(() => {
  const parts = props.filename.split('.')
  return parts.length > 1 ? parts.pop()!.toLowerCase() : ''
})

const isImage = computed(() => {
  if (props.mime?.startsWith('image/')) return true
  return ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp', 'svg'].includes(ext.value)
})

const iconClass = computed(() => {
  if (isImage.value) return 'bg-purple-500/10 text-purple-400'
  if (ext.value === 'jar') return 'bg-orange-500/10 text-orange-400'
  if (['zip', 'rar', '7z', 'tar', 'gz'].includes(ext.value)) return 'bg-yellow-500/10 text-yellow-400'
  if (['pdf', 'doc', 'docx', 'txt'].includes(ext.value)) return 'bg-blue-500/10 text-blue-400'
  return 'bg-[var(--accent)]/10 text-[var(--accent)]'
})
</script>
