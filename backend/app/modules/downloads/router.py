# 下载站路由
import hashlib
import os
import uuid
from datetime import datetime, timezone
from typing import Any

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.response import success
from app.database import get_db
from app.modules.auth.dependencies import get_current_user_optional, require_role
from app.modules.auth.models import User
from app.modules.downloads import schemas
from app.modules.downloads.models import FileNode, Folder, FolderPermission
from app.modules.downloads.permission import check_folder_access

router = APIRouter()


def _get_user_role(user: User | None) -> str:
    return user.role if user else "guest"


async def _can_read_folder(folder_id: int, user: User | None, db: AsyncSession) -> bool:
    return await check_folder_access(folder_id, user, "read", db)


async def _can_download_folder(folder_id: int, user: User | None, db: AsyncSession) -> bool:
    return await check_folder_access(folder_id, user, "download", db)


def _build_folder_tree(folders: list[Folder]) -> list[dict[str, Any]]:
    """将扁平文件夹列表构建为嵌套树"""
    folder_map = {f.id: f for f in folders}
    children_map: dict[int, list[Folder]] = {}
    roots: list[Folder] = []

    for folder in folders:
        if folder.parent_id is None:
            roots.append(folder)
        else:
            children_map.setdefault(folder.parent_id, []).append(folder)

    def _build(folder: Folder) -> dict[str, Any]:
        node = {
            "id": folder.id,
            "name": folder.name,
            "slug": folder.slug,
            "description": folder.description,
            "is_visible": folder.is_visible,
            "sort_order": folder.sort_order,
            "children": [_build(child) for child in children_map.get(folder.id, [])],
        }
        node["children"].sort(key=lambda x: x["sort_order"])
        return node

    tree = [_build(root) for root in roots]
    tree.sort(key=lambda x: x["sort_order"])
    return tree


async def _get_breadcrumbs(folder_id: int, db: AsyncSession) -> list[dict[str, Any]]:
    """获取文件夹面包屑"""
    breadcrumbs = []
    current = await db.get(Folder, folder_id)
    while current:
        breadcrumbs.append({"id": current.id, "name": current.name})
        if current.parent_id is None:
            break
        current = await db.get(Folder, current.parent_id)
    return list(reversed(breadcrumbs))


@router.get("/downloads/folders")
async def list_folders(
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """当前用户可见的文件夹树"""
    result = await db.execute(select(Folder))
    all_folders = list(result.scalars().all())
    visible_folders = [f for f in all_folders if await _can_read_folder(f.id, user, db)]
    return success(_build_folder_tree(visible_folders))


@router.get("/downloads/folders/{folder_id}/files")
async def list_folder_files(
    folder_id: int,
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """文件夹详情、子文件夹与文件列表"""
    folder = await db.get(Folder, folder_id)
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件夹不存在")
    if not await _can_read_folder(folder_id, user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问该文件夹")

    # 子文件夹（仅可见）
    sub_result = await db.execute(select(Folder).where(Folder.parent_id == folder_id))
    subfolders = [
        schemas.SubFolderItem.model_validate(f).model_dump()
        for f in sub_result.scalars().all()
        if await _can_read_folder(f.id, user, db)
    ]
    subfolders.sort(key=lambda x: x["name"])

    # 文件
    files_result = await db.execute(
        select(FileNode).where(FileNode.folder_id == folder_id).order_by(FileNode.filename)
    )
    files = []
    for f in files_result.scalars().all():
        item = schemas.FileItem.model_validate(f).model_dump()
        item["has_external"] = bool(f.external_url)
        files.append(item)

    return success(
        {
            "folder": {
                "id": folder.id,
                "name": folder.name,
                "slug": folder.slug,
                "description": folder.description,
                "is_visible": folder.is_visible,
                "sort_order": folder.sort_order,
            },
            "breadcrumbs": await _get_breadcrumbs(folder_id, db),
            "subfolders": subfolders,
            "files": files,
        }
    )


def _resolve_storage_path(storage_path: str) -> str:
    """解析文件存储路径为绝对路径，兼容新旧两种存储格式。

    新格式: storage_path 相对于 UPLOAD_DIR（如 downloads/3/xxx.txt）
    旧格式: storage_path 含 UPLOAD_DIR 前缀（如 ./uploads/downloads/3/xxx.txt）
    """
    if os.path.isabs(storage_path) and os.path.exists(storage_path):
        return storage_path

    # 新格式：相对 UPLOAD_DIR 拼接
    new_path = os.path.join(settings.UPLOAD_DIR, storage_path)
    if os.path.exists(new_path):
        return new_path

    # 旧格式：可能已经包含 UPLOAD_DIR，尝试去掉重复前缀后再拼接
    normalized = storage_path
    upload_prefix = settings.UPLOAD_DIR.rstrip("/\\")
    if normalized.startswith(upload_prefix):
        normalized = normalized[len(upload_prefix):].lstrip("/\\")
        legacy_path = os.path.join(settings.UPLOAD_DIR, normalized)
        if os.path.exists(legacy_path):
            return legacy_path

    # 兜底返回新格式路径（让调用方报 404）
    return new_path


@router.get("/downloads/files/{file_id}/download")
async def download_file(
    file_id: int,
    user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """下载文件，触发计数；本地文件流式返回，外部链接 302 跳转"""
    result = await db.execute(select(FileNode).where(FileNode.id == file_id))
    file_node = result.scalar_one_or_none()
    if file_node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    if not await _can_download_folder(file_node.folder_id, user, db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权下载该文件")

    file_node.download_count += 1
    await db.commit()

    if file_node.external_url:
        return RedirectResponse(file_node.external_url)

    full_path = _resolve_storage_path(file_node.storage_path)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="物理文件不存在")

    async def file_stream():
        async with aiofiles.open(full_path, "rb") as f:
            while chunk := await f.read(1024 * 1024):
                yield chunk

    filename = file_node.display_name or file_node.filename
    return StreamingResponse(
        file_stream(),
        media_type=file_node.mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


# === 管理接口 ===


async def _apply_permission_rules(
    db: AsyncSession, folder_id: int, rules: list[schemas.FolderPermissionRule]
):
    """应用文件夹权限规则：先删除旧规则，再插入新规则"""
    await db.execute(
        delete(FolderPermission).where(FolderPermission.folder_id == folder_id)
    )
    for rule in rules:
        perm = FolderPermission(
            folder_id=folder_id,
            role=rule.role,
            can_read=rule.can_read,
            can_download=rule.can_download,
            can_upload=rule.can_upload,
            can_delete=rule.can_delete,
        )
        db.add(perm)


@router.post("/downloads/folders")
async def create_folder(
    payload: schemas.FolderCreate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """创建文件夹（admin）"""
    slug = payload.slug or payload.name.strip().lower().replace(" ", "-")
    existing = await db.execute(select(Folder).where(Folder.slug == slug))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="文件夹 slug 已存在")

    folder = Folder(
        name=payload.name,
        slug=slug,
        parent_id=payload.parent_id,
        description=payload.description,
        is_visible=payload.is_visible,
        sort_order=payload.sort_order,
    )
    db.add(folder)
    await db.flush()

    if payload.permission_rules:
        await _apply_permission_rules(db, folder.id, payload.permission_rules)

    await db.commit()
    await db.refresh(folder)
    return success(schemas.FolderTreeNode.model_validate(folder).model_dump())


@router.put("/downloads/folders/{folder_id}")
async def update_folder(
    folder_id: int,
    payload: schemas.FolderUpdate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """更新文件夹（admin）"""
    result = await db.execute(select(Folder).where(Folder.id == folder_id))
    folder = result.scalar_one_or_none()
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件夹不存在")

    if payload.name is not None:
        folder.name = payload.name
    if payload.slug is not None:
        folder.slug = payload.slug
    if payload.parent_id is not None:
        # 避免循环引用
        if payload.parent_id == folder_id:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="不能将自己设为父文件夹")
        folder.parent_id = payload.parent_id
    if payload.description is not None:
        folder.description = payload.description
    if payload.is_visible is not None:
        folder.is_visible = payload.is_visible
    if payload.sort_order is not None:
        folder.sort_order = payload.sort_order

    if payload.permission_rules is not None:
        await _apply_permission_rules(db, folder_id, payload.permission_rules)

    folder.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(folder)
    return success(schemas.FolderTreeNode.model_validate(folder).model_dump())


@router.delete("/downloads/folders/{folder_id}")
async def delete_folder(
    folder_id: int,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """删除文件夹（admin），非空禁止删除"""
    folder = await db.get(Folder, folder_id)
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件夹不存在")

    sub_count = (
        await db.execute(select(func.count(Folder.id)).where(Folder.parent_id == folder_id))
    ).scalar() or 0
    file_count = (
        await db.execute(select(func.count(FileNode.id)).where(FileNode.folder_id == folder_id))
    ).scalar() or 0
    if sub_count > 0 or file_count > 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="文件夹非空，无法删除",
        )

    await db.delete(folder)
    await db.commit()
    return success(None)


@router.post("/downloads/files")
async def upload_files(
    folder_id: int = Query(...),
    files: list[UploadFile] = File(...),
    user: User = Depends(require_role("admin", "author", "member")),
    db: AsyncSession = Depends(get_db),
):
    """上传文件到指定文件夹（需 can_upload 权限）"""
    folder = await db.get(Folder, folder_id)
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件夹不存在")

    if not await check_folder_access(folder_id, user, "upload", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权上传到该文件夹")

    base_dir = os.path.join(settings.UPLOAD_DIR, "downloads", str(folder_id))
    os.makedirs(base_dir, exist_ok=True)

    created = []
    for upload in files:
        content = await upload.read()
        file_hash = hashlib.sha256(content).hexdigest()
        file_id = uuid.uuid4().hex
        storage_name = f"{file_id}_{upload.filename or 'unknown'}"
        storage_path = os.path.join(base_dir, storage_name)

        async with aiofiles.open(storage_path, "wb") as f:
            await f.write(content)

        # 存储相对于 UPLOAD_DIR 的路径，避免下载时重复拼接
        rel_path = os.path.join("downloads", str(folder_id), storage_name)
        file_node = FileNode(
            folder_id=folder_id,
            filename=upload.filename or "unknown",
            file_size=len(content),
            file_hash=file_hash,
            mime_type=upload.content_type or "application/octet-stream",
            storage_path=rel_path,
        )
        db.add(file_node)
        await db.flush()
        created.append(file_node)

    await db.commit()
    return success([schemas.FileItem.model_validate(f).model_dump() for f in created])


@router.delete("/downloads/files/{file_id}")
async def delete_file(
    file_id: int,
    user: User = Depends(require_role("admin", "author", "member")),
    db: AsyncSession = Depends(get_db),
):
    """删除文件（需 can_delete 权限），同时删除物理文件"""
    result = await db.execute(select(FileNode).where(FileNode.id == file_id))
    file_node = result.scalar_one_or_none()
    if file_node is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    if not await check_folder_access(file_node.folder_id, user, "delete", db):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除该文件")

    full_path = _resolve_storage_path(file_node.storage_path)
    if os.path.exists(full_path):
        os.remove(full_path)

    await db.delete(file_node)
    await db.commit()
    return success(None)


# === 权限矩阵管理接口（admin） ===

ALL_ROLES = ["admin", "author", "member", "guest"]


@router.get("/admin/permissions/folders")
async def get_permission_matrix(
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """返回所有文件夹 + 各角色权限矩阵"""
    folders_result = await db.execute(select(Folder).order_by(Folder.id))
    folders = list(folders_result.scalars().all())

    perms_result = await db.execute(select(FolderPermission))
    all_perms = list(perms_result.scalars().all())

    # 按 folder_id 分组
    perms_by_folder: dict[int, list[FolderPermission]] = {}
    for p in all_perms:
        perms_by_folder.setdefault(p.folder_id, []).append(p)

    matrix_folders: list[dict] = []
    for folder in folders:
        folder_perms = perms_by_folder.get(folder.id, [])
        perm_items: list[dict] = []
        for role in ALL_ROLES:
            existing = next((p for p in folder_perms if p.role == role), None)
            if existing:
                perm_items.append(
                    {
                        "folder_id": folder.id,
                        "folder_name": folder.name,
                        "role": role,
                        "can_read": existing.can_read,
                        "can_download": existing.can_download,
                        "can_upload": existing.can_upload,
                        "can_delete": existing.can_delete,
                    }
                )
            else:
                # 默认值：admin 全开，其他角色 read=True 其余 False
                if role == "admin":
                    perm_items.append(
                        {
                            "folder_id": folder.id,
                            "folder_name": folder.name,
                            "role": role,
                            "can_read": True,
                            "can_download": True,
                            "can_upload": True,
                            "can_delete": True,
                        }
                    )
                else:
                    perm_items.append(
                        {
                            "folder_id": folder.id,
                            "folder_name": folder.name,
                            "role": role,
                            "can_read": True,
                            "can_download": False,
                            "can_upload": False,
                            "can_delete": False,
                        }
                    )
        matrix_folders.append(
            {
                "folder_id": folder.id,
                "folder_name": folder.name,
                "permissions": perm_items,
            }
        )

    return success({"folders": matrix_folders, "roles": ALL_ROLES})


@router.put("/admin/permissions")
async def update_permission_matrix(
    payload: schemas.PermissionBatchUpdate,
    user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """批量更新文件夹权限矩阵

    对每个 (folder_id, role) 组合执行 upsert：
    - 存在则更新
    - 不存在则插入
    admin 角色记录强制保持全权限（防止误锁）
    """
    # 按 folder_id 分组请求项
    by_folder: dict[int, list[schemas.PermissionBatchUpdateItem]] = {}
    for item in payload.items:
        by_folder.setdefault(item.folder_id, []).append(item)

    for folder_id, items in by_folder.items():
        # 拉取该文件夹现有权限
        existing_result = await db.execute(
            select(FolderPermission).where(FolderPermission.folder_id == folder_id)
        )
        existing_perms = {p.role: p for p in existing_result.scalars().all()}

        for item in items:
            # admin 强制全开，防止误锁
            if item.role == "admin":
                can_read = can_download = can_upload = can_delete = True
            else:
                can_read = item.can_read
                can_download = item.can_download
                can_upload = item.can_upload
                can_delete = item.can_delete

            if item.role in existing_perms:
                perm = existing_perms[item.role]
                perm.can_read = can_read
                perm.can_download = can_download
                perm.can_upload = can_upload
                perm.can_delete = can_delete
            else:
                db.add(
                    FolderPermission(
                        folder_id=folder_id,
                        role=item.role,
                        can_read=can_read,
                        can_download=can_download,
                        can_upload=can_upload,
                        can_delete=can_delete,
                    )
                )

    await db.commit()
    return success(None)
