# 资源展示业务逻辑
import io
import os
import re
import uuid

import aiofiles
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.modules.resources.models import Resource


def _slugify(text: str) -> str:
    """生成 URL 友好的 slug，保留中文字符"""
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\u4e00-\u9fa5a-z0-9-]+", "-", text)
    text = re.sub(r"-+", "-", text)
    text = text.strip("-")
    return text or "resource"


async def generate_unique_slug(db: AsyncSession, title: str, exclude_id: int | None = None) -> str:
    """基于标题生成唯一 slug，重复时追加 -n"""
    base_slug = _slugify(title)
    slug = base_slug
    suffix = 2
    while True:
        stmt = select(Resource).where(Resource.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Resource.id != exclude_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is None:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1


async def save_screenshot(
    db_resource_id: int,
    upload: object,
    caption: str | None = None,
    max_width: int = 1200,
    thumb_width: int = 400,
) -> tuple[str, str]:
    """
    保存截图原图与缩略图。
    返回 (原图 URL, 缩略图 URL)。
    """
    content = await upload.read()
    ext = os.path.splitext(upload.filename or "")[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        ext = ".png"

    base_dir = os.path.join(settings.UPLOAD_DIR, "screenshots", str(db_resource_id))
    os.makedirs(base_dir, exist_ok=True)

    file_id = uuid.uuid4().hex
    original_name = f"{file_id}{ext}"
    original_path = os.path.join(base_dir, original_name)

    async with aiofiles.open(original_path, "wb") as f:
        await f.write(content)

    # 生成缩略图
    thumb_name = f"thumb_{file_id}{ext}"
    thumb_path = os.path.join(base_dir, thumb_name)
    try:
        img = Image.open(io.BytesIO(content))
        if img.mode in ("RGBA", "P") and ext in {".jpg", ".jpeg"}:
            img = img.convert("RGB")
        ratio = min(max_width / max(img.width, 1), 1.0)
        resized = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        resized.save(original_path, optimize=True)

        ratio_thumb = min(thumb_width / max(img.width, 1), 1.0)
        thumb = img.resize((int(img.width * ratio_thumb), int(img.height * ratio_thumb)), Image.LANCZOS)
        if thumb.mode in ("RGBA", "P") and ext in {".jpg", ".jpeg"}:
            thumb = thumb.convert("RGB")
        thumb.save(thumb_path, optimize=True)
    except Exception:
        # 如果处理失败，缩略图与原图相同
        async with aiofiles.open(thumb_path, "wb") as f:
            await f.write(content)

    original_url = f"/uploads/screenshots/{db_resource_id}/{original_name}"
    thumb_url = f"/uploads/screenshots/{db_resource_id}/{thumb_name}"
    return original_url, thumb_url
