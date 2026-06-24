<template>
  <ClientOnly>
    <Transition name="live2d-fade">
      <div
        v-if="visible"
        ref="widgetRef"
        class="fixed z-40 cursor-grab active:cursor-grabbing live2d-widget"
        :class="{ 'pointer-events-none': isDragging, 'live2d-mobile-hidden': isMobileChatFull }"
        :style="positionStyle"
        @pointerdown="onPointerDown"
        @click="handleTap"
      >
        <canvas ref="canvasRef" class="w-full h-full" />

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
    </Transition>
  </ClientOnly>
</template>

<script setup lang="ts">
import { useLive2DStore } from '~~/stores/live2d'

const props = defineProps<{
  visible?: boolean
  openChat?: () => void
}>()

const live2d = useLive2DStore()
const widgetRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()

const MODEL_PATH = '/live2d/mao/Mao.model3.json'
// 萌系台词库
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

const isMobile = ref(false)

function checkMobile() {
  if (typeof window === 'undefined') return
  isMobile.value = window.innerWidth < 768
}

// 移动端聊天面板占满屏幕时不显示 Live2D
const isMobileChatFull = computed(() => isMobile.value && props.visible === true)

const positionStyle = computed(() => ({
  transform: `translate(${translate.x}px, ${translate.y}px)`,
  willChange: isDragging.value ? 'transform' : 'auto',
}))

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

  const PIXI = await import('pixi.js')
  const { Live2DModel } = await import('pixi-live2d-display/cubism4')

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

    idleMotionIndex = Math.floor(Math.random() * 2)
    model.motion('Idle', idleMotionIndex)

    widgetRef.value.addEventListener('pointermove', (e) => {
      if (!model) return
      const rect = widgetRef.value!.getBoundingClientRect()
      model.focus(e.clientX - rect.left, e.clientY - rect.top)
    })

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

// 当 visible 变化时管理 PIXI 生命周期
// 关闭时销毁资源，下次打开重新初始化（避免 v-if 重建 DOM 后旧 app 绑定在已销毁的 canvas 上）
watch(() => props.visible, async (val) => {
  if (val) {
    await nextTick()
    if (!app) {
      initPixi()
    }
  } else {
    // 关闭时销毁 PIXI，下次打开会重新初始化绑定到新的 canvas
    destroyPixi()
  }
})

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
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
/* Live2D 默认在左下角 */
.live2d-widget {
  width: 140px;
  height: 200px;
  left: 8px;
  bottom: 12px;
  touch-action: none;
}

@media (min-width: 768px) {
  .live2d-widget {
    width: 220px;
    height: 300px;
    left: 16px;
    bottom: 16px;
  }
}

/* 移动端聊天面板占满屏幕时隐藏 Live2D */
.live2d-mobile-hidden {
  display: none !important;
}

.bubble-text {
  max-width: 140px;
}

@media (min-width: 768px) {
  .bubble-text {
    max-width: 200px;
  }
}

/* 淡入淡出动画 */
.live2d-fade-enter-active,
.live2d-fade-leave-active {
  transition: opacity 0.5s ease;
}
.live2d-fade-enter-from,
.live2d-fade-leave-to {
  opacity: 0;
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
</style>
