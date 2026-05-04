from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
import jwt

# Cấu hình khóa bí mật (Secret Key) để ký Token (Trong thực tế nên giấu vào file .env)
SECRET_KEY = "day_la_khoa_bi_mat_cua_nhom_cho_du_an_nay"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Token sẽ hết hạn sau 30 phút

# Khởi tạo bộ băm mật khẩu chuẩn bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """Hàm kiểm tra mật khẩu người dùng nhập có khớp với mật khẩu đã băm trong DB không"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """Hàm băm mật khẩu trước khi lưu vào DB"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Hàm tạo JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt