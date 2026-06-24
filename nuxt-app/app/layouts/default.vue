<template>
  <div class="min-h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-primary)] transition-colors duration-300">
    <AppHeader />
    <main class="flex-1 pt-14">
      <slot />
    </main>
    <AppFooter />
    <Live2DWidget :visible="chatOpen" :open-chat="openChat" />
    <ChatPanel v-model="chatOpen" />
  </div>
</template>

<script setup lang="ts">
const chatOpen = ref(false)

function openChat() {
  chatOpen.value = true
}
</script>
