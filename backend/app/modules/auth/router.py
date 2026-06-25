# 认证路由
import os
import uuid
from datetime import datetime, timezone

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.response import success, error
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import UserRegister, UserLogin, LoginResponse, UserInfo, UserUpdateMe, RefreshRequest

router = APIRouter()


def _token_payload(user: User) -> dict:
    return {"sub": str(user.id), "username": user.username, "role": user.role}


# 允许通过注册接口创建的角色（admin 必须由种子数据或管理员手动赋予）
_REGISTERABLE_ROLES = {"member", "author", "moderator"}


def _resolve_register_role() -> str:
    """从环境变量读取注册默认角色，非法值回退为 member"""
    role = (settings.REGISTER_DEFAULT_ROLE or "member").strip().lower()
    if role not in _REGISTERABLE_ROLES:
        return "member"
    return role


@router.post("/register")
async def register(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 唯一性校验
    existing = await db.execute(
        select(User).where((User.username == payload.username) | (User.email == payload.email))
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="用户名或邮箱已存在",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        role=_resolve_register_role(),
        is_active=True,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token_data = _token_payload(user)
    response = LoginResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserInfo.model_validate(user),
    )
    return success(response.model_dump())


@router.post("/login")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户名密码登录"""
    result = await db.execute(select(User).where(User.username == payload.username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token_data = _token_payload(user)
    response = LoginResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserInfo.model_validate(user),
    )
    return success(response.model_dump())


@router.post("/login/form")
async def login_form(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """OAuth2 表单登录，兼容 Swagger Authorize"""
    result = await db.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    token_data = _token_payload(user)
    response = LoginResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserInfo.model_validate(user),
    )
    return success(response.model_dump())


@router.post("/refresh")
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """使用 refresh_token 换取新的 access_token"""
    payload_data = decode_token(payload.refresh_token)
    if payload_data is None or payload_data.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="刷新令牌无效或已过期",
        )

    user_id = payload_data.get("sub")
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用",
        )

    token_data = _token_payload(user)
    return success({
        "access_token": create_access_token(token_data),
        "token_type": "bearer",
    })


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return success(UserInfo.model_validate(user).model_dump())


@router.put("/me")
async def update_me(payload: UserUpdateMe, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """更新当前用户信息"""
    if payload.display_name is not None:
        user.display_name = payload.display_name
    if payload.bio is not None:
        user.bio = payload.bio
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url

    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return success(UserInfo.model_validate(user).model_dump())


@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传当前用户头像，限制 ≤2MB 的图片"""
    allowed_types = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if file.content_type not in allowed_types:
        return error("仅支持 JPEG/PNG/WebP/GIF 图片", code=422, status_code=422)

    content = await file.read()
    if len(content) > settings.AVATAR_MAX_SIZE:
        return error("头像大小不能超过 2MB", code=422, status_code=422)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        ext = ".png"

    upload_dir = os.path.join(settings.UPLOAD_DIR, "avatars")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"{user.id}_{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    user.avatar_url = f"/uploads/avatars/{filename}"
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    return success(UserInfo.model_validate(user).model_dump())
