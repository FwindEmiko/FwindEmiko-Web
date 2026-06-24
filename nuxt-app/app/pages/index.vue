<template>
  <div>
    <!-- Sakura particles decoration -->
    <div class="sakura-container" aria-hidden="true">
      <span
        v-for="i in 8"
        :key="i"
        class="sakura-particle"
        :style="sakuraStyle(i)"
      >❀</span>
    </div>

    <!-- Hero -->
    <section class="relative w-full min-h-[85vh] flex items-center justify-center overflow-hidden">
      <!-- Starfield gradient background: 紫→蓝→青 -->
      <div class="absolute inset-0 bg-gradient-to-br from-purple-600/20 via-blue-500/15 to-cyan-400/20" />

      <!-- SVG starfield pattern (P2: clearer than radial-gradient) -->
      <svg class="absolute inset-0 w-full h-full opacity-60" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <pattern id="starfield" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">
            <circle cx="20" cy="30" r="1" fill="#a78bfa" opacity="0.8" />
            <circle cx="60" cy="10" r="0.8" fill="#60a5fa" opacity="0.6" />
            <circle cx="90" cy="50" r="1.2" fill="#22d3ee" opacity="0.7" />
            <circle cx="30" cy="80" r="0.6" fill="#f0abfc" opacity="0.5" />
            <circle cx="100" cy="100" r="1" fill="#a78bfa" opacity="0.7" />
            <circle cx="70" cy="70" r="0.5" fill="#ffffff" opacity="0.4" />
          </pattern>
          <pattern id="pixel-grid" x="0" y="0" width="24" height="24" patternUnits="userSpaceOnUse">
            <rect x="0" y="0" width="2" height="2" fill="#38bdf8" opacity="0.15" />
            <rect x="12" y="12" width="2" height="2" fill="#a78bfa" opacity="0.1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#starfield)" />
        <rect width="100%" height="100%" fill="url(#pixel-grid)" />
      </svg>

      <!-- Twinkling stars -->
      <div class="absolute inset-0">
        <span
          v-for="star in stars"
          :key="star.id"
          class="star-particle absolute rounded-full bg-white"
          :style="star.style"
        />
      </div>

      <div class="relative z-10 max-w-4xl mx-auto px-4 text-center">
        <!-- Pixel art fox avatar -->
        <div class="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-500/30 via-[var(--accent)]/30 to-cyan-400/30 flex items-center justify-center mb-6 border border-white/10 mx-auto">
          <!-- Pixel-style fox SVG -->
          <svg class="text-[var(--accent)]" xmlns="http://www.w3.org/2000/svg" width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 10 L6 4 L9 8 L15 8 L18 4 L21 10 L21 16 L18 20 L15 18 L9 18 L6 20 L3 16 Z" />
            <circle cx="9" cy="13" r="1" fill="currentColor" />
            <circle cx="15" cy="13" r="1" fill="currentColor" />
            <path d="M11 16 L12 17 L13 16" />
          </svg>
        </div>
        <h1 class="text-4xl sm:text-6xl font-bold text-[var(--text-primary)] mb-4 font-anime">
          狐风轩汐の小屋
        </h1>
        <!-- Pixel decorations around subtitle -->
        <p class="text-lg sm:text-xl text-[var(--text-secondary)] mb-8 flex items-center justify-center gap-2">
          <span class="text-pink-400 text-sm" aria-hidden="true">◆</span>
          <span>代码 · 游戏 · 创作</span>
          <span class="text-cyan-400 text-sm" aria-hidden="true">◆</span>
        </p>
        <div class="flex flex-wrap items-center justify-center gap-4">
          <NuxtLink to="/blog" class="px-7 py-3 rounded-full bg-[var(--accent)] text-white font-medium hover:bg-[var(--accent-hover)] transition-colors shadow-lg shadow-[var(--accent)]/20">
            浏览博客
          </NuxtLink>
          <NuxtLink to="/resources" class="px-7 py-3 rounded-full glass-panel text-[var(--text-primary)] font-medium hover:bg-glass-hover transition-colors">
            发现资源
          </NuxtLink>
        </div>
        <!-- Terminal style decoration -->
        <div class="mt-8 terminal-text text-xs opacity-70">
          <span class="text-terminal">$</span> echo "Welcome to FwindEmiko's world"
        </div>
      </div>
    </section>

    <!-- 渐变过渡遮罩：Hero → 精选文章平滑过渡 -->
    <div class="relative h-16 -mt-16 bg-gradient-to-b from-transparent to-[var(--bg-primary)] pointer-events-none z-10" aria-hidden="true" />

    <!-- Featured posts -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-[var(--text-primary)] flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[var(--accent)]"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/><line x1="10" x2="8" y1="9" y2="9"/></svg>
          精选文章
        </h2>
        <NuxtLink to="/blog" class="text-sm text-[var(--text-muted)] hover:text-[var(--accent)] flex items-center gap-1">
          全部
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </NuxtLink>
      </div>
      <div v-if="pending" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="h-72 rounded-glass bg-glass animate-pulse" />
      </div>
      <div v-else-if="posts?.items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PostCard v-for="post in posts.items.slice(0, 6)" :key="post.id" :post="post" />
      </div>
      <div v-else class="text-center py-12 text-[var(--text-muted)]">
        暂无文章
      </div>
    </section>

    <!-- Hot resources -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-bold text-[var(--text-primary)] flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-[var(--accent)]"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
          热门资源
        </h2>
        <NuxtLink to="/resources" class="text-sm text-[var(--text-muted)] hover:text-[var(--accent)] flex items-center gap-1">
          全部
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>
        </NuxtLink>
      </div>
      <div v-if="resourcesPending" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 3" :key="i" class="h-64 rounded-glass bg-glass animate-pulse" />
      </div>
      <div v-else-if="resources?.items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <ResourceCard v-for="resource in resources.items.slice(0, 6)" :key="resource.id" :resource="resource" />
      </div>
      <div v-else class="text-center py-12 text-[var(--text-muted)]">
        暂无资源
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { blogApi, resourceApi } from '@windemiko/shared'

useSeoMeta({
  title: '首页',
  description: '狐风轩汐の小屋 - 代码、游戏、创作，分享技术与生活的碎片。',
})

const { data: posts, pending } = await useAsyncData('home-posts', () => blogApi.listPosts({ page: 1, size: 6 }))
const { data: resources, pending: resourcesPending } = await useAsyncData('home-resources', () => resourceApi.listResources({ page: 1, size: 6, sort: 'downloads' }))

// Twinkling stars for Hero background
const stars = Array.from({ length: 24 }, (_, i) => ({
  id: i,
  style: {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    width: `${1 + Math.random() * 2}px`,
    height: `${1 + Math.random() * 2}px`,
    animationDuration: `${2 + Math.random() * 4}s`,
    animationDelay: `${Math.random() * 3}s`,
    opacity: 0.4 + Math.random() * 0.5,
  },
}))

// Sakura particle styles
function sakuraStyle(i: number) {
  const left = (i * 12 + Math.random() * 8) % 100
  const duration = 12 + Math.random() * 10
  const delay = Math.random() * 15
  const size = 10 + Math.random() * 8
  return {
    left: `${left}%`,
    fontSize: `${size}px`,
    color: ['#ff70a6', '#f0abfc', '#a78bfa'][i % 3],
    animationDuration: `${duration}s`,
    animationDelay: `${delay}s`,
  }
}
</script>

<style scoped>
.sakura-container {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 5;
  overflow: hidden;
}
</style>
