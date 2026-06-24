<template>
  <ClientOnly>
    <!-- Collapsed dot (mobile only, <768px) -->
    <button
      v-if="isMobileCollapsed"
      class="fixed z-40 live2d-toggle-dot"
      :style="collapsedStyle"
      aria-label="展开 Live2D 角色"
      @click.stop="expandMobile"
    >
      <span class="text-lg">🐱</span>
    </button>

    <div
      v-else
      ref="widgetRef"
      class="fixed z-40 cursor-grab active:cursor-grabbing live2d-widget"
      :class="{ 'pointer-events-none': isDragging }"
      :style="positionStyle"
      @pointerdown="onPointerDown"
      @click="handleTap"
    >
      <canvas ref="canvasRef" class="w-full h-full" />

      <!-- Mobile collapse button -->
      <button
        v-if="isMobile"
        class="live2d-collapse-btn"
        aria-label="收起 Live2D 角色"
        @click.stop="collapseMobile"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
      </button>

      <Transition name="bubble">
        <div
          v-if="live2d.bubbleVisible"
          class="absolute -top-14 left-1/2 -translate-x-1/2
                 glass-panel px-3 py-1.5 text-sm text-[var(--text-primary)]
                 shadow-glass whitespace-nowrap truncate bubble-text"
        >
          {{ live2d.bubbleText }}
        </div>
      </Transition>
    </div>
  </ClientOnly>
</template>

<script setup lang="ts">
import { useLive2DStore } from '~~/stores/live2d'

const props = defineProps<{
  openChat?: () => void
}>()

const live2d = useLive2DStore()
const widgetRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()

const MODEL_PATH = '/live2d/mao/Mao.model3.json'
// 萌系台词库 (P1-2)
const TAP_BUBBLES = [
  '怎么了喵~',
  '别戳啦~',
  '嗯哼？',
  '你好呀喵~',
  '想看博客还是资源呢？',
  '今天也辛苦啦~',
  '点击我可以打开 AI 对话哦~',
  '呼呼~ 在下打盹中~',
  '有什么可以帮你的喵？',
  '欢迎来到狐风轩汐の小屋~',
]

let app: any = null
let model: any = null
let dragOffset = { x: 0, y: 0 }
let dragStart = { x: 0, y: 0 }
const translate = reactive({ x: 0, y: 0 })
const isDragging = ref(false)
let hasDragged = false
let idleMotionIndex = 0
let bubbleTimer: ReturnType<typeof setTimeout> | null = null

// Mobile collapse state (P1-4: <768px default collapsed)
const isMobile = ref(false)
const isMobileCollapsed = ref(false)

function checkMobile() {
  if (typeof window === 'undefined') return
  const wasMobile = isMobile.value
  isMobile.value = window.innerWidth < 768
  // Auto-collapse when entering mobile
  if (isMobile.value && !wasMobile) {
    isMobileCollapsed.value = true
  } else if (!isMobile.value && wasMobile) {
    isMobileCollapsed.value = false
  }
}

const collapsedStyle = computed(() => ({
  right: '12px',
  bottom: '16px',
}))

const positionStyle = computed(() => ({
  transform: `translate(${translate.x}px, ${translate.y}px)`,
  willChange: isDragging.value ? 'transform' : 'auto',
}))

function collapseMobile() {
  isMobileCollapsed.value = true
}

function expandMobile() {
  isMobileCollapsed.value = false
  showBubble('回来啦喵~', 2000)
}

function showBubble(text: string, duration = 3000) {
  live2d.bubbleText = text
  live2d.bubbleVisible = true
  if (bubbleTimer) clearTimeout(bubbleTimer)
  bubbleTimer = setTimeout(() => {
    live2d.bubbleVisible = false
    live2d.bubbleText = ''
  }, duration)
}

async function handleTap() {
  if (hasDragged || !model) return

  const bubble = TAP_BUBBLES[Math.floor(Math.random() * TAP_BUBBLES.length)]
  showBubble(bubble)

  await model.motion('TapBody')
  model.motion('Idle', idleMotionIndex)

  props.openChat?.()
}

function onPointerDown(e: PointerEvent) {
  if (!widgetRef.value) return
  e.preventDefault()
  hasDragged = false
  dragStart = { x: e.clientX, y: e.clientY }
  dragOffset = { x: translate.x, y: translate.y }
  isDragging.value = true

  document.addEventListener('pointermove', onPointerMove)
  document.addEventListener('pointerup', onPointerUp, { once: true })
}

function onPointerMove(e: PointerEvent) {
  const dx = e.clientX - dragStart.x
  const dy = e.clientY - dragStart.y
  if (Math.abs(dx) > 4 || Math.abs(dy) > 4) {
    hasDragged = true
  }
  translate.x = dragOffset.x + dx
  translate.y = dragOffset.y + dy
}

function onPointerUp() {
  isDragging.value = false
  document.removeEventListener('pointermove', onPointerMove)
  setTimeout(() => {
    hasDragged = false
  }, 50)
}

function fitModel() {
  if (!model || !app) return
  const rawWidth = model.internalModel?.width ?? model.width
  const rawHeight = model.internalModel?.height ?? model.height
  if (!rawWidth || !rawHeight) return

  const scaleX = app.screen.width / rawWidth
  const scaleY = app.screen.height / rawHeight
  const scale = Math.min(scaleX, scaleY) * 0.92
  model.scale.set(scale)
  model.anchor.set(0.5, 0.5)
  model.position.set(app.screen.width / 2, app.screen.height / 2)
}

async function initPixi() {
  if (!canvasRef.value || !widgetRef.value || app || typeof window === 'undefined') return

  // Dynamic client-side imports prevent SSR crashes and ensure Cubism Core is loaded first
  const PIXI = await import('pixi.js')
  // Cubism 4 only bundle: Mao is a Cubism 4 model (moc3)
  const { Live2DModel } = await import('pixi-live2d-display/cubism4')

  // pixi-live2d-display needs global PIXI.Ticker reference
  ;(window as any).PIXI = PIXI

  app = new PIXI.Application({
    view: canvasRef.value,
    resizeTo: widgetRef.value,
    backgroundAlpha: 0,
    antialias: true,
    resolution: window.devicePixelRatio || 1,
    autoDensity: true,
  })

  try {
    model = await Live2DModel.from(MODEL_PATH)
    app.stage.addChild(model)
    fitModel()

    // idle motion has Loop=true in the motion file, so it repeats automatically
    idleMotionIndex = Math.floor(Math.random() * 2)
    model.motion('Idle', idleMotionIndex)

    // gaze tracking
    widgetRef.value.addEventListener('pointermove', (e) => {
      if (!model) return
      const rect = widgetRef.value!.getBoundingClientRect()
      model.focus(e.clientX - rect.left, e.clientY - rect.top)
    })

    // speaking lip-sync animation
    let mouthPhase = 0
    app.ticker.add((delta) => {
      if (!model) return
      const coreModel = (model.internalModel as any)?.coreModel
      if (live2d.isSpeaking) {
        mouthPhase += 0.15 * delta
        const open = (Math.sin(mouthPhase) + 1) / 2 * 0.7 + 0.05
        coreModel?.setParameterValueById?.('ParamA', open)
      } else {
        coreModel?.setParameterValueById?.('ParamA', 0)
      }
    })
  } catch (err) {
    // eslint-disable-next-line no-console
    console.error('[Live2D] 加载 Mao 模型失败:', err)
  }
}

function destroyPixi() {
  if (model) {
    model.destroy()
    model = null
  }
  if (app) {
    app.destroy(true, { children: true })
    app = null
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
  // delay to ensure ClientOnly has rendered the DOM
  nextTick(initPixi)
})

onUnmounted(() => {
  destroyPixi()
  document.removeEventListener('pointermove', onPointerMove)
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', checkMobile)
  }
  if (bubbleTimer) clearTimeout(bubbleTimer)
})
</script>

<style scoped>
.live2d-widget {
  width: 140px;
  height: 200px;
  right: 8px;
  bottom: 12px;
  touch-action: none;
}

@media (min-width: 768px) {
  .live2d-widget {
    width: 220px;
    height: 300px;
    right: 16px;
    bottom: 16px;
  }
}

.bubble-text {
  max-width: 140px;
}

@media (min-width: 768px) {
  .bubble-text {
    max-width: 200px;
  }
}

.bubble-enter-active,
.bubble-leave-active {
  transition: all 0.25s ease;
}
.bubble-enter-from,
.bubble-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(10px) scale(0.95);
}

/* Mobile collapse dot button (P1-4) */
.live2d-toggle-dot {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(56, 189, 248, 0.2);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(56, 189, 248, 0.3);
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.live2d-toggle-dot:hover {
  transform: scale(1.1);
  background: rgba(56, 189, 248, 0.3);
}

/* Collapse button on widget (mobile only) */
.live2d-collapse-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.85);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
}

.live2d-collapse-btn:hover {
  background: rgba(220, 38, 38, 1);
  transform: scale(1.1);
}

@media (min-width: 768px) {
  .live2d-collapse-btn {
    display: none;
  }
}
</style>
