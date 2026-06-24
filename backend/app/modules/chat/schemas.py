# AI 对话模块请求/响应模型
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatSessionCreate(BaseModel):
    title: str | None = Field(None, max_length=200)


class ChatSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    model: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class ChatMessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    model: str | None = Field(None, max_length=50)


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: str
    content: str
    created_at: datetime


class ChatQuotaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    date: date
    count: int
    limit: int
    remaining: int
