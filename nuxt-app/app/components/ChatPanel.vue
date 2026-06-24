<template>
  <!-- 顶部弹幕 Toast -->
  <Transition name="toast-slide">
    <div
      v-if="toast.show"
      class="fixed top-4 left-1/2 -translate-x-1/2 z-[100] glass-panel px-5 py-3 rounded-xl shadow-glass flex items-center gap-3 cursor-pointer select-none max-w-[90vw]"
      @click="toast.link && navigateTo(toast.link)"
    >
      <div class="w-8 h-8 rounded-full bg-[var(--accent)]/15 flex items-center justify-center text-[var(--accent)] flex-shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
      </div>
      <div>
        <p class="text-sm font-medium text-[var(--text-primary)]">{{ toast.message }}</p>
        <p v-if="toast.link" class="text-xs text-[var(--accent)]">点击前往登录 →</p>
      </div>
    </div>
  </Transition>

  <div class="fixed bottom-24 right-4 z-50 flex flex-col items-end">
    <!-- Toggle button: 始终显示，未登录时提示 -->
    <button
      v-if="!modelValue"
      class="w-12 h-12 rounded-full glass-panel flex items-center justify-center text-[var(--accent)] shadow-glass hover:scale-105 transition-transform"
      title="AI 对话"
      @click="handleToggle"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
    </button>

    <!-- Panel: 仅登录用户显示 -->
    <Transition name="chat-panel">
      <div
        v-if="modelValue && auth.isLoggedIn"
        class="chat-panel-box w-[90vw] max-w-[420px] glass-panel flex flex-col overflow-hidden"
      >
        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-glass-border">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-full bg-[var(--accent)]/20 flex items-center justify-center text-[var(--accent)]">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
            </div>
            <div>
              <h3 class="text-sm font-medium text-[var(--text-primary)]">AI 助手</h3>
              <p v-if="quota" class="text-[10px] text-[var(--text-muted)]">
                今日剩余 {{ quota.remaining === -1 ? '无限' : quota.remaining }} 条
              </p>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <button class="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-glass-hover" title="新会话" @click="createNewSession">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
            </button>
            <button class="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-glass-hover" @click="modelValue = false">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="M12 19V5"/></svg>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div ref="messagesRef" class="flex-1 overflow-y-auto p-4 space-y-4">
          <div v-if="messages.length === 0" class="text-center py-10">
            <div class="w-12 h-12 rounded-full bg-[var(--accent)]/10 flex items-center justify-center text-[var(--accent)] mx-auto mb-3">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <p class="text-sm text-[var(--text-muted)]">你好，我是你的 AI 助手。<br>有什么可以帮你的吗？</p>
          </div>

          <div
            v-for="msg in messages"
            :key="msg.id"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[85%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed"
              :class="msg.role === 'user' ? 'bg-[var(--accent)]/20 text-[var(--text-primary)] rounded-br-md' : 'bg-glass-hover text-[var(--text-secondary)] rounded-bl-md border border-glass-border'"
            >
              {{ msg.content }}
            </div>
          </div>

          <!-- Streaming message -->
          <div v-if="streamingContent" class="flex justify-start">
            <div class="max-w-[85%] px-3.5 py-2.5 rounded-2xl rounded-bl-md text-sm leading-relaxed bg-glass-hover text-[var(--text-secondary)] border border-glass-border">
              {{ streamingContent }}<span class="inline-block w-1.5 h-4 ml-0.5 bg-[var(--accent)] animate-pulse align-middle" />
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="p-3 border-t border-glass-border">
          <form class="flex items-end gap-2" @submit.prevent="sendMessage">
            <textarea
              v-model="input"
              rows="1"
              placeholder="输入消息..."
              class="flex-1 max-h-24 bg-glass border border-glass-border rounded-xl px-3 py-2 text-sm text-[var(--text-primary)] placeholder-[var(--text-muted)] resize-none focus:outline-none focus:border-[var(--accent)]/50"
              @keydown.enter.prevent="sendMessage"
            />
            <button
              type="submit"
              :disabled="!input.trim() || streaming"
              class="p-2.5 rounded-xl bg-[var(--accent)] text-white disabled:opacity-40 disabled:pointer-events-none hover:bg-[var(--accent-hover)] transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 2-7 20-4-9-9-4 20-7z"/><path d="M22 2 11 13"/></svg>
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessageOut, ChatSessionOut } from '@windemiko/shared'
import { chatApi } from '@windemiko/shared'
import { useAuthStore } from '~~/stores/auth'
import { useLive2DStore } from '~~/stores/live2d'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const modelValue = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const auth = useAuthStore()
const live2d = useLive2DStore()
const messages = ref<ChatMessageOut[]>([])
const currentSession = ref<ChatSessionOut | null>(null)
const input = ref('')
const streaming = ref(false)
const streamingContent = ref('')
const messagesRef = ref<HTMLElement>()
const quota = ref<{ remaining: number } | null>(null)

