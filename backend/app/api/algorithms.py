import traceback
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Any
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import algorithms as service
from app.models import models

router = APIRouter()

class InitRequest(BaseModel):
    graph_id: int
    start_node: str
    algorithm: str = "Dijkstra"

class GraphCreateRequest(BaseModel):
    name: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]

@router.post("/graphs")
def create_graph(req: GraphCreateRequest, db: Session = Depends(get_db)):
    """Tạo đồ thị mới từ dữ liệu frontend gửi lên (dùng cho chức năng vẽ đồ thị)."""
    try:
        graph = models.Graph(
            name=req.name,
            data_json={"nodes": req.nodes, "edges": req.edges},
            is_template=False
        )
        db.add(graph)
        db.commit()
        db.refresh(graph)
        return {"graph_id": graph.graph_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/init")
def init_algorithm_session(req: InitRequest, db: Session = Depends(get_db)):
    # ✅ Thêm debug log
    print(f"📥 Frontend request: graph_id={req.graph_id}, start_node={req.start_node}, algorithm={req.algorithm}")
    
    try:
        algo = req.algorithm.lower()
        
        # 2. KHÚC RẼ NHÁNH ĐÃ ĐỦ 5 THUẬT TOÁN
        if algo == "dijkstra":
            result = service.run_dijkstra_and_capture(db, req.graph_id, req.start_node)
        elif algo == "bfs":
            result = service.run_bfs_and_capture(db, req.graph_id, req.start_node)
        elif algo == "dfs":
            result = service.run_dfs_and_capture(db, req.graph_id, req.start_node)
        elif algo == "prim":
            result = service.run_prim_and_capture(db, req.graph_id, req.start_node)
        elif algo == "kruskal":
            result = service.run_kruskal_and_capture(db, req.graph_id, req.start_node)
        else:
            # Nếu người dùng gửi lên 1 thuật toán tào lao không có trong hệ thống
            raise HTTPException(status_code=400, detail=f"Hệ thống chưa hỗ trợ thuật toán: {req.algorithm}")
        
        # 3. Kiểm tra xem quá trình chạy thuật toán có báo lỗi gì không (ví dụ: đỉnh bắt đầu không tồn tại)
        if "error" in result:
            print(f"⚠️ Service error: {result['error']}")  # ✅ Log error
            raise HTTPException(status_code=400, detail=result["error"])
            
        # 4. Trả về kết quả thành công cho Frontend
        print(f"✅ Success: session_id={result['session_id']}")  # ✅ Log success
        return {
            "session_id": result["session_id"],
            "total_steps": result["total_steps"],
            "algorithm": req.algorithm
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")

@router.get("/step/{session_id}")
def get_algorithm_step(session_id: str, step_index: int = Query(...), db: Session = Depends(get_db)):
    # Phần API lấy Snapshot này được GIỮ NGUYÊN 100%
    session = db.query(models.AlgoSession).filter(models.AlgoSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session_id không tồn tại")
        
    if step_index < 0 or step_index >= session.total_steps:
        raise HTTPException(status_code=404, detail=f"step_index ngoài phạm vi [0, {session.total_steps - 1}]")
        
    snapshot = db.query(models.ExecutionState).filter(
        models.ExecutionState.session_id == session_id,
        models.ExecutionState.step_index == step_index
    ).first()
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="Không tìm thấy bản ghi snapshot")
        
    return {
        "session_id": snapshot.session_id,
        "step_index": snapshot.step_index,
        "description": snapshot.description,
        "data": snapshot.step_data_json
    }