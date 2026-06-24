<template>
  <Teleport to="body">
    <Transition name="glass-modal">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="close">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" />
        <div
          class="relative w-full max-w-lg rounded-glass bg-glass border border-glass-border shadow-glass backdrop-blur-glass p-6"
          :class="panelClass"
        >
          <button
            v-if="showClose"
            class="absolute right-4 top-4 p-1 rounded-full text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-glass-hover transition-colors"
            @click="close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: boolean
  showClose?: boolean
  panelClass?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

function close() {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.glass-modal-enter-active,
.glass-modal-leave-active {
  transition: opacity 0.25s ease;
}
.glass-modal-enter-from,
.glass-modal-leave-to {
  opacity: 0;
}
</style>
