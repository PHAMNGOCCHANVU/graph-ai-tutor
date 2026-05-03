from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import algorithms
from app.api import rag
from app.db.session import engine
from app.models import models

# Tự động tạo bảng khi chạy app
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AGI Algorithm Backend")

# CORS: Cho phép frontend (localhost:3000) gọi API backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Thay thế tạm thời thành wildcard để test luồng
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nhúng router API vào hệ thống
app.include_router(algorithms.router, prefix="/api/v1", tags=["Algorithms"])
app.include_router(rag.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Hệ thống giải thuật AGI đang hoạt động"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)