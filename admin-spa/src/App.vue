<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminLayout from '@/components/layout/AdminLayout.vue'

const route = useRoute()
const isAuthLayout = computed(() => !!route.meta.auth)
</script>

<template>
  <AdminLayout v-if="isAuthLayout" />
  <router-view v-else />
</template>
