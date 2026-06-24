# Session 5 报告：Nuxt3 公网站点集成 Live2D 角色组件

## 概要
在右下角添加了可交互的 Live2D（Mao）角色，实现了点击/拖拽/视线跟随，并与 AI 对话气泡联动。

## 完成内容

### Mao 模型获取
- 从 Live2D/CubismWebSamples 提取 Mao 模型
- 从 Live2D CDN 下载 live2dcubismcore.min.js（GitHub 仓库不再包含预编译文件）

### 依赖安装
- pixi.js@^7 + pixi-live2d-display@0.5.0-beta（0.4.0 与 pixi.js 7 不兼容）

### Live2DWidget 组件
- ClientOnly 包裹防 SSR 报错
- PixiJS Application + pixi-live2d-display 渲染 Mao 模型
- 待机动作（Idle 组循环）、视线跟随（model.focus()）
- 点击触发随机 TapBody 动作 + 随机气泡（3 秒消失）
- 拖拽移动
- 对话时 ticker 驱动 ParamA 实现 lip-sync

### 对话联动
- Pinia store（live2d.ts）：isSpeaking、bubbleText
- ChatPanel SSE chunk → live2d.speak()；done/error → live2d.idle()
- DEV mock 路径同样联动

### 移动端适配
- <768px 缩小到 140×200px；≥768px 220×300px
- pointer 事件统一桌面/移动端拖拽
- touch-action: none 防页面滚动

## 自测结果
全部通过：角色渲染、点击交互、拖拽、视线跟随、对话联动、移动端尺寸

## 修复的问题
1. SSR 500 → ClientOnly + 动态 import
2. PixiJS 7 兼容 → 升级到 pixi-live2d-display@0.5.0-beta
3. z-index 遮挡 ChatPanel → 交换层级
4. 后端 CORS 端口 → 补加 3002
5. DEV mock 补全 → createNewSession + loadQuota
