import heapq
import uuid
from collections import deque
from sqlalchemy.orm import Session
from app.models import models

def get_graph(db: Session, graph_id: int):
    return db.query(models.Graph).filter(models.Graph.graph_id == graph_id).first()

def _save_snapshot(db: Session, session_id: str, step_index: int, graph_id: int, 
                   phase_id: str, current_node: str, target_node: str, visited: list, 
                   distances: dict, pq: list, description: str,
                   traversed_edges: list = None, final_path_edges: list = None):
    """Lưu snapshot với traversed_edges và final_path_edges chuẩn hóa."""
    queue_state = [f"{dist}:{node}" for dist, node in pq] if pq else []
    
    step_data = {
        "phase_id": phase_id,
        "current_node": current_node,
        "target_node": target_node,
        "visited": visited.copy() if visited else [],
        "distances": distances.copy() if distances else {},
        "queue": queue_state,
        "traversed_edges": traversed_edges.copy() if traversed_edges else [],
        "final_path_edges": final_path_edges.copy() if final_path_edges else [],
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
def _get_node_ids(graph_data: dict) -> list[str]:
    """Extract node IDs from graph data (supports both dict and string formats)."""
    nodes_raw = graph_data.get("nodes", [])
    if nodes_raw and isinstance(nodes_raw[0], dict):
        return [str(n["id"]) for n in nodes_raw]
    return [str(n) for n in nodes_raw]

def _get_weight(edge: dict, default_weight: float = 1.0) -> float:
    """Extract weight from edge data (supports both flat and nested data formats)."""
    if "weight" in edge:
        return float(edge["weight"])
    data = edge.get("data", {})
    if isinstance(data, dict) and "weight" in data:
        return float(data["weight"])
    return default_weight

def run_dijkstra_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
        
    graph_data = graph.data_json
    nodes = _get_node_ids(graph_data)
    edges = graph_data.get("edges", [])
    
    if str(start_node) not in nodes: return {"error": "start_node không tồn tại trong đồ thị"}
        
    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="Dijkstra", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    adj = {node: [] for node in nodes}
    for edge in edges:
        u, v, w = str(edge["source"]), str(edge["target"]), _get_weight(edge)
        if u in adj: adj[u].append((v, w))

    INF = 1e18
    distances = {node: INF for node in nodes}
    distances[str(start_node)] = 0
    pq = [(0, str(start_node))]
    visited = []
    traversed_edges = []
    parent = {node: None for node in nodes}  # Truy vết đường đi
    step_index = 0
    
    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, pq, 
                   f"Khởi tạo hệ thống với start_node = {start_node}", traversed_edges)
    step_index += 1

    while pq:
        current_dist, current_node = heapq.heappop(pq)
        if current_node in visited: continue
        visited.append(current_node)
        
        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, pq, 
                       f"Chọn đỉnh {current_node} có khoảng cách nhỏ nhất ({current_dist})", traversed_edges)
        step_index += 1
        
        for neighbor, weight in adj.get(current_node, []):
            if neighbor in visited: continue
            new_dist = current_dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                parent[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))
                edge_id = f"{current_node}-{neighbor}"
                if edge_id not in traversed_edges:
                    traversed_edges.append(edge_id)
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, pq, 
                               f"Cập nhật khoảng cách đỉnh {neighbor} thành {new_dist}", traversed_edges)
                step_index += 1
                
    # Tính final_path_edges: đường đi ngắn nhất từ start đến mỗi node
    final_path_edges = []
    for node in nodes:
        if node != str(start_node) and distances[node] < INF:
            curr = node
            while parent[curr] is not None:
                edge = f"{parent[curr]}-{curr}"
                if edge not in final_path_edges:
                    final_path_edges.append(edge)
                curr = parent[curr]
    
    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, pq, 
                   "Thuật toán hoàn tất", traversed_edges, final_path_edges)
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 2. THUẬT TOÁN BFS
# ==========================================
def run_bfs_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = _get_node_ids(graph.data_json)
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
    distances = {node: INF for node in nodes}
    distances[str(start_node)] = 0
    queue = deque([(0, str(start_node))])
    visited = []
    traversed_edges = []
    parent = {node: None for node in nodes}
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, list(queue), 
                   f"Khởi tạo BFS từ đỉnh {start_node}", traversed_edges)
    step_index += 1

    while queue:
        current_depth, current_node = queue.popleft()
        if current_node in visited: continue
        visited.append(current_node)

        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, list(queue), 
                       f"Duyệt đỉnh {current_node} ở mức {current_depth}", traversed_edges)
        step_index += 1

        for neighbor in adj.get(current_node, []):
            if distances[neighbor] == INF:
                distances[neighbor] = current_depth + 1
                parent[neighbor] = current_node
                queue.append((distances[neighbor], neighbor))
                edge_id = f"{current_node}-{neighbor}"
                if edge_id not in traversed_edges:
                    traversed_edges.append(edge_id)
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, list(queue), 
                               f"Đưa đỉnh {neighbor} vào hàng đợi", traversed_edges)
                step_index += 1

    # Tính final_path_edges
    final_path_edges = []
    for node in nodes:
        if node != str(start_node) and distances[node] < INF:
            curr = node
            while parent[curr] is not None:
                edge = f"{parent[curr]}-{curr}"
                if edge not in final_path_edges:
                    final_path_edges.append(edge)
                curr = parent[curr]

    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, list(queue), 
                   "Hoàn tất BFS", traversed_edges, final_path_edges)
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 3. THUẬT TOÁN DFS
# ==========================================
def run_dfs_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = _get_node_ids(graph.data_json)
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
    traversed_edges = []
    parent = {node: None for node in nodes}
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, stack, 
                   f"Khởi tạo DFS từ đỉnh {start_node}", traversed_edges)
    step_index += 1

    while stack:
        current_depth, current_node = stack.pop()
        if current_node in visited: continue
        visited.append(current_node)

        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, stack, 
                       f"Duyệt sâu vào đỉnh {current_node}", traversed_edges)
        step_index += 1

        for neighbor in reversed(adj.get(current_node, [])):
            if neighbor not in visited:
                distances[neighbor] = current_depth + 1
                parent[neighbor] = current_node
                stack.append((distances[neighbor], neighbor))
                edge_id = f"{current_node}-{neighbor}"
                if edge_id not in traversed_edges:
                    traversed_edges.append(edge_id)
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, stack, 
                               f"Thêm {neighbor} vào ngăn xếp", traversed_edges)
                step_index += 1

    # Tính final_path_edges
    final_path_edges = []
    for node in nodes:
        if node != str(start_node) and distances[node] < INF:
            curr = node
            while parent[curr] is not None:
                edge = f"{parent[curr]}-{curr}"
                if edge not in final_path_edges:
                    final_path_edges.append(edge)
                curr = parent[curr]

    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, stack, 
                   "Hoàn tất DFS", traversed_edges, final_path_edges)
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 4. THUẬT TOÁN PRIM (TÌM CÂY KHUNG NHỎ NHẤT)
# ==========================================
def run_prim_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = _get_node_ids(graph.data_json)
    if str(start_node) not in nodes: return {"error": "start_node không tồn tại"}

    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="Prim", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    adj = {node: [] for node in nodes}
    for edge in graph.data_json.get("edges", []):
        u, v, w = str(edge["source"]), str(edge["target"]), _get_weight(edge)
        if u in adj: adj[u].append((v, w))
        if v in adj: adj[v].append((u, w)) 

    INF = 1e18
    distances = {node: INF for node in nodes}
    distances[str(start_node)] = 0
    pq = [(0, str(start_node))]
    visited = []
    traversed_edges = []
    parent = {node: None for node in nodes}
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited, distances, pq, 
                   f"Khởi tạo Prim từ đỉnh {start_node}", traversed_edges)
    step_index += 1

    while pq:
        current_weight, current_node = heapq.heappop(pq)
        if current_node in visited: continue
        visited.append(current_node)

        # Thêm cạnh từ parent vào MST
        if parent[current_node] is not None:
            edge_id = f"{parent[current_node]}-{current_node}"
            if edge_id not in traversed_edges:
                traversed_edges.append(edge_id)

        _save_snapshot(db, session_id, step_index, graph_id, "select", current_node, None, visited, distances, pq, 
                       f"Đưa đỉnh {current_node} vào cây khung MST", traversed_edges)
        step_index += 1

        for neighbor, weight in adj.get(current_node, []):
            if neighbor not in visited and weight < distances[neighbor]:
                distances[neighbor] = weight
                parent[neighbor] = current_node
                heapq.heappush(pq, (weight, neighbor))
                _save_snapshot(db, session_id, step_index, graph_id, "relax_success", current_node, neighbor, visited, distances, pq, 
                               f"Phát hiện cạnh nối đến {neighbor} tối ưu hơn (trọng số {weight})", traversed_edges)
                step_index += 1

    # final_path_edges = MST edges
    final_path_edges = traversed_edges.copy()

    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited, distances, pq, 
                   "Hoàn tất Prim MST", traversed_edges, final_path_edges)
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}

