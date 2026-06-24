# AI 对话业务逻辑
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.chat.models import ChatQuota

DAILY_QUOTA = 50


async def get_or_create_quota(db: AsyncSession, user_id: int, today: date) -> ChatQuota:
    """获取或创建今日配额记录"""
    result = await db.execute(
        select(ChatQuota).where(ChatQuota.user_id == user_id, ChatQuota.date == today)
    )
    quota = result.scalar_one_or_none()
    if quota is None:
        quota = ChatQuota(user_id=user_id, date=today, count=0)
        db.add(quota)
        await db.flush()
    return quota


async def check_quota(user: User, db: AsyncSession) -> bool:
    """检查用户今日配额是否用完（admin 不限）"""
    if user.role == "admin":
        return True
    today = date.today()
    quota = await get_or_create_quota(db, user.id, today)
    return quota.count < DAILY_QUOTA


async def increment_quota(user: User, db: AsyncSession) -> int:
    """递增今日使用计数，返回最新次数"""
    if user.role == "admin":
        return 0
    today = date.today()
    quota = await get_or_create_quota(db, user.id, today)
    quota.count += 1
    await db.flush()
    return quota.count
