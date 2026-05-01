--------------------------------------------------------------------------------
algorithm: dfs
doc_type: theory
language: vi
level: foundation
version: 1.0
phase_coverage: [init, visit_node, explore_deep, backtrack]
intent_tags: [how_it_works, why, invariant, edge_case]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này mô tả lý thuyết nền của Depth-First Search (DFS) theo dạng có cấu trúc để module ingestion cắt chunk ổn định và module orchestrator map đúng với trạng thái runtime.

#### Snapshot Mapping (theory <-> runtime)
* Thuật ngữ chuẩn trong giải thích:
  * `Ngăn xếp (Stack) / Đệ quy`: Cấu trúc dữ liệu lưu các đỉnh đang trong quá trình duyệt (LIFO) hoặc call stack của đệ quy.
  * `Trạng thái đã duyệt`: Đánh dấu đỉnh đã được thăm để không quay lại.
* Key runtime tương ứng từ snapshot JSON:
  * `stack` hoặc hệ thống đệ quy -> `Ngăn xếp / Đệ quy`
  * `visited[]` (hoặc `Free[]` trong một số tài liệu) -> `Trạng thái đã duyệt`

#### Phase 1: Initialization
* phase_id: init
* Goal: Khởi tạo các cấu trúc dữ liệu cơ bản và bắt đầu quá trình tìm kiếm từ đỉnh nguồn.
* Input state keys: source, nodes.
* Trigger condition: Bắt đầu chạy thuật toán.
* Core update:
  * `stack.push(source)` (nếu dùng vòng lặp) hoặc gọi `DFS(source)` (nếu dùng đệ quy).
  * Khởi tạo mảng `visited` với tất cả các giá trị là `false`.
* Invariant: Mọi đỉnh lúc khởi đầu đều ở trạng thái tự do (chưa duyệt).
* Teaching hint: Việc chọn cấu trúc Stack (Vào sau ra trước) quyết định tính chất "đi sâu" của DFS.
* Common misconception: Quên khởi tạo mảng `visited` dẫn đến lỗi chạy vô hạn nếu đồ thị có chu trình.
* Giải thích ngắn: Giai đoạn thiết lập để bắt đầu hành trình. Đỉnh xuất phát được đưa vào hệ thống ngăn xếp để chuẩn bị được thăm đầu tiên.

#### Phase 2: Visit Node
* phase_id: visit_node
* Goal: Xác nhận đỉnh hiện tại đang được xét và đánh dấu nó.
* Input state keys: current_node, visited[].
* Trigger condition: Khi một đỉnh vừa được lấy ra khỏi stack hoặc bắt đầu một thân hàm đệ quy mới.
* Core update:
  * `visited[current_node] = true`
* Invariant: Bất kỳ đỉnh nào đang được hàm DFS xử lý (hoặc vừa pop khỏi stack) đều mang trạng thái `visited = true`.
* Teaching hint: Đánh dấu là thao tác bắt buộc ngay khi thăm đỉnh để đảm bảo các nhánh khác không duyệt lại đỉnh này.
* Giải thích ngắn: "Thăm" đỉnh tức là ghi nhận sự hiện diện tại đó. Việc đánh dấu giúp thuật toán nhớ những nơi đã đi qua, giống như rải vụn bánh mì trong mê cung.

#### Phase 3: Explore Deep
* phase_id: explore_deep
* Goal: Tìm một đỉnh kề chưa được thăm để tiếp tục đi sâu xuống nhánh đó.
* Input state keys: current_node, adjacency, visited[], stack.
* Trigger condition: Ngay sau khi đánh dấu `current_node`, bắt đầu duyệt qua danh sách các đỉnh kề của nó.
* Core update:
  * Với một đỉnh kề `v` của `current_node`:
  * Nếu `visited[v] == false`:
    * Đưa `v` vào stack (hoặc gọi đệ quy `DFS(v)`).
    * (Tạm dừng việc xét các đỉnh kề còn lại của `current_node` cho đến khi `v` được duyệt xong - đây là điểm cốt lõi của "đi sâu").
* Invariant: Đường đi hiện tại từ gốc đến đỉnh đang xét luôn tạo thành một dải liên tục các đỉnh chưa từng lặp lại.
* Teaching hint: Nhấn mạnh tính chất "không xét ngay mọi đỉnh kề như BFS" mà "thấy đỉnh kề chưa thăm là đi theo nó đến cùng".
* Giải thích ngắn: Thay vì loang ra xung quanh, thuật toán chọn ngay một con đường mới và đi sâu nhất có thể cho đến khi chạm "ngõ cụt".

#### Phase 4: Backtrack
* phase_id: backtrack
* Goal: Rút lui (quay lui) về đỉnh trước đó khi đỉnh hiện tại không còn đỉnh kề nào chưa duyệt.
* Input state keys: current_node, stack.
* Trigger condition: Khi toàn bộ các đỉnh kề của `current_node` đều đã `visited == true`.
* Core update:
  * Hàm `DFS(current_node)` kết thúc, hoặc `stack.pop()` hoàn tất công việc với `current_node`.
  * Trở về xử lý tiếp đỉnh nằm dưới nó trong Stack (hoặc đỉnh gọi nó trong đệ quy).
* Invariant: Khi một đỉnh hoàn tất backtrack, mọi đỉnh thuộc nhánh con (subtree) của nó trong cây DFS đều đã được thăm xong.
* Teaching hint: Backtrack là cơ chế cốt lõi để thoát khỏi "ngõ cụt" và quay lại các ngã ba chưa khám phá hết.
* Giải thích ngắn: Khi không còn đường đi tiếp, thuật toán tự động lùi lại đỉnh liền trước để tìm kiếm các nhánh rẽ khác còn bỏ sót.

#### Boundary và Failure Conditions
* Đồ thị có chu trình (Cycles): Lỗi lặp vô hạn (Stack Overflow/Infinite Loop) nếu không sử dụng mảng `visited` để kiểm tra.
* Đồ thị thưa và sâu: Cấu trúc đệ quy có nguy cơ gây tràn bộ nhớ (Stack Overflow) do số lượng hàm gọi lồng nhau quá lớn. Khuyến nghị dùng Stack vòng lặp.
* Đồ thị không liên thông: Cần một vòng lặp bên ngoài bọc lấy DFS để đảm bảo duyệt mọi thành phần liên thông.

#### Query Hints cho Retrieval
* intent why: Ưu tiên chunk Invariant và Backtrack.
* intent how_it_works: Ưu tiên Core update của Explore Deep.
* intent edge_case: Ưu tiên Boundary conditions (chu trình).

#### Snapshot Examples theo Phase (JSON Mapping)
* Example A - phase init:
  `{"phase_id": "init", "current_node": null, "stack": [1], "visited": {}}`
* Example B - phase visit_node:
  `{"phase_id": "visit_node", "current_node": 1, "stack": [1], "visited": {"1": true}}`
* Example C - phase explore_deep:
  `{"phase_id": "explore_deep", "current_node": 1, "next_target": 2, "stack": [1, 2], "visited": {"1": true}}`
* Example D - phase backtrack:
  `{"phase_id": "backtrack", "current_node": 4, "stack": [1-3], "status": "no_unvisited_neighbors_left"}`
