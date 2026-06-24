<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ResourceEditor from '@/components/editors/ResourceEditor.vue'

const route = useRoute()
const router = useRouter()

const resourceId = computed(() => {
  const id = route.params.id
  return id && id !== 'new' ? Number(id) : undefined
})

const isNew = computed(() => !resourceId.value)

function onSaved(id: number) {
  if (isNew.value && id) {
    router.replace(`/resources/${id}`)
  }
}
</script>

<template>
  <div>
    <h2 class="admin-page-title">{{ isNew ? '新建资源' : '编辑资源' }}</h2>
    <ResourceEditor :resource-id="resourceId" @saved="onSaved" />
  </div>
</template>
