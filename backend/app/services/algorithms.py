import heapq
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import models

def get_graph(db: Session, graph_id: int):
    return db.query(models.Graph).filter(models.Graph.graph_id == graph_id).first()

def _save_snapshot(db: Session, session_id: str, step_index: int, graph_id: int, 
                   phase_id: str, current_node: str, visited: list, distances: dict, 
                   pq: list, description: str):
    """
    Hàm phụ trợ để đóng gói và lưu 1 Snapshot vào Database
    """
    # Ép kiểu queue theo đúng chuẩn hợp đồng (Contract): dist:node
    queue_state = [f"{dist}:{node}" for dist, node in pq]
    
    step_data = {
        "phase_id": phase_id,
        "current_node": current_node,
        "visited": visited.copy(),
        "distances": distances.copy(),
        "queue": queue_state
    }
    
    new_state = models.ExecutionState(
        session_id=session_id,
        step_index=step_index,
        graph_id=graph_id,
        step_data_json=step_data,
        description=description
    )
    db.add(new_state)
    return new_state

def run_dijkstra_and_capture(db: Session, graph_id: int, start_node: str):
    """
    Chạy thuật toán Dijkstra từ đầu đến cuối và lưu lại toàn bộ các bước vào Database.
    """
    graph = get_graph(db, graph_id)
    if not graph:
        return {"error": "Không tìm thấy đồ thị"}
        
    # 1. TẠO SESSION MỚI (Mỗi lần chạy là 1 session duy nhất)
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(
        session_id=session_id,
        graph_id=graph_id,
        algo_name="Dijkstra"
    )
    db.add(db_session)
    db.commit() # Lưu session trước để lấy khóa ngoại cho Snapshot

    # 2. XỬ LÝ DỮ LIỆU ĐẦU VÀO (Parse Graph JSON)
    graph_data = graph.data_json
    nodes = [str(n) for n in graph_data.get("nodes", [])]
    edges = graph_data.get("edges", [])
    
    # Tạo danh sách kề (Adjacency List)
    adj = {node: [] for node in nodes}
    for edge in edges:
        u, v, w = str(edge["source"]), str(edge["target"]), float(edge["weight"])
        if u in adj: adj[u].append((v, w))
        # Nếu đồ thị vô hướng, bạn có thể mở comment dòng dưới:
        # if v in adj: adj[v].append((u, w))

    # 3. KHỞI TẠO CÁC BIẾN CỦA DIJKSTRA
    INF = 1e18 # Chuẩn Infinity của hệ thống
    distances = {node: INF for node in nodes}
    distances[str(start_node)] = 0
    
    pq = [(0, str(start_node))] # Hàng đợi ưu tiên (Priority Queue)
    visited = []
    step_index = 0
    
    # [SNAPSHOT 0]: EVENT INIT
    _save_snapshot(db, session_id, step_index, graph_id, "init", None, visited, distances, pq, 
                   f"Khởi tạo hệ thống. Khoảng cách đỉnh bắt đầu ({start_node}) là 0, các đỉnh khác là vô cực.")
    step_index += 1

    # 4. VÒNG LẶP DIJKSTRA (Thực thi và bắt sự kiện)
    while pq:
        current_dist, current_node = heapq.heappop(pq)
        
        # Bỏ qua nếu đỉnh đã được chốt (fixed)
        if current_node in visited:
            continue
            
        visited.append(current_node)
        
        # [SNAPSHOT]: EVENT SELECT
        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, visited, distances, pq, 
                       f"Đỉnh {current_node} có khoảng cách nhỏ nhất ({current_dist}). Chọn làm đỉnh hiện tại và chốt khoảng cách.")
        step_index += 1
        
        # Duyệt các đỉnh kề để dãn cạnh (Relaxation)
        for neighbor, weight in adj.get(current_node, []):
            if neighbor in visited:
                continue
                
            new_dist = current_dist + weight
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
                
                # [SNAPSHOT]: EVENT RELAX SUCCESS
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, visited, distances, pq, 
                               f"Dãn cạnh thành công. Cập nhật khoảng cách đỉnh {neighbor} thành {new_dist} (đi qua {current_node}).")
                step_index += 1
                
    # 5. [SNAPSHOT CUỐI CÙNG]: EVENT FINISH
    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, visited, distances, pq, 
                   "Thuật toán Dijkstra hoàn tất. Đã tìm được đường đi ngắn nhất đến các đỉnh có thể tới.")
    
    # Cập nhật tổng số bước vào Session và Commit toàn bộ
    db_session.total_steps = step_index
    db.commit()
    
    return {"session_id": session_id, "total_steps": step_index}