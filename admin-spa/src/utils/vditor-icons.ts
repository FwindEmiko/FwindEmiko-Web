/**
 * Vditor 编辑器图标预加载
 *
 * Vditor 内部使用同步 XHR (addScriptSync) 加载 material.js 图标脚本，
 * 在某些环境下（如服务器 CSP 限制、跨域配置等）可能加载失败，导致工具栏图标不显示。
 *
 * 本工具在 Vditor 初始化前，使用 fetch 异步预加载 material.js 并注入到 DOM 中，
 * 确保 SVG sprite 被正确注入。Vditor 内部的 addScriptSync 会检测到脚本已存在而跳过重复加载。
 */

const ICON_SCRIPT_ID = 'vditorIconScript'

/**
 * 预加载 Vditor 图标
 * @param cdnBase Vditor CDN 基础路径（如 '/admin/vditor'）
 * @param icon 图标库名称，默认 'material'
 */
export async function preloadVditorIcons(
  cdnBase: string,
  icon: string = 'material'
): Promise<void> {
  if (document.getElementById(ICON_SCRIPT_ID)) return

  const url = `${cdnBase}/dist/js/icons/${icon}.js`
  try {
    const response = await fetch(url)
    if (!response.ok) {
      console.warn(`[Vditor] 图标加载失败: ${url} (${response.status})`)
      return
    }
    const text = await response.text()
    const script = document.createElement('script')
    script.id = ICON_SCRIPT_ID
    script.text = text
    document.head.appendChild(script)
  } catch (e) {
    console.warn('[Vditor] 图标预加载失败:', e)
  }
}
