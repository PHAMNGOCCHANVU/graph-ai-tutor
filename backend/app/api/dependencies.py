from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer
from starlette.requests import Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import models
from app.services.auth import decode_token, get_user_by_id

security = HTTPBearer()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> models.User:
    """
    Dependency to get current authenticated user from JWT token.
    Raises 401 if token is invalid or expired.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_user_or_query(
    request: Request,
    token: str | None = Query(None, description="JWT token từ query parameter (cho SSE/EventSource)"),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Hàm phụ thuộc để lấy người dùng hiện tại từ JWT token.
    Hỗ trợ cả Authorization header (Bearer token) và query parameter.
    
    Ưu tiên:
    1. Authorization header (Bearer token) - ưu tiên hơn
    2. Query parameter (?token=...) - giải pháp thay thế cho EventSource/SSE
    
    Nếu token không hợp lệ hoặc hết hạn sẽ báo lỗi 401.
    """
    auth_token = None
    
    # Kiểm tra Authorization header trước tiên
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.split(" ")[1]
    # Nếu không có header, kiểm tra query parameter
    elif token:
        auth_token = token
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thiếu token xác thực",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Giải mã và xác thực token
    payload = decode_token(auth_token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    user = get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
