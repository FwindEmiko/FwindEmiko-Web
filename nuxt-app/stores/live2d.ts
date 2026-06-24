import { defineStore } from 'pinia'

export const useLive2DStore = defineStore('live2d', () => {
  const isSpeaking = ref(false)
  const bubbleText = ref('')
  const bubbleVisible = ref(false)

  let idleTimer: ReturnType<typeof setTimeout> | null = null
  let bubbleTimer: ReturnType<typeof setTimeout> | null = null

  function speak(chunk: string) {
    bubbleText.value += chunk
    isSpeaking.value = true
    bubbleVisible.value = true
    if (idleTimer) {
      clearTimeout(idleTimer)
      idleTimer = null
    }
    if (bubbleTimer) {
      clearTimeout(bubbleTimer)
      bubbleTimer = null
    }
  }

  function idle() {
    isSpeaking.value = false
    idleTimer = setTimeout(() => {
      bubbleVisible.value = false
      bubbleText.value = ''
    }, 2000)
  }

  function showBubble(text: string, duration = 3000) {
    bubbleText.value = text
    bubbleVisible.value = true
    isSpeaking.value = false
    if (idleTimer) {
      clearTimeout(idleTimer)
      idleTimer = null
    }
    if (bubbleTimer) {
      clearTimeout(bubbleTimer)
      bubbleTimer = null
    }
    bubbleTimer = setTimeout(() => {
      bubbleVisible.value = false
      bubbleText.value = ''
    }, duration)
  }

  return {
    isSpeaking,
    bubbleText,
    bubbleVisible,
    speak,
    idle,
    showBubble,
  }
})