# ==========================================
# 5. THUẬT TOÁN KRUSKAL (TÌM CÂY KHUNG NHỎ NHẤT)
# ==========================================
def run_kruskal_and_capture(db: Session, graph_id: int, start_node: str):
    graph = get_graph(db, graph_id)
    if not graph: return {"error": "Không tìm thấy đồ thị"}
    nodes = _get_node_ids(graph.data_json)

    session_id = f"sess-{uuid.uuid4().hex[:8]}"
    db_session = models.AlgoSession(session_id=session_id, graph_id=graph_id, algo_name="Kruskal", start_node=str(start_node))
    db.add(db_session)
    db.commit()

    edges_list = []
    for edge in graph.data_json.get("edges", []):
        edges_list.append((_get_weight(edge), str(edge["source"]), str(edge["target"])))
    edges_list.sort()

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

    pq = [(w, f"{u}-{v}") for w, u, v in edges_list]
    visited_edges = []
    traversed_edges = []
    distances = {node: 1e18 for node in nodes}
    step_index = 0

    _save_snapshot(db, session_id, step_index, graph_id, "init", None, None, visited_edges, distances, pq, 
                   "Khởi tạo Kruskal, đã sắp xếp toàn bộ cạnh", traversed_edges)
    step_index += 1

    for weight, u, v in edges_list:
        _save_snapshot(db, session_id, step_index, graph_id, "select", u, v, visited_edges, distances, pq, 
                       f"Xét cạnh {u}-{v} (trọng số {weight})", traversed_edges)
        step_index += 1

        if union(u, v):
            visited_edges.append(f"{u}-{v}")
            edge_id = f"{u}-{v}"
            if edge_id not in traversed_edges:
                traversed_edges.append(edge_id)
            distances[v] = weight
            distances[u] = weight
            _save_snapshot(db, session_id, step_index, graph_id, "relax_success", u, v, visited_edges, distances, pq, 
                           f"Thêm cạnh {u}-{v} vào MST", traversed_edges)
            step_index += 1
            
            pq = [item for item in pq if item[1] != f"{u}-{v}"]

    final_path_edges = traversed_edges.copy()
    _save_snapshot(db, session_id, step_index, graph_id, "finish", None, None, visited_edges, distances, pq, 
                   "Hoàn tất Kruskal MST", traversed_edges, final_path_edges)
    db_session.total_steps = step_index + 1
    db.commit()
    return {"session_id": session_id, "total_steps": step_index + 1}