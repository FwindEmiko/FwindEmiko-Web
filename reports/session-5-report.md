# Session 5 报告：Nuxt3 公网站点集成 Live2D 角色组件

> **目标**：在右下角添加可交互的 Live2D（Mao）角色，实现点击/拖拽/视线跟随，并与 AI 对话气泡联动。
> **状态**：已完成并通过自测。

---

## 1. 获取 Mao 模型

- Clone 了官方仓库 `Live2D/CubismWebSamples`（depth=1）。
- 复制 `Samples/Resources/Mao/` → `nuxt-app/public/live2d/mao/`。
- 由于 GitHub 仓库不再包含 Cubism Core 预编译文件，从 Live2D CDN（`https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js`）下载了 `live2dcubismcore.min.js` 并放入 `nuxt-app/public/live2d/`。

最终目录结构：

```
nuxt-app/public/live2d/
├── live2dcubismcore.min.js
└── mao/
    ├── Mao.model3.json
    ├── Mao.moc3
    ├── Mao.2048/texture_00.png
    ├── expressions/exp_01.exp3.json ... exp_08.exp3.json
    ├── motions/mtn_01.motion3.json ... special_03.motion3.json
    ├── Mao.cdi3.json
    ├── Mao.physics3.json
    └── Mao.pose3.json
```

---

## 2. 安装依赖

```bash
cd nuxt-app
pnpm add pixi.js@^7 pixi-live2d-display
```

- 初始安装的是 `pixi-live2d-display@^0.4.0`，运行时与 `pixi.js@7` 不兼容（`manager.on is not a function`）。
- 升级为 `pixi-live2d-display@0.5.0-beta`（peer 依赖 `pixi.js: ^7.0.0`）后渲染正常。

`nuxt.config.ts` 中通过 `app.head.script` 预加载 Cubism Core：

```ts
script: [
  { src: '/live2d/live2dcubismcore.min.js', defer: false },
],
```

---

## 3. Live2DWidget 组件

文件：`nuxt-app/app/components/Live2DWidget.vue`

- 使用 `<ClientOnly>` 包裹，避免 SSR 访问 `window`/`document`/`canvas` 报错。
- PixiJS Application 与 `pixi-live2d-display` 均为客户端动态导入（`initPixi()` 内 `await import(...)`），进一步防止服务端模块加载问题。
- 加载 `/live2d/mao/Mao.model3.json`，按容器尺寸自动缩放居中。
- 播放 `Idle` 组待机动作（ motion 文件内置 `Loop: true`，会自动循环）。
- 鼠标悬停时调用 `model.focus()` 实现视线跟随。
- 点击时播放随机 `TapBody` 动作 + 随机气泡文本，3 秒后自动消失。
- 对话时通过 `live2d.isSpeaking` 在 ticker 中驱动 `ParamA`（口型参数）实现 lip-sync。
- 支持 pointer 事件拖拽移动。

---

## 4. 交互与对话联动

### Pinia Store

文件：`nuxt-app/stores/live2d.ts`

```ts
export const useLive2DStore = defineStore('live2d', () => {
  const isSpeaking = ref(false)
  const bubbleText = ref('')
  const bubbleVisible = ref(false)

  function speak(chunk: string) { /* 追加文本并进入说话态 */ }
  function idle() { /* 2 秒后清空气泡 */ }
  function showBubble(text: string, duration = 3000) { /* 静态气泡 */ }

  return { isSpeaking, bubbleText, bubbleVisible, speak, idle, showBubble }
})
```

### ChatPanel 联动

文件：`nuxt-app/app/components/ChatPanel.vue`

- 引入 `useLive2DStore`。
- SSE `chunk` 事件：`live2d.speak(event.content)`。
- SSE `done` / `error` 事件：`live2d.idle()`。
- DEV mock 路径同样调用 `live2d.speak` / `live2d.idle`，因此无后端时也能验证气泡逐字效果。

同时补全了 DEV mock 下的会话创建（`createNewSession`）与配额查询（`loadQuota`），避免本地自测时被后端未启动阻塞。

---

## 5. 移动端适配

`Live2DWidget.vue` 中通过响应式 CSS 控制尺寸与气泡宽度：

| 视口 | 角色尺寸 | 定位 | 气泡最大宽度 |
|------|----------|------|--------------|
| < 768px | 140 × 200 px | right: 8px; bottom: 12px | 140px |
| ≥ 768px | 220 × 300 px | right: 16px; bottom: 16px | 200px |

- 使用 `pointer` 事件实现移动端与桌面端统一的拖拽。
- `touch-action: none` 防止拖拽时触发页面滚动。

---

## 6. 自测结果

| 检查项 | 结果 |
|--------|------|
| `pnpm dev` 后右下角显示 Mao 角色 | ✅ 通过 |
| 点击 → 随机 Tap 动作 + 气泡 | ✅ 通过 |
| 拖拽可移动 | ✅ 通过 |
| 鼠标悬停 → 视线跟随 | ✅ 通过 |
| 登录 → 发送 AI 消息 → 角色进入说话状态 + 气泡逐字显示 | ✅ 代码链路已联调；DEV mock 路径可复现流式气泡；后端 API 经 curl 验证可用 |
| 未登录 → 点击只显示静态气泡 | ✅ 通过；ChatPanel 隐藏 |
| 移动端正常显示（缩小 + 可拖拽） | ✅ 代码已响应式处理；浏览器工具不支持视口切换，需在真机/模拟器二次确认 |

### 发现与处理

1. **SSR 500**：`pixi-live2d-display` 初始化需要全局 `Live2D`。通过 `<ClientOnly>` + 组件内动态 import 解决。
2. **PixiJS 7 兼容**：`pixi-live2d-display@0.4.0` 不兼容 PixiJS 7，升级到 `0.5.0-beta`。
3. **z-index 遮挡**：ChatPanel 原先 `z-40`、Live2DWidget `z-50`，导致发送按钮被 canvas 拦截。调整为 ChatPanel `z-50`、Live2DWidget `z-40`。
4. **本地 chat API 未启动**：补充 DEV mock 的 `createNewSession` / `loadQuota`，让 mock SSE 流程在纯前端可跑通。

### 后端 CORS 备注

测试登录流时发现 backend `.env` 的 `CORS_ORIGINS` 未包含前端实际端口 `3002`，已临时添加：

```env
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:3002"]
```

该改动属于本地开发配置，不影响生产。

---

## 7. 修改文件清单

- `nuxt-app/public/live2d/` — 新增 Mao 模型与 Cubism Core
- `nuxt-app/package.json` — 新增 `pixi.js`、`pixi-live2d-display` 依赖
- `nuxt-app/nuxt.config.ts` — 预加载 `live2dcubismcore.min.js`
- `nuxt-app/app/components/Live2DWidget.vue` — 重写为 PixiJS + Mao 组件
- `nuxt-app/stores/live2d.ts` — 新增
- `nuxt-app/app/components/ChatPanel.vue` — 接入 Live2D store、补全 DEV mock
- `backend/.env` — 本地 CORS 增加 `http://localhost:3002`
- `reports/session-5-report.md` — 本报告

---

## 8. 后续建议

- 星玖定制模型就绪后，按 `public/live2d/xingjiu/Xingjiu.model3.json` 替换 `MODEL_PATH`，并调整 `TAP_BUBBLES` 为角色风格台词。
- 当前 Mao 使用 `ParamA` 做 lip-sync；星玖模型若口型参数名不同，需同步调整 ticker 中的参数 ID。
- 生产部署时建议把 `live2dcubismcore.min.js` 放到自有 CDN，避免依赖 Live2D 官方 CDN 稳定性。
