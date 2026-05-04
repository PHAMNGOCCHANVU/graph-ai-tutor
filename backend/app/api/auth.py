from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import User
from app.core import security

router = APIRouter()

# --- SCHEMAS (Định nghĩa dữ liệu đầu vào/ra) ---
class UserAuth(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- API ENDPOINTS ---

@router.post("/register", response_model=Token)
def register(user_in: UserAuth, db: Session = Depends(get_db)):
    """API Đăng ký tài khoản mới"""
    # 1. Kiểm tra xem username đã có ai lấy chưa
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(status_code=400, detail="Tên đăng nhập đã tồn tại")
        
    # 2. Mã hóa mật khẩu và lưu vào Database
    hashed_pw = security.get_password_hash(user_in.password)
    new_user = User(username=user_in.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    
    # 3. Đăng ký xong thì cấp luôn thẻ Token cho người dùng
    access_token = security.create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user_in: UserAuth, db: Session = Depends(get_db)):
    """API Đăng nhập"""
    # 1. Tìm user trong Database
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Sai tên đăng nhập hoặc mật khẩu")
        
    # 2. Đối chiếu mật khẩu
    if not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Sai tên đăng nhập hoặc mật khẩu")
        
    # 3. Đúng mật khẩu -> Cấp thẻ Token
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}