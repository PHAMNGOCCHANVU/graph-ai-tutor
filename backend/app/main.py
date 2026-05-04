from fastapi import FastAPI
from app.api import algorithms, auth # Đã thêm auth ở đây
from app.db.session import engine
from app.models import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Graph AI Tutor API")

# Gắn các Router vào ứng dụng
app.include_router(algorithms.router, prefix="/api/v1/algorithms", tags=["Algorithms"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"]) # Gắn thêm Auth Router

@app.get("/")
def read_root():
    return {"message": "Server đang chạy"}