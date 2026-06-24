<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-[var(--text-primary)] mb-2">博客文章</h1>
      <p class="text-[var(--text-muted)]">探索技术、游戏与创作的记录</p>
    </div>

    <!-- Filters -->
    <GlassCard class="mb-8">
      <div class="flex flex-col lg:flex-row gap-4">
        <div class="flex-1 relative">
          <input
            v-model="q"
            type="text"
            placeholder="搜索文章标题或内容..."
            class="w-full bg-glass border border-glass-border rounded-lg pl-9 pr-4 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            @keydown.enter="applyFilters"
          >
          <svg class="absolute left-3 top-2.5 text-[var(--text-muted)]" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
        <select
          v-model="selectedCategory"
          class="bg-glass border border-glass-border rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]/50"
          @change="applyFilters"
        >
          <option value="">全部分类</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.slug">
            {{ cat.name }} ({{ cat.post_count }})
          </option>
        </select>
      </div>

      <!-- Tags -->
      <div v-if="tags?.length" class="mt-4 flex flex-wrap gap-2">
        <button
          v-for="tag in tags || []"
          :key="tag.id"
          class="px-2.5 py-1 rounded-full text-xs transition-colors"
          :class="selectedTag === tag.slug ? 'bg-[var(--accent)] text-white' : 'bg-glass-hover text-[var(--text-secondary)] border border-glass-border hover:text-[var(--accent)]'"
          @click="toggleTag(tag.slug)"
        >
          {{ tag.name }}
        </button>
      </div>
    </GlassCard>

    <!-- Posts grid -->
    <div v-if="pending" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="h-72 rounded-glass bg-glass animate-pulse" />
    </div>
    <div v-else-if="posts?.items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts.items" :key="post.id" :post="post" />
    </div>
    <div v-else class="text-center py-20 text-[var(--text-muted)]">
      没有找到符合条件的文章
    </div>

    <!-- Pagination -->
    <div v-if="posts && posts.pages > 1" class="mt-10 flex items-center justify-center gap-2">
      <button
        :disabled="page <= 1"
        class="px-3 py-1.5 rounded-lg text-sm glass-panel disabled:opacity-40"
        @click="page--; applyFilters()"
      >
        上一页
      </button>
      <span class="text-sm text-[var(--text-muted)] px-3">
        {{ page }} / {{ posts.pages }}
      </span>
      <button
        :disabled="page >= posts.pages"
        class="px-3 py-1.5 rounded-lg text-sm glass-panel disabled:opacity-40"
        @click="page++; applyFilters()"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { blogApi } from '@windemiko/shared'

useSeoMeta({
  title: '博客',
  description: '浏览狐风轩汐の小屋的全部博客文章，涵盖技术、游戏与创作。',
})

const route = useRoute()
const router = useRouter()

const page = ref(Number(route.query.page) || 1)
const q = ref(String(route.query.q || ''))
const selectedCategory = ref(String(route.query.category || ''))
const selectedTag = ref(String(route.query.tag || ''))

const { data: categories } = await useAsyncData('blog-categories', () => blogApi.listCategories())
const { data: tags } = await useAsyncData('blog-tags', () => blogApi.listTags())

const { data: posts, pending, refresh } = await useAsyncData(
  () => `blog-posts-${page.value}-${selectedCategory.value}-${selectedTag.value}-${q.value}`,
  () => blogApi.listPosts({
    page: page.value,
    size: 12,
    category: selectedCategory.value || undefined,
    tag: selectedTag.value || undefined,
    q: q.value || undefined,
  }),
)

function toggleTag(slug: string) {
  selectedTag.value = selectedTag.value === slug ? '' : slug
  page.value = 1
  applyFilters()
}

function applyFilters() {
  router.push({
    query: {
      ...(page.value > 1 ? { page: page.value } : {}),
      ...(q.value ? { q: q.value } : {}),
      ...(selectedCategory.value ? { category: selectedCategory.value } : {}),
      ...(selectedTag.value ? { tag: selectedTag.value } : {}),
    },
  })
  refresh()
}
</script>
