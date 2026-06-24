<template>
  <div v-if="post" class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <!-- Cover -->
    <div v-if="post.cover_url" class="aspect-[21/9] rounded-glass overflow-hidden mb-8">
      <img :src="resolveUploadUrl(post.cover_url)" :alt="post.title" class="w-full h-full object-cover">
    </div>

    <!-- Header -->
    <div class="mb-8">
      <div class="flex flex-wrap items-center gap-2 mb-3">
        <span v-if="post.category" class="px-2.5 py-0.5 rounded-full text-xs bg-[var(--accent)]/10 text-[var(--accent)]">
          {{ post.category.name }}
        </span>
        <span v-if="post.is_pinned" class="px-2.5 py-0.5 rounded-full text-xs bg-[var(--warning)]/20 text-[var(--warning)]">
          置顶
        </span>
      </div>
      <h1 class="text-2xl sm:text-4xl font-bold text-[var(--text-primary)] mb-4">{{ post.title }}</h1>
      <div class="flex flex-wrap items-center gap-4 text-sm text-[var(--text-muted)]">
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-full bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)] text-xs font-bold">
            {{ post.author.display_name?.slice(0, 1) || post.author.username.slice(0, 1) }}
          </div>
          <span>{{ post.author.display_name || post.author.username }}</span>
        </div>
        <span>|</span>
        <span>{{ formatDate(post.published_at || post.created_at) }}</span>
        <span>|</span>
        <span class="flex items-center gap-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
          {{ post.view_count }}
        </span>
      </div>
      <div v-if="post.tags.length" class="flex flex-wrap gap-2 mt-4">
        <NuxtLink
          v-for="tag in post.tags"
          :key="tag.id"
          :to="`/blog?tag=${tag.slug}`"
          class="px-2.5 py-1 rounded-full text-xs bg-glass-hover text-[var(--text-secondary)] border border-glass-border hover:text-[var(--accent)]"
        >
          # {{ tag.name }}
        </NuxtLink>
      </div>
    </div>

    <!-- Content -->
    <GlassCard class="mb-8 no-hover-lift">
      <article class="prose-custom" v-html="post.content_html || render(post.content_md)" />
    </GlassCard>

    <!-- Prev/Next -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-12">
      <NuxtLink v-if="prevPost" :to="`/blog/${prevPost.slug}`" class="glass-panel p-4 hover:bg-glass-hover transition-colors group">
        <span class="text-xs text-[var(--text-muted)] block mb-1">上一篇</span>
        <span class="text-sm font-medium text-[var(--text-primary)] group-hover:text-[var(--accent)] line-clamp-2">{{ prevPost.title }}</span>
      </NuxtLink>
      <div v-else class="glass-panel p-4 opacity-50">
        <span class="text-xs text-[var(--text-muted)] block mb-1">上一篇</span>
        <span class="text-sm text-[var(--text-muted)]">没有了</span>
      </div>
      <NuxtLink v-if="nextPost" :to="`/blog/${nextPost.slug}`" class="glass-panel p-4 hover:bg-glass-hover transition-colors group sm:text-right">
        <span class="text-xs text-[var(--text-muted)] block mb-1">下一篇</span>
        <span class="text-sm font-medium text-[var(--text-primary)] group-hover:text-[var(--accent)] line-clamp-2">{{ nextPost.title }}</span>
      </NuxtLink>
      <div v-else class="glass-panel p-4 opacity-50 sm:text-right">
        <span class="text-xs text-[var(--text-muted)] block mb-1">下一篇</span>
        <span class="text-sm text-[var(--text-muted)]">没有了</span>
      </div>
    </div>
  </div>

  <div v-else-if="loadError" class="max-w-4xl mx-auto px-4 py-20 text-center text-[var(--text-muted)]">
    {{ loadError }}
  </div>

  <div v-else class="max-w-4xl mx-auto px-4 py-20 text-center text-[var(--text-muted)]">
    文章不存在或已被删除
  </div>
</template>

<script setup lang="ts">
import { blogApi, resolveUploadUrl } from '@windemiko/shared'

const route = useRoute()
const slug = route.params.slug as string
const { render } = useMarkdown()

const { data: response, error } = await useAsyncData(`post-${slug}`, () => blogApi.getPost(slug), {
  default: () => null,
})

const post = computed(() => response.value?.post || null)
const prevPost = computed(() => response.value?.prev_post)
const nextPost = computed(() => response.value?.next_post)
const loadError = computed(() => error.value ? '加载文章失败，请稍后重试' : '')

useHead(() => ({
  title: post.value?.title || '文章详情',
  meta: [
    { name: 'description', content: post.value?.summary || '狐风轩汐の小屋博客文章' },
    { property: 'og:title', content: post.value?.title || '文章详情' },
    { property: 'og:description', content: post.value?.summary || '狐风轩汐の小屋博客文章' },
    { property: 'og:image', content: post.value?.cover_url ? resolveUploadUrl(post.value.cover_url) : '' },
    { property: 'og:type', content: 'article' },
    { property: 'article:published_time', content: post.value?.published_at || '' },
  ],
}))

function formatDate(date: string | undefined | null) {
  if (!date) return ''
  return new Date(date).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>
