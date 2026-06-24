import MarkdownIt from 'markdown-it'

// 单例 md 实例，避免每次调用都新建
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: false,
})

export function useMarkdown() {
  function render(content: string): string {
    if (!content) return ''
    // 如果内容已经是 HTML（以 < 开头且不含未渲染的 markdown 语法），直接返回
    const trimmed = content.trim()
    if (trimmed.startsWith('<') && !trimmed.includes('# ') && !trimmed.includes('- ') && !trimmed.includes('```')) {
      return content
    }
    return md.render(content)
  }

  return { render }
}
