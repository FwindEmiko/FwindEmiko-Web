# 统一 API 响应格式
from typing import Any

from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "ok") -> dict[str, Any]:
    """成功响应"""
    return {"code": 0, "data": data, "message": message}


def error(message: str, code: int = 500, status_code: int = 200) -> JSONResponse:
    """错误响应，默认 HTTP 状态码 200 以符合统一格式"""
    return JSONResponse(
        status_code=status_code,
        content={"code": code, "data": None, "message": message},
    )
