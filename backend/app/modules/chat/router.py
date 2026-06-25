# AI 对话路由
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.response import success
from app.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.chat import schemas
from app.modules.chat.llm_client import stream_chat
from app.modules.chat.models import ChatMessage, ChatSession
from app.modules.chat.service import DAILY_QUOTA, check_quota, increment_quota

router = APIRouter()


@router.get("/chat/sessions")
async def list_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """当前用户的会话列表"""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user.id)
        .order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return success([schemas.ChatSessionOut.model_validate(s).model_dump() for s in sessions])


@router.post("/chat/sessions")
async def create_session(
    payload: schemas.ChatSessionCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新会话"""
    session = ChatSession(
        user_id=user.id,
        title=payload.title or "新对话",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return success(schemas.ChatSessionOut.model_validate(session).model_dump())


@router.get("/chat/sessions/{session_id}/messages")
async def list_messages(
    session_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话消息历史"""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    msg_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = msg_result.scalars().all()
    return success([schemas.ChatMessageOut.model_validate(m).model_dump() for m in messages])


@router.delete("/chat/sessions/{session_id}")
async def delete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除会话及其消息（admin 可删全部）"""
    stmt = select(ChatSession).where(ChatSession.id == session_id)
    if user.role != "admin":
        stmt = stmt.where(ChatSession.user_id == user.id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    await db.delete(session)
    await db.commit()
    return success(None)


@router.get("/chat/quota")
async def get_quota(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查看今日对话配额"""
    from datetime import date

    from app.modules.chat.service import get_or_create_quota

    today = date.today()
    quota = await get_or_create_quota(db, user.id, today)
    remaining = DAILY_QUOTA - quota.count if user.role != "admin" else -1
    return success(
        {
            "user_id": user.id,
            "date": today.isoformat(),
            "count": quota.count,
            "limit": None if user.role == "admin" else DAILY_QUOTA,
            "remaining": remaining,
        }
    )


@router.post("/chat/sessions/{session_id}/messages")
async def send_message(
    session_id: int,
    payload: schemas.ChatMessageCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息，SSE 流式返回 AI 回复"""
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user.id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    if not await check_quota(user, db):
        async def error_generator():
            yield f'data: {json.dumps({"type": "error", "message": "今日对话配额已用完"})}\n\n'

        return StreamingResponse(
            error_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    # 保存用户消息
    user_msg = ChatMessage(session_id=session_id, role="user", content=payload.content)
    db.add(user_msg)
    session.message_count += 1
    session.updated_at = datetime.now(timezone.utc)
    await db.flush()

    # 自动设置会话标题（首次用户消息前 30 字符）
    if session.title == "新对话" or not session.title.strip():
        session.title = payload.content[:30]

    # 构造 LLM 上下文（最近 20 条）
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    history = history_result.scalars().all()
    messages = [{"role": m.role, "content": m.content} for m in history[-20:]]

    model = payload.model or session.model

    await increment_quota(user, db)
    await db.commit()

    async def event_generator():
        full_content = ""
        async for chunk in stream_chat(model, messages):
            full_content += chunk
            yield f'data: {json.dumps({"type": "chunk", "content": chunk})}\n\n'

        # 保存 assistant 消息
        assistant_msg = ChatMessage(
            session_id=session_id, role="assistant", content=full_content
        )
        db.add(assistant_msg)
        session.message_count += 1
        session.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(assistant_msg)

        yield f'data: {json.dumps({"type": "done", "message_id": assistant_msg.id})}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
