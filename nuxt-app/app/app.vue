<template>
  <div>
    <NuxtRouteAnnouncer />
    <NuxtLoadingIndicator color="var(--accent)" />
    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~~/stores/auth'

const auth = useAuthStore()
const { applyTheme } = useTheme()

onMounted(() => {
  applyTheme()
  auth.init()
})
</script>
