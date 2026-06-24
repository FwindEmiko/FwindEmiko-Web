# 08 — Live2D 集成

> **依赖**: `06-frontend-nuxt.md`  
> **目标**: 右下角 Live2D 角色 + 对话气泡 + 点击交互 + 与 AI 对话联动  
> **占位模型**: Niziiro Mao → 未来替换为星玖定制模型

---

## 1. 获取 Mao 模型文件

从 Live2D 官方 Cubism SDK for Web Samples 提取：

```bash
# 1. 下载 SDK
#    https://www.live2d.com/en/download/cubism-sdk/download-web/
#    或直接 clone 官方 GitHub:
git clone https://github.com/Live2D/CubismWebSamples.git --depth 1

# 2. 复制 Mao 模型到项目中
#    源路径: CubismWebSamples/Samples/Resources/Mao/
#    目标路径: nuxt-app/public/live2d/mao/
cp -r CubismWebSamples/Samples/Resources/Mao nuxt-app/public/live2d/mao/

# 3. 复制 Cubism Core（运行时库）
#    源路径: CubismWebSamples/Core/live2dcubismcore.min.js
#    目标路径: nuxt-app/public/live2d/
cp CubismWebSamples/Core/live2dcubismcore.min.js nuxt-app/public/live2d/
```

最终目录结构：
```
nuxt-app/public/live2d/
├── live2dcubismcore.min.js     # Cubism 4 Core 运行时
└── mao/
    ├── Mao.model3.json          # 模型入口
    ├── Mao.moc3                 # 模型数据
    ├── Mao.2048/
    │   └── texture_00.png       # 贴图
    ├── expressions/             # 表情
    │   └── exp_01.exp3.json
    ├── motions/                 # 动作
    │   ├── mtn_01.motion3.json
    │   ├── sample_01.motion3.json
    │   └── special_01.motion3.json
    └── Mao.physics3.json        # 物理效果
```

---

## 2. 技术栈

```
Live2DWidget.vue (Nuxt3 组件, 右下角固定定位)
    │
    ├── PixiJS Application (Canvas)
    │   └── pixi-live2d-display (npm 包)
    │       └── Mao.model3.json → 渲染角色
    │
    ├── 交互层
    │   ├── 鼠标悬停 → 视线跟随
    │   ├── 点击 → 触发 tap 动作 + 随机气泡文本
    │   └── 对话中 → 播放说话动画
    │
    └── LLM 桥接
        └── ChatPanel 组件发送消息
            → SSE 流式读取
            → Live2D 播放说话动画 + 对话气泡逐字显示
```

---

## 3. 安装依赖

```bash
cd nuxt-app
pnpm add pixi.js@^7 pixi-live2d-display
# pixi-live2d-display 依赖 live2dcubismcore.min.js
# 在 nuxt.config.ts 中配置 script 预加载
```

---

## 4. Live2DWidget 组件

```vue
<!-- nuxt-app/components/live2d/Live2DWidget.vue -->
<template>
  <ClientOnly>
    <div
      ref="containerRef"
      class="fixed bottom-4 right-4 z-50 cursor-pointer 
             w-[180px] h-[240px] md:w-[220px] md:h-[300px]"
      :class="{ 'pointer-events-none': isDragging }"
      @click="handleTap"
    >
      <!-- PixiJS Canvas 挂载点 -->
      <canvas ref="canvasRef" class="w-full h-full" />
      
      <!-- 对话气泡 -->
      <Transition name="bubble">
        <div
          v-if="bubbleText"
          class="absolute -top-16 left-1/2 -translate-x-1/2
                 bg-glass backdrop-blur-glass border border-glass-border
                 rounded-glass px-3 py-1.5 text-sm text-white
                 shadow-glass whitespace-nowrap max-w-[200px] truncate"
        >
          {{ bubbleText }}
        </div>
      </Transition>
    </div>
  </ClientOnly>
</template>

<script setup lang="ts">
// ⚠️ 关键: 使用 ClientOnly 包裹，避免 SSR 时 canvas API 报错

// === 模型加载 ===
// 1. 创建 PixiJS Application (透明背景)
// 2. 加载 Mao.model3.json (从 /live2d/mao/Mao.model3.json)
// 3. 设置 Scale 适配容器大小
// 4. 加载默认表情 + 待机动作

// === 交互 ===
// handleTap:
//   播放随机 Tap 动作 (从 motions/ 中选择)
//   显示随机气泡: ["怎么了喵？", "嗯？", "别戳我~", "你好呀"]
//   气泡 3 秒后自动消失

// === 拖拽 ===
// 移动端/桌面端均可拖拽 Live2D 到屏幕任意位置
// 用 @vueuse/core 的 useDraggable 或手写 mousedown/move/up

// === 对话模式 ===
// 提供 speak(text: string) 方法:
//   接收 AI 回复文本 → 显示气泡逐字效果
//   调用 Live2D 说话动作 → 唇形同步参数
// props/methods 由父组件或 provide/inject 暴露

defineExpose({ speak, setMood })
</script>
```

---

## 5. Live2D ↔ Chat 联动

```
ChatPanel.vue                    Live2DWidget.vue
    │                                  │
    ├── 用户发送消息                      │
    │   └── POST /api/chat → SSE        │
    │       └── onToken(chunk) ─────────→ speak(chunk)  
    │          逐 token 追加到气泡         │   播放说话动画
    │                                  │
    ├── 对话结束                          │
    │   └── onComplete() ─────────────→ idle()
    │                                  │   回到待机动画
```

在 Nuxt3 中跨组件通信：`provide/inject` 或 Pinia store。

```ts
// stores/live2d.ts
export const useLive2DStore = defineStore('live2d', () => {
  const isSpeaking = ref(false)
  const bubbleText = ref('')

  function speak(chunk: string) {
    bubbleText.value += chunk
    isSpeaking.value = true
  }

  function idle() {
    isSpeaking.value = false
    setTimeout(() => { bubbleText.value = '' }, 2000)
  }

  return { isSpeaking, bubbleText, speak, idle }
})
```

---

## 6. 替换为星玖模型（未来）

模型文件路径约定不变：

```
nuxt-app/public/live2d/xingjiu/
├── Xingjiu.model3.json
├── Xingjiu.moc3
├── textures/
├── expressions/
├── motions/
└── Xingjiu.physics3.json
```

替换步骤：
1. 将星玖模型文件放入 `public/live2d/xingjiu/`
2. 修改 `Live2DWidget.vue` 中模型路径 → `xingjiu/Xingjiu.model3.json`
3. 保持动作组同名（Tap, Idle, Special）→ 交互逻辑无需改动
4. 更新气泡文本数组 → 星玖风格的台词

---

## 7. 移动端适配

```css
/* 移动端缩小到 70% */
@media (max-width: 768px) {
  .live2d-container {
    width: 140px !important;
    height: 200px !important;
    bottom: 12px;
    right: 8px;
  }
}
```

- 移动端拖拽更敏感（手指比鼠标大）
- 气泡文字截断更短（`max-w-[140px]`）
- 对话面板在移动端全屏弹出（避免被 Live2D 遮挡）

---

## 8. 许可注意事项

- Live2D Cubism Core 遵循 Live2D 使用协议——非商业个人站点可用
- Mao 模型属于 Live2D Free Material License，允许个人展示/测试
- 未来星玖定制模型不受此协议限制

---

## 9. 验证方式

```bash
cd nuxt-app
pnpm dev
# 访问 http://localhost:3000

# 验证清单:
# [ ] 右下角显示 Mao 角色（Canvas 正常渲染）
# [ ] 鼠标悬停时角色视线跟随
# [ ] 点击角色触发动作 + 气泡弹出
# [ ] 气泡 3 秒后自动消失
# [ ] 拖拽角色可移动到任意位置
# [ ] 移动端（F12 模拟）角色缩小 + 拖拽正常
# [ ] 已登录 → 发送 AI 消息 → 角色进入说话状态
# [ ] 未登录 → 点击角色只显示静态气泡，不触发对话
```

---

> **下一份**: `09-deployment.md` — 部署参考
