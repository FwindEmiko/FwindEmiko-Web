# 博客业务逻辑
import re

import markdown
from pygments.formatters import HtmlFormatter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.blog.models import Post


def render_md(content: str) -> str:
    """将 Markdown 渲染为 HTML，支持代码语法高亮"""
    return markdown.markdown(
        content,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "nl2br",
        ],
        extension_configs={
            "codehilite": {
                "guess_lang": True,
                "css_class": "highlight",
                "noclasses": False,
                "pygments_style": "monokai",
            },
        },
    )


def get_highlight_css() -> str:
    """生成 Pygments 语法高亮 CSS（Monokai 深色主题）"""
    formatter = HtmlFormatter(style="monokai", noclasses=False)
    return formatter.get_style_defs(".highlight")


def _slugify(text: str) -> str:
    """生成 URL 友好的 slug，保留中文字符"""
    text = text.strip().lower()
    # 将空白字符替换为 -
    text = re.sub(r"\s+", "-", text)
    # 保留中文、字母、数字、-，其余替换为 -
    text = re.sub(r"[^\u4e00-\u9fa5a-z0-9-]+", "-", text)
    # 合并多个 -
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text or "post"


async def generate_unique_slug(db: AsyncSession, title: str, exclude_id: int | None = None) -> str:
    """基于标题生成唯一 slug，重复时追加 -n"""
    base_slug = _slugify(title)
    slug = base_slug
    suffix = 2
    while True:
        stmt = select(Post).where(Post.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Post.id != exclude_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1
