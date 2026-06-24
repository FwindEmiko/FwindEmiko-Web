# 认证模块请求/响应模型
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    display_name: str | None = Field(None, max_length=100)


class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserLogin(BaseModel):
    username: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class LoginResponse(TokenPair):
    user: UserInfo


class RefreshRequest(BaseModel):
    refresh_token: str


class UserUpdateMe(BaseModel):
    display_name: str | None = Field(None, max_length=100)
    bio: str | None = Field(None, max_length=2000)
    avatar_url: str | None = Field(None, max_length=500)


class ApiResponse(BaseModel):
    code: int = 0
    data: object | None = None
    message: str = "ok"