// 顶部弹幕 toast
const toast = ref({ show: false, message: '', link: '' })

function showToast(message: string, link = '') {
  toast.value = { show: true, message, link }
  setTimeout(() => { toast.value.show = false }, 4000)
}

// 未登录点击 💬 按钮 → 顶部弹幕提醒
function handleToggle() {
  if (!auth.isLoggedIn) {
    showToast('请先登录后使用 AI 对话', '/login')
    return
  }
  modelValue.value = true
}

async function loadQuota() {
  const useMock = import.meta.env.DEV && true
  if (useMock) {
    quota.value = { remaining: -1 }
    return
  }
  try {
    quota.value = await chatApi.getQuota()
  } catch {
    quota.value = null
  }
}

async function createNewSession() {
  const useMock = import.meta.env.DEV && true
  if (useMock) {
    currentSession.value = {
      id: Date.now(),
      title: '新对话',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as ChatSessionOut
    messages.value = []
    streamingContent.value = ''
    return
  }
  try {
    const session = await chatApi.createSession({ title: '新对话' })
    currentSession.value = session
    messages.value = []
    streamingContent.value = ''
  } catch (err: any) {
    ElMessage.error(err?.message || '创建会话失败')
  }
}

async function loadMessages(sessionId: number) {
  try {
    messages.value = await chatApi.listMessages(sessionId)
    scrollToBottom()
  } catch (err: any) {
    ElMessage.error(err?.message || '加载消息失败')
  }
}

function scrollToBottom() {
  nextTick(() => {
    messagesRef.value?.scrollTo({ top: messagesRef.value.scrollHeight, behavior: 'smooth' })
  })
}

async function sendMessage() {
  const content = input.value.trim()
  if (!content || streaming.value || !auth.isLoggedIn) return

  if (!currentSession.value) {
    await createNewSession()
    if (!currentSession.value) return
  }

  const sessionId = currentSession.value.id
  input.value = ''
  streaming.value = true
  streamingContent.value = ''

  // Optimistically add user message
  messages.value.push({
    id: Date.now(),
    session_id: sessionId,
    role: 'user',
    content,
    created_at: new Date().toISOString(),
  })
  scrollToBottom()

  // SSE fallback: if backend not available, mock response
  const useMock = import.meta.env.DEV && true
  if (useMock) {
    live2d.speak('')
    const reply = `收到你的消息："${content}"\n\n（当前为 mock 回复，实际接入后端 SSE 后将返回 AI 生成内容。）`
    const chunks = reply.split('')
    let i = 0
    const interval = setInterval(() => {
      if (i >= chunks.length) {
        clearInterval(interval)
        messages.value.push({
          id: Date.now() + 1,
          session_id: sessionId,
          role: 'assistant',
          content: reply,
          created_at: new Date().toISOString(),
        })
        streamingContent.value = ''
        streaming.value = false
        live2d.idle()
        loadQuota()
        return
      }
      const chunk = chunks.slice(i, i + 3).join('')
      streamingContent.value += chunk
      live2d.speak(chunk)
      i += 3
      scrollToBottom()
    }, 60)
    return
  }

  live2d.speak('')
  chatApi.sendMessageStream(
    sessionId,
    { content },
    (event) => {
      if (event.type === 'chunk') {
        streamingContent.value += event.content
        live2d.speak(event.content)
        scrollToBottom()
      } else if (event.type === 'done') {
        messages.value.push({
          id: event.message_id || Date.now(),
          session_id: sessionId,
          role: 'assistant',
          content: streamingContent.value,
          created_at: new Date().toISOString(),
        })
        streamingContent.value = ''
        streaming.value = false
        live2d.idle()
        loadQuota()
      } else if (event.type === 'error') {
        ElMessage.error(event.message)
        streaming.value = false
        streamingContent.value = ''
        live2d.idle()
      }
    },
  )
}

onMounted(() => {
  if (auth.isLoggedIn) {
    loadQuota()
    createNewSession()
  }
})
</script>

<style scoped>
.chat-panel-box {
  height: 380px;
  max-height: 80vh;
}

.toast-slide-enter-active { transition: all 0.3s ease-out; }
.toast-slide-leave-active { transition: all 0.25s ease-in; }
.toast-slide-enter-from { opacity: 0; transform: translate(-50%, -20px); }
.toast-slide-leave-to   { opacity: 0; transform: translate(-50%, -12px); }

@media (min-width: 768px) {
  .chat-panel-box {
    height: 520px;
  }
}

.chat-panel-enter-active,
.chat-panel-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.chat-panel-enter-from,
.chat-panel-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.96);
}
</style>
