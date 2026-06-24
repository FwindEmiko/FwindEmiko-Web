# 通用文件上传路由
import os
import uuid
from typing import Any

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.config import settings
from app.core.response import success
from app.modules.auth.dependencies import require_role
from app.modules.auth.models import User

router = APIRouter()


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/svg+xml",
}
ALLOWED_FILE_TYPES = {
    "application/zip",
    "application/x-zip-compressed",
    "application/java-archive",
    "application/octet-stream",
    "text/plain",
    "application/json",
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    user: User = Depends(require_role("admin", "author")),
):
    """通用文件上传，返回可直接访问的 URL"""
    upload_dir = os.path.join(settings.UPLOAD_DIR, "editor")
    os.makedirs(upload_dir, exist_ok=True)

    succ_map: dict[str, str] = {}
    err_files: list[str] = []

    for upload in files:
        content_type = upload.content_type or "application/octet-stream"
        if content_type not in ALLOWED_IMAGE_TYPES and content_type not in ALLOWED_FILE_TYPES:
            err_files.append(upload.filename or "unknown")
            continue

        content = await upload.read()
        if len(content) == 0:
            err_files.append(upload.filename or "unknown")
            continue

        ext = os.path.splitext(upload.filename or "")[1].lower()
        if not ext:
            ext = ".bin"
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(upload_dir, filename)

        async with aiofiles.open(filepath, "wb") as f:
            await f.write(content)

        url = f"/uploads/editor/{filename}"
        succ_map[upload.filename or filename] = url

    return success(
        {
            "errFiles": err_files,
            "succMap": succ_map,
        }
    )
