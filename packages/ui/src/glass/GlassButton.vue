<template>
  <component
    :is="tag"
    :href="href"
    :to="to"
    class="inline-flex items-center justify-center gap-2 rounded-glass px-4 py-2 text-sm font-medium transition-all duration-200 bg-glass border border-glass-border backdrop-blur-glass shadow-glass hover:bg-glass-hover hover:shadow-card active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none"
    :class="[variantClasses, sizeClasses]"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    tag?: string
    href?: string
    to?: string | object
    variant?: 'default' | 'primary' | 'ghost'
    size?: 'sm' | 'md' | 'lg'
  }>(),
  {
    tag: 'button',
    variant: 'default',
    size: 'md',
  },
)

const variantClasses = {
  default: 'text-[var(--text-primary)]',
  primary: 'bg-[var(--accent)]/20 border-[var(--accent)]/30 text-[var(--accent)] hover:bg-[var(--accent)]/30',
  ghost: 'bg-transparent border-transparent shadow-none hover:bg-glass',
}

const sizeClasses = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
}
</script>
