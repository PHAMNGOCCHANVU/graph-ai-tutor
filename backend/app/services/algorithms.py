from sqlalchemy.orm import Session
from app.models import models
import math
from app.services.algorithms import save_snapshot, get_graph 

def save_graph(db: Session, name: str, data: dict):
    db_graph = models.Graph(name=name, data_json=data)
    db.add(db_graph)
    db.commit()
    db.refresh(db_graph)
    return db_graph

def get_graph(db: Session, graph_id: int):
    return db.query(models.Graph).filter(models.Graph.graph_id == graph_id).first()

def save_snapshot(db: Session, graph_id: int, step_id: int, step_data: dict, explanation: str):
    new_state = models.ExecutionState(
        graph_id=graph_id,
        algo_step_id=step_id,
        step_data_json=step_data,
        explanation=explanation
    )
    db.add(new_state)
    db.commit()
    db.refresh(new_state)
    return new_state

def get_previous_state(db: Session, current_state_id: int, graph_id: int):
    """
    Logic phục vụ Back Step: Tìm snapshot có ID nhỏ hơn gần nhất của đồ thị này
    """
    return db.query(models.ExecutionState)\
             .filter(models.ExecutionState.graph_id == graph_id)\
             .filter(models.ExecutionState.state_id < current_state_id)\
             .order_by(models.ExecutionState.state_id.desc())\
             .first()


def run_dijkstra(db: Session, graph_id: int, start_node: str):
    """
    Thực thi thuật toán Dijkstra và lưu lại từng bước (Snapshot) vào Database
    """
    # 1. Lấy dữ liệu đồ thị từ DB
    graph = get_graph(db, graph_id)
    if not graph:
        return {"error": "Không tìm thấy đồ thị"}
    
    # Giả sử cấu trúc data_json của đồ thị lưu có dạng:
    # {"nodes": ["A", "B", "C"], "edges": [{"source": "A", "target": "B", "weight": 5}, ...]}
    graph_data = graph.data_json
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    # (Tùy chọn) Tìm hoặc tạo ID cho thuật toán Dijkstra trong bảng AlgorithmStep
    algo_step = db.query(models.AlgorithmStep).filter(models.AlgorithmStep.algo_name == "Dijkstra").first()
    algo_id = algo_step.algo_step_id if algo_step else 1

    # 2. KHỞI TẠO DIJKSTRA
    distances = {node: math.inf for node in nodes}
    distances[start_node] = 0
    visited = []
    
    # [LƯU SNAPSHOT BƯỚC 1] - Khởi tạo
    step_order = 1
    save_snapshot(
        db=db, 
        graph_id=graph_id, 
        step_id=algo_id, 
        step_data={"distances": distances, "visited": visited, "current_node": None}, 
        explanation=f"Khởi tạo khoảng cách từ đỉnh {start_node} là 0, các đỉnh khác là vô cực."
    )

    # 3. VÒNG LẶP DIJKSTRA CHÍNH
    unvisited_nodes = list(nodes)
    
    while unvisited_nodes:
        # Tìm đỉnh có khoảng cách nhỏ nhất
        current_node = min(unvisited_nodes, key=lambda node: distances[node])
        
        if distances[current_node] == math.inf:
            break # Các đỉnh còn lại không thể đi tới
            
        unvisited_nodes.remove(current_node)
        visited.append(current_node)
        
        # Cập nhật khoảng cách cho các đỉnh kề
        for edge in edges:
            if edge["source"] == current_node and edge["target"] in unvisited_nodes:
                new_dist = distances[current_node] + edge["weight"]
                if new_dist < distances[edge["target"]]:
                    distances[edge["target"]] = new_dist
        
        # [LƯU SNAPSHOT CÁC BƯỚC TIẾP THEO]
        step_order += 1
        save_snapshot(
            db=db, 
            graph_id=graph_id, 
            step_id=algo_id, 
            step_data={"distances": distances.copy(), "visited": visited.copy(), "current_node": current_node}, 
            explanation=f"Đang xét đỉnh {current_node}. Cập nhật lại khoảng cách các đỉnh kề."
        )

    return {"message": "Đã chạy xong Dijkstra và lưu toàn bộ Snapshot", "total_steps": step_order}