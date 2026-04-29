import heapq
import uuid
from collections import deque
from sqlalchemy.orm import Session
from app.models import models

def get_graph(db: Session, graph_id: int):
    return db.query(models.Graph).filter(models.Graph.graph_id == graph_id).first()

def _save_snapshot(db: Session, session_id: str, step_index: int, graph_id: int, 
                   phase_id: str, current_node: str, target_node: str, visited: list, 
                   distances: dict, pq: list, description: str):
    # Hàm này gánh còng lưng cả 5 thuật toán, format hàng đợi chuẩn "dist:node"
    queue_state = [f"{dist}:{node}" for dist, node in pq]
    
    step_data = {
        "phase_id": phase_id,
        "current_node": current_node,
        "target_node": target_node,
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

# ==========================================
# 1. THUẬT TOÁN DIJKSTRA
# ==========================================
def run_dijkstra_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
        
    graph_data = graph.data_json
    nodes = [str(n) for n in graph_data.get("nodes", [])]
    edges = graph_data.get("edges", [])
    
    if str(start_node) not in nodes: return {"error": "start_node không tồn tại trong đồ thị"}
        
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="Dijkstra", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    adj = {node: [] for node in nodes}
    for edge in edges:
        u, v, w = str(edge["source"]), str(edge["target"]), float(edge["weight"])
        if u in adj: adj[u].append((v, w))

    INF = 1e18
    distances = {node: INF for node in nodes}
    distances[str(start_node)] = 0
    pq = [(0, str(start_node))]
    visited = []
    step_index = 0
    
    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, pq, f"Khởi tạo hệ thống với start_node = {start_node}")
    step_index += 1

    while pq:
        current_dist, current_node = heapq.heappop(pq)
        if current_node in visited: continue
        visited.append(current_node)
        
        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, pq, f"Chọn đỉnh {current_node} có khoảng cách nhỏ nhất ({current_dist})")
        step_index += 1
        
        for neighbor, weight in adj.get(current_node, []):
            if neighbor in visited: continue
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, pq, f"Cập nhật khoảng cách đỉnh {neighbor} thành {new_dist}")
                step_index += 1
                
    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, pq, "Thuật toán hoàn tất")
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 2. THUẬT TOÁN BFS
# ==========================================
def run_bfs_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = [str(n) for n in graph.data_json.get("nodes", [])]
    if str(start_node) not in nodes: return {"error": "start_node không tồn tại"}

    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="BFS", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    adj = {node: [] for node in nodes}
    for edge in graph.data_json.get("edges", []):
        u, v = str(edge["source"]), str(edge["target"])
        if u in adj: adj[u].append(v)

    INF = 1e18
    distances = {node: INF for node in nodes} # Dùng distances lưu chiều sâu
    distances[str(start_node)] = 0
    queue = deque([(0, str(start_node))])
    visited = []
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, list(queue), f"Khởi tạo BFS từ đỉnh {start_node}")
    step_index += 1

    while queue:
        current_depth, current_node = queue.popleft()
        if current_node in visited: continue
        visited.append(current_node)

        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, list(queue), f"Duyệt đỉnh {current_node} ở mức {current_depth}")
        step_index += 1

        for neighbor in adj.get(current_node, []):
            if distances[neighbor] == INF:
                distances[neighbor] = current_depth + 1
                queue.append((distances[neighbor], neighbor))
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, list(queue), f"Đưa đỉnh {neighbor} vào hàng đợi")
                step_index += 1

    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, list(queue), "Hoàn tất BFS")
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 3. THUẬT TOÁN DFS
# ==========================================
def run_dfs_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = [str(n) for n in graph.data_json.get("nodes", [])]
    if str(start_node) not in nodes: return {"error": "start_node không tồn tại"}

    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="DFS", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    adj = {node: [] for node in nodes}
    for edge in graph.data_json.get("edges", []):
        u, v = str(edge["source"]), str(edge["target"])
        if u in adj: adj[u].append(v)

    INF = 1e18
    distances = {node: INF for node in nodes}
    distances[str(start_node)] = 0
    stack = [(0, str(start_node))]
    visited = []
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, stack, f"Khởi tạo DFS từ đỉnh {start_node}")
    step_index += 1

    while stack:
        current_depth, current_node = stack.pop()
        if current_node in visited: continue
        visited.append(current_node)

        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, stack, f"Duyệt sâu vào đỉnh {current_node}")
        step_index += 1

        for neighbor in reversed(adj.get(current_node, [])):
            if neighbor not in visited:
                distances[neighbor] = current_depth + 1
                stack.append((distances[neighbor], neighbor))
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, stack, f"Thêm {neighbor} vào ngăn xếp")
                step_index += 1

    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, stack, "Hoàn tất DFS")
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 4. THUẬT TOÁN PRIM (TÌM CÂY KHUNG NHỎ NHẤT)
# ==========================================
def run_prim_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = [str(n) for n in graph.data_json.get("nodes", [])]
    if str(start_node) not in nodes: return {"error": "start_node không tồn tại"}

    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="Prim", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    # Prim yêu cầu đồ thị vô hướng
    adj = {node: [] for node in nodes}
    for edge in graph.data_json.get("edges", []):
        u, v, w = str(edge["source"]), str(edge["target"]), float(edge["weight"])
        if u in adj: adj[u].append((v, w))
        if v in adj: adj[v].append((u, w)) 

    INF = 1e18
    distances = {node: INF for node in nodes} # Lưu trọng số cạnh nhỏ nhất nối vào MST
    distances[str(start_node)] = 0
    pq = [(0, str(start_node))]
    visited = []
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, pq, f"Khởi tạo Prim từ đỉnh {start_node}")
    step_index += 1

    while pq:
        current_weight, current_node = heapq.heappop(pq)
        if current_node in visited: continue
        visited.append(current_node)

        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, pq, f"Đưa đỉnh {current_node} vào cây khung MST")
        step_index += 1

        for neighbor, weight in adj.get(current_node, []):
            if neighbor not in visited and weight < distances[neighbor]:
                distances[neighbor] = weight
                heapq.heappush(pq, (weight, neighbor))
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, pq, f"Phát hiện cạnh nối đến {neighbor} tối ưu hơn (trọng số {weight})")
                step_index += 1

    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, pq, "Hoàn tất Prim MST")
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 5. THUẬT TOÁN KRUSKAL (TÌM CÂY KHUNG NHỎ NHẤT)
# ==========================================
def run_kruskal_and_capture(db: Session, graph_id: int, start_node: str):
    # Kruskal duyệt toàn cục, start_node chỉ để đồng bộ API
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = [str(n) for n in graph.data_json.get("nodes", [])]

    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="Kruskal", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    edges_list = []
    for edge in graph.data_json.get("edges", []):
        edges_list.append((float(edge["weight"]), str(edge["source"]), str(edge["target"])))
    edges_list.sort() # Kruskal bắt buộc sắp xếp cạnh theo trọng số tăng dần

    # Cấu trúc Disjoint Set Union (DSU) để chống tạo vòng (cycle)
    parent = {node: node for node in nodes}
    def find(i):
        if parent[i] == i: return i
        parent[i] = find(parent[i])
        return parent[i]
    
    def union(i, j):
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    # Ép kiểu danh sách cạnh thành format của _save_snapshot (weight, "u-v")
    pq = [(w, f"{u}-{v}") for w, u, v in edges_list]
    visited_edges = [] # Lưu các cạnh đã chọn vào MST
    distances = {node: 1e18 for node in nodes}
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited_edges, distances, pq, "Khởi tạo Kruskal, đã sắp xếp toàn bộ cạnh")
    step_index += 1

    for weight, u, v in edges_list:
        _save_snapshot(db, session_id, step_index, graph_id, "select", u, v, visited_edges, distances, pq, f"Xét cạnh {u}-{v} (trọng số {weight})")
        step_index += 1

        if union(u, v): # Nếu gộp thành công (không tạo vòng)
            visited_edges.append(f"{u}-{v}")
            distances[v] = weight # Ghi nhận trọng số
            distances[u] = weight
            _save_snapshot(db, session_id, step_index, graph_id, "relax_success", u, v, visited_edges, distances, pq, f"Thêm cạnh {u}-{v} vào MST")
            step_index += 1
            
            # Loại bỏ cạnh đã xét ra khỏi danh sách chờ (pq)
            pq = [item for item in pq if item[1] != f"{u}-{v}"]

    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited_edges, distances, pq, "Hoàn tất Kruskal MST")
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}