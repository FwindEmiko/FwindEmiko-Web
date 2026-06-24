# FastAPI 应用入口
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import engine, Base
from app.core.response import error
from app.modules.auth.router import router as auth_router
from app.modules.blog.router import router as blog_router
from app.modules.resources.router import router as resources_router
from app.modules.downloads.router import router as downloads_router
from app.modules.chat.router import router as chat_router
from app.modules.admin.router import router as admin_router
from app.modules.files.router import router as files_router

# 导入模型以确保 Base.metadata 注册全部表
from app.modules.auth.models import User  # noqa: F401
from app.modules.blog.models import Category, Post, Tag  # noqa: F401
from app.modules.resources.models import Resource, ResourceVersion, Screenshot  # noqa: F401
from app.modules.downloads.models import Folder, FileNode, FolderPermission  # noqa: F401
from app.modules.chat.models import ChatSession, ChatMessage, ChatQuota  # noqa: F401

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时建表，关闭时释放连接"""
    # 启动
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务（上传文件）
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常统一格式"""
    return error(exc.detail, code=exc.status_code, status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求参数校验失败统一格式"""
    detail = exc.errors()[0]["msg"] if exc.errors() else "请求参数错误"
    return error(detail, code=422, status_code=422)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """数据库异常统一格式"""
    return error("数据库操作失败", code=500, status_code=500)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """兜底异常处理"""
    return error("服务器内部错误", code=500, status_code=500)


# 路由注册
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(blog_router, prefix="/api", tags=["Blog"])
app.include_router(resources_router, prefix="/api", tags=["Resources"])
app.include_router(downloads_router, prefix="/api", tags=["Downloads"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(files_router, prefix="/api/files", tags=["Files"])


@app.get("/health", tags=["Health"])
async def health():
    """健康检查"""
    return {"status": "ok"}
