--------------------------------------------------------------------------------
algorithm: kruskal
doc_type: theory
language: vi
level: foundation
version: 1.0
phase_coverage: [init, pick_edge, cycle_check_union]
intent_tags: [how_it_works, why, invariant, edge_case]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này mô tả lý thuyết nền của thuật toán Kruskal theo dạng có cấu trúc để module ingestion cắt chunk ổn định và module orchestrator map đúng với trạng thái runtime khi giải quyết bài toán Cây khung nhỏ nhất (Minimum Spanning Tree - MST) [1].

#### Snapshot Mapping (theory <-> runtime)
* Thuật ngữ chuẩn trong giải thích:
  * `Danh sách cạnh`: Mảng hoặc danh sách chứa tất cả các cạnh ban đầu của đồ thị.
  * `Danh sách cạnh đã sắp xếp`: Danh sách các cạnh được sắp xếp theo thứ tự trọng số tăng dần.
  * `Cấu trúc Disjoint Set (Union-Find)`: Cấu trúc tập hợp rời rạc dùng để kiểm tra chu trình và gộp các đỉnh [2, 3].
  * `Tập cạnh cây khung`: Tập hợp các cạnh tối ưu đã được kết nạp vào cây khung nhỏ nhất [4].
* Key runtime tương ứng từ snapshot JSON:
  * `edge_list` -> `Danh sách cạnh`
  * `sorted_edges` -> `Danh sách cạnh đã sắp xếp`
  * `disjoint_set` (gồm `parent` và `rank` hoặc `count`) -> `Cấu trúc Disjoint Set (Union-Find)`
  * `mst_edges` -> `Tập cạnh cây khung`

#### Phase 1: Initialization
* phase_id: init
* Goal: Chuẩn bị dữ liệu bằng cách sắp xếp các cạnh theo trọng số tăng dần và khởi tạo mỗi đỉnh là một tập hợp rời rạc [4].
* Input state keys: nodes, edge_list.
* Trigger condition: Bắt đầu chạy thuật toán.
* Core update:
  * `sorted_edges = sort(edge_list) by weight ascending`
  * `disjoint_set.parent[v] = v` (hoặc `-1`) với mọi đỉnh `v` [3].
  * `mst_edges = []`
* Invariant: Mọi đỉnh lúc khởi đầu đều là gốc của một cây độc lập chứa duy nhất chính nó [2].
* Teaching hint: Việc sắp xếp cạnh đảm bảo nguyên lý tham lam (greedy): luôn ưu tiên xem xét các cạnh rẻ nhất trước [4, 5].
* Common misconception: Quên khởi tạo cấu trúc Disjoint Set dẫn đến lỗi khi gộp các đỉnh sau này.
* Giải thích ngắn: Đây là bước chuẩn bị. Thuật toán gom tất cả các cạnh mang đi sắp xếp từ rẻ đến đắt, đồng thời coi mỗi đỉnh là một quốc gia độc lập chưa có đường giao thương nào.

#### Phase 2: Pick Edge
* phase_id: pick_edge
* Goal: Lấy ra cạnh có trọng số nhỏ nhất tiếp theo để kiểm tra [4].
* Input state keys: sorted_edges, current_edge_index.
* Trigger condition: Khi `mst_edges` chưa đủ `N-1` cạnh và `sorted_edges` vẫn còn cạnh [4, 5].
* Core update:
  * `current_edge = sorted_edges[current_edge_index]`
  * `current_edge_index++`
* Invariant: Cạnh được chọn luôn là cạnh có trọng số nhỏ nhất trong số các cạnh chưa được xét.
* Teaching hint: Nhấn mạnh tính tham lam của Kruskal: thuật toán duyệt mù quáng theo danh sách đã sắp xếp.
* Giải thích ngắn: Thuật toán nhặt ra cạnh rẻ nhất chưa được kiểm tra để xem xét liệu có nên dùng nó để xây đường nối hay không.

#### Phase 3: Cycle Check & Union
* phase_id: cycle_check_union
* Goal: Dùng Disjoint Set để kiểm tra xem việc kết nạp cạnh hiện tại có tạo thành chu trình không. Nếu không, gộp hai tập hợp và thêm cạnh vào MST [2-4].
* Input state keys: current_edge (u, v, weight), disjoint_set, mst_edges.
* Trigger condition: Ngay sau khi nhặt `current_edge` từ danh sách.
* Core update:
  * `root_u = Find(u)`
  * `root_v = Find(v)`
  * `If root_u != root_v`: (Không tạo chu trình)
    * `Union(root_u, root_v)`
    * `mst_edges.push(current_edge)`
  * `Else`: Bỏ qua cạnh (chống chu trình) [2].
* Invariant: Tập `mst_edges` tại mọi thời điểm luôn là một rừng (forest) không có chu trình [2].
* Teaching hint: Trọng tâm thuật toán nằm ở đây. Find để tìm gốc (đại diện quốc gia), nếu hai đỉnh khác gốc tức là chưa liên thông, có thể nối lại bằng thao tác Union.
* Common misconception: Duyệt mảng `visited[]` kiểu DFS/BFS để kiểm tra chu trình (điều này làm thuật toán cực kỳ chậm, Kruskal phải dùng Disjoint Set) [2, 3].
* Giải thích ngắn: Thuật toán kiểm tra xem hai đầu của cạnh có thuộc cùng một cụm hay chưa. Nếu đã cùng cụm, việc nối thêm sẽ tạo thành vòng tròn (chu trình) thừa thãi nên bị vứt bỏ. Nếu khác cụm, ta nối chúng lại và kết nạp cạnh này vào kết quả.

#### Boundary và Failure Conditions
* Đồ thị không liên thông (Disconnected Graph): Thuật toán sẽ duyệt hết danh sách `sorted_edges` nhưng số lượng cạnh trong `mst_edges` vẫn nhỏ hơn `N-1`. Cần báo lỗi không thể tạo Cây khung hoàn chỉnh [4, 5].
* Đồ thị có trọng số âm (Negative Weights): Kruskal VẪN chạy đúng. Đây là điểm khác biệt lớn so với Dijkstra.

#### Query Hints cho Retrieval
* intent why: Ưu tiên chunk có Invariant và thao tác Union-Find [2, 3].
* intent how_it_works: Ưu tiên chunk có Core update của Cycle Check & Union.
* intent edge_case: Ưu tiên phần Boundary (Đồ thị không liên thông) [5].

#### Snapshot Examples theo Phase (JSON Mapping)
* Example A - phase init:
  `{"phase_id": "init", "sorted_edges": [{"u":2,"v":3,"w":1}, {"u":1,"v":2,"w":4}], "disjoint_set": {"parent": {"1":1, "2":2, "3":3}}, "mst_edges": []}`
* Example B - phase pick_edge:
  `{"phase_id": "pick_edge", "current_edge": {"u":2,"v":3,"w":1}, "mst_edges": []}`
* Example C - phase cycle_check_union (thành công):
  `{"phase_id": "cycle_check_union", "current_edge": {"u":2,"v":3,"w":1}, "action": "union", "disjoint_set": {"parent": {"1":1, "2":2, "3":2}}, "mst_edges": [{"u":2,"v":3,"w":1}]}`
* Example D - phase cycle_check_union (bỏ qua do chu trình):
  `{"phase_id": "cycle_check_union", "current_edge": {"u":1,"v":3,"w":5}, "action": "skip_cycle", "disjoint_set": {"parent": {"1":2, "2":2, "3":2}}, "mst_edges": [{"u":2,"v":3,"w":1}, {"u":1,"v":2,"w":4}]}`