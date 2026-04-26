from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import algorithms as service

router = APIRouter()

@router.post("/save-graph")
def create_graph(name: str, data: dict, db: Session = Depends(get_db)):
    return service.save_graph(db, name, data)

@router.get("/load-graph/{graph_id}")
def load_graph(graph_id: int, db: Session = Depends(get_db)):
    graph = service.get_graph(db, graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Không tìm thấy đồ thị")
    return graph

@router.post("/save-snapshot")
def save_snapshot(graph_id: int, step_id: int, step_data: dict, explanation: str, db: Session = Depends(get_db)):
    return service.save_snapshot(db, graph_id, step_id, step_data, explanation)

@router.get("/back-step/{current_state_id}/{graph_id}")
def back_step(current_state_id: int, graph_id: int, db: Session = Depends(get_db)):
    prev_state = service.get_previous_state(db, current_state_id, graph_id)
    if not prev_state:
        raise HTTPException(status_code=404, detail="Không có trạng thái trước đó")
    return prev_state


@router.post("/run-dijkstra")
def api_run_dijkstra(graph_id: int, start_node: str, db: Session = Depends(get_db)):
    """
    API để chạy thuật toán Dijkstra cho một đồ thị cụ thể
    """
    result = service.run_dijkstra(db, graph_id, start_node)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
        
    return result