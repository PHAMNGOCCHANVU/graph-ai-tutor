from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Thêm dòng này
from app.api import algorithms, auth
from app.db.session import engine
from app.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Graph AI Tutor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép mọi nguồn truy cập (để test)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các Router vào ứng dụng
app.include_router(algorithms.router, prefix="/api/v1/algorithms", tags=["Algorithms"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Server đang chạy!"}