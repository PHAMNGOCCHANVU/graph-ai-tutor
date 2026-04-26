from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import algorithms as service
from app.models import models

router = APIRouter()

# --- SCHEMAS (Chuẩn hóa dữ liệu đầu vào/ra) ---
class InitRequest(BaseModel):
    graph_id: int
    start_node: str
    algorithm: str = "Dijkstra" # Mặc định

# --- API ENDPOINTS ---

@router.post("/init")
def init_algorithm_session(req: InitRequest, db: Session = Depends(get_db)):
    """
    [API 1]: Khởi tạo phiên chạy thuật toán (Pre-computation).
    Backend sẽ chạy 1 mạch từ đầu đến cuối và lưu toàn bộ Snapshot vào Database.
    """
    # Gọi hàm thực thi Dijkstra từ service
    result = service.run_dijkstra_and_capture(db, req.graph_id, req.start_node)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
        
    # Trả về chuẩn Contract: session_id, total_steps, algorithm
    return {
        "session_id": result["session_id"],
        "total_steps": result["total_steps"],
        "algorithm": req.algorithm
    }

@router.get("/step/{session_id}")
def get_algorithm_step(session_id: str, step_index: int = Query(..., description="Vị trí bước cần lấy (Bắt đầu từ 0)"), db: Session = Depends(get_db)):
    """
    [API 2]: Lấy chính xác 1 Snapshot dựa vào session_id và step_index để phục vụ tính năng Next/Back.
    """
    # 1. Kiểm tra session có tồn tại không (Nếu không -> 404)
    session = db.query(models.AlgoSession).filter(models.AlgoSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session_id không tồn tại")
        
    # 2. Kiểm tra step_index có nằm trong phạm vi không (Nếu không -> 404)
    if step_index < 0 or step_index >= session.total_steps:
        raise HTTPException(status_code=404, detail=f"Step_index ngoài phạm vi. Tổng số bước là {session.total_steps}")
        
    # 3. Truy vấn Snapshot tương ứng
    snapshot = db.query(models.ExecutionState).filter(
        models.ExecutionState.session_id == session_id,
        models.ExecutionState.step_index == step_index
    ).first()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="Không tìm thấy dữ liệu Snapshot tại bước này")
        
    return {
        "session_id": snapshot.session_id,
        "step_index": snapshot.step_index,
        "description": snapshot.description,
        "data": snapshot.step_data_json
    }