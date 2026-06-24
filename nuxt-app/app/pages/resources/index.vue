<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <div class="mb-8">
      <h1 class="text-2xl font-bold text-[var(--text-primary)] mb-2">资源中心</h1>
      <p class="text-[var(--text-muted)]">插件、Mod、数据包与工具</p>
    </div>

    <!-- Filters -->
    <GlassCard class="mb-8">
      <div class="flex flex-col lg:flex-row gap-4">
        <div class="flex-1 relative">
          <input
            v-model="q"
            type="text"
            placeholder="搜索资源..."
            class="w-full bg-glass border border-glass-border rounded-lg pl-9 pr-4 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:border-[var(--accent)]/50"
            @keydown.enter="applyFilters"
          >
          <svg class="absolute left-3 top-2.5 text-[var(--text-muted)]" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        </div>
        <select
          v-model="selectedType"
          class="bg-glass border border-glass-border rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]/50"
          @change="applyFilters"
        >
          <option value="">全部类型</option>
          <option value="plugin">插件</option>
          <option value="mod">Mod</option>
          <option value="datapack">数据包</option>
          <option value="tool">工具</option>
        </select>
        <select
          v-model="selectedVersion"
          class="bg-glass border border-glass-border rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]/50"
          @change="applyFilters"
        >
          <option value="">全部 MC 版本</option>
          <option v-for="v in gameVersions" :key="v" :value="v">{{ v }}</option>
        </select>
        <select
          v-model="sort"
          class="bg-glass border border-glass-border rounded-lg px-3 py-2 text-sm text-[var(--text-primary)] focus:outline-none focus:border-[var(--accent)]/50"
          @change="applyFilters"
        >
          <option value="newest">最新发布</option>
          <option value="downloads">最多下载</option>
        </select>
      </div>

      <!-- Loader filter -->
      <div class="mt-4 flex flex-wrap gap-2">
        <span class="text-xs text-[var(--text-muted)] py-1">加载器：</span>
        <button
          v-for="loader in loaders"
          :key="loader"
          class="px-2.5 py-1 rounded-full text-xs transition-colors"
          :class="selectedLoader === loader ? 'bg-[var(--accent)] text-white' : 'bg-glass-hover text-[var(--text-secondary)] border border-glass-border hover:text-[var(--accent)]'"
          @click="toggleLoader(loader)"
        >
          {{ loader }}
        </button>
      </div>
    </GlassCard>

    <!-- Resources grid -->
    <div v-if="pending" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="h-64 rounded-glass bg-glass animate-pulse" />
    </div>
    <div v-else-if="resources?.items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <ResourceCard v-for="resource in resources.items" :key="resource.id" :resource="resource" />
    </div>
    <div v-else class="text-center py-20 text-[var(--text-muted)]">
      没有找到符合条件的资源
    </div>

    <!-- Pagination -->
    <div v-if="resources && resources.pages > 1" class="mt-10 flex items-center justify-center gap-2">
      <button
        :disabled="page <= 1"
        class="px-3 py-1.5 rounded-lg text-sm glass-panel disabled:opacity-40"
        @click="page--; applyFilters()"
      >
        上一页
      </button>
      <span class="text-sm text-[var(--text-muted)] px-3">
        {{ page }} / {{ resources.pages }}
      </span>
      <button
        :disabled="page >= resources.pages"
        class="px-3 py-1.5 rounded-lg text-sm glass-panel disabled:opacity-40"
        @click="page++; applyFilters()"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { resourceApi } from '@windemiko/shared'

useSeoMeta({
  title: '资源中心',
  description: '浏览 Minecraft 插件、Mod、数据包与工具资源。',
})

const route = useRoute()
const router = useRouter()

const page = ref(Number(route.query.page) || 1)
const q = ref(String(route.query.q || ''))
const selectedType = ref(String(route.query.type || ''))
const selectedVersion = ref(String(route.query.version || ''))
const selectedLoader = ref(String(route.query.loader || ''))
const sort = ref<'newest' | 'downloads'>((route.query.sort as 'newest' | 'downloads') || 'newest')

const gameVersions = ['1.20.4', '1.20.1', '1.19.4', '1.18.2', '1.16.5']
const loaders = ['Fabric', 'Forge', 'Paper', 'Quilt', 'NeoForge']

const { data: resources, pending, refresh } = await useAsyncData(
  () => `resources-${page.value}-${selectedType.value}-${selectedVersion.value}-${selectedLoader.value}-${sort.value}-${q.value}`,
  () => resourceApi.listResources({
    page: page.value,
    size: 12,
    type: selectedType.value || undefined,
    version: selectedVersion.value || undefined,
    loader: selectedLoader.value || undefined,
    q: q.value || undefined,
    sort: sort.value,
  }),
)

function toggleLoader(loader: string) {
  selectedLoader.value = selectedLoader.value === loader ? '' : loader
  page.value = 1
  applyFilters()
}

function applyFilters() {
  router.push({
    query: {
      ...(page.value > 1 ? { page: page.value } : {}),
      ...(q.value ? { q: q.value } : {}),
      ...(selectedType.value ? { type: selectedType.value } : {}),
      ...(selectedVersion.value ? { version: selectedVersion.value } : {}),
      ...(selectedLoader.value ? { loader: selectedLoader.value } : {}),
      ...(sort.value !== 'newest' ? { sort: sort.value } : {}),
    },
  })
  refresh()
}
</script>
