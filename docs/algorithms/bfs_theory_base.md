--------------------------------------------------------------------------------
algorithm: bfs
doc_type: theory
language: vi
level: foundation
version: 1.0
phase_coverage: [init, dequeue_visit, explore_neighbors]
intent_tags: [how_it_works, why, invariant, edge_case]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này mô tả lý thuyết nền của Breadth-First Search (BFS) theo dạng có cấu trúc để module ingestion cắt chunk ổn định và module orchestrator map đúng với trạng thái runtime.

#### Snapshot Mapping (theory <-> runtime)
* Thuật ngữ chuẩn trong giải thích:
  * `Hàng đợi (Queue)`: Cấu trúc dữ liệu lưu các đỉnh chờ duyệt (FIFO).
  * `Trạng thái đã duyệt`: Đánh dấu đỉnh đã được đưa vào hàng đợi.
  * `Mức / Khoảng cách`: Khoảng cách không trọng số (số cạnh) từ đỉnh nguồn.
* Key runtime tương ứng từ snapshot JSON:
  * `queue` -> `Hàng đợi (Queue)`
  * `visited[]` -> `Trạng thái đã duyệt`
  * `level[]` / `dist[]` -> `Mức / Khoảng cách không trọng số`

#### Phase 1: Initialization
* phase_id: init
* Goal: Khởi tạo các cấu trúc dữ liệu cơ bản và đưa đỉnh xuất phát vào hàng đợi.
* Input state keys: source, nodes.
* Trigger condition: Bắt đầu chạy thuật toán tại step đầu tiên.
* Core update:
  * `queue.push(source)`
  * `visited[source] = true`
  * `level[source] = 0`
* Invariant: Hàng đợi không rỗng ở đầu thuật toán, đỉnh nguồn luôn có mức 0.
* Teaching hint: Nhấn mạnh việc đỉnh nguồn phải được đánh dấu `visited` ngay lúc khởi tạo để tránh việc nó bị thêm lại vào hàng đợi sau này.
* Common misconception: Quên khởi tạo mảng visited hoặc khởi tạo mức của nguồn là 1 thay vì 0.
* Giải thích ngắn: Việc khởi tạo nhằm thiết lập điểm neo ban đầu. Đỉnh nguồn được đưa vào hàng đợi và đánh dấu đã duyệt, đóng vai trò như điểm trung tâm để lan truyền theo từng mức (level).

#### Phase 2: Dequeue Visit
* phase_id: dequeue_visit
* Goal: Lấy một đỉnh ra khỏi hàng đợi để bắt đầu xét các đỉnh kề của nó.
* Input state keys: queue, current_node.
* Trigger condition: Khi hàng đợi không rỗng, bắt đầu một vòng lặp mới.
* Core update:
  * `current_node = queue.pop()`
* Invariant: Đỉnh được lấy ra luôn là đỉnh có `level` nhỏ nhất (gần nguồn nhất) trong số các đỉnh đang chờ.
* Teaching hint: Trọng tâm của BFS nằm ở tính chất FIFO (First-In-First-Out). Đỉnh nào vào hàng đợi trước sẽ được xét trước.
* Common misconception: Lấy nhầm phần tử cuối hàng đợi (nhầm với Stack trong DFS).
* Giải thích ngắn: Thuật toán tuân thủ nguyên tắc FIFO. Đỉnh được lấy ra khỏi hàng đợi chính là đỉnh đang được xét để loang ra các đỉnh lân cận ở mức tiếp theo.

#### Phase 3: Explore Neighbors
* phase_id: explore_neighbors
* Goal: Duyệt qua các đỉnh kề của `current_node`, đỉnh nào chưa duyệt thì đánh dấu và đưa vào hàng đợi.
* Input state keys: current_node, adjacency, visited[], level[], queue.
* Trigger condition: Ngay sau khi `current_node` được lấy ra từ hàng đợi.
* Core update:
  * Với mỗi đỉnh kề `v` của `current_node`:
  * Nếu `visited[v] == false`:
    * `visited[v] = true`
    * `level[v] = level[current_node] + 1`
    * `queue.push(v)`
* Invariant: Các đỉnh trong hàng đợi tại mọi thời điểm có độ chênh lệch mức tối đa không quá 1 (chỉ gồm các đỉnh ở mức `k` và `k+1`).
* Teaching hint: Nhấn mạnh tại sao phải đánh dấu `visited` ngay khi push vào Queue thay vì đợi khi pop ra. Điều này tránh việc 1 đỉnh bị push vào Queue nhiều lần.
* Common misconception: Đánh dấu `visited` sau khi pop đỉnh khỏi hàng đợi (dễ gây phình to Queue thừa thãi).
* Giải thích ngắn: Các đỉnh kề chưa duyệt được phát hiện sẽ ngay lập tức được kết nạp vào hàng đợi và ghi nhận mức (level). Hành động này giống như vết dầu loang, lan dần ra các đỉnh xa hơn một khoảng cách đều.

#### Boundary và Failure Conditions
* Đồ thị không liên thông (Disconnected graph): Từ đỉnh nguồn, BFS không thể chạm tới tất cả các đỉnh. Các đỉnh không thể tới sẽ giữ trạng thái `visited = false`.
* Đồ thị có chu trình (Cycles): Cần có mảng `visited` để tránh lặp vô hạn (infinite loop).
* Đồ thị có trọng số (Weighted graphs): BFS tiêu chuẩn KHÔNG đảm bảo đường đi ngắn nhất trên đồ thị có cạnh mang trọng số khác nhau.

#### Query Hints cho Retrieval
* intent why: Ưu tiên chunk có Invariant và Common misconception.
* intent how_it_works: Ưu tiên chunk có Core update và Trigger condition.
* intent edge_case: Ưu tiên phần Boundary và Failure Conditions.

#### Snapshot Examples theo Phase (JSON Mapping)
* Example A - phase init:
  `{"phase_id": "init", "current_node": null, "queue": [1], "visited": {"1": true}, "level": {"1": 0}}`
* Example B - phase dequeue_visit:
  `{"phase_id": "dequeue_visit", "current_node": 1, "queue": []}`
* Example C - phase explore_neighbors:
  `{"phase_id": "explore_neighbors", "current_node": 1, "neighbors_checked": [2, 3], "queue": [2, 3], "visited": {"1": true, "2": true, "3": true}, "level": {"1": 0, "2": 1, "3": 1}}`
