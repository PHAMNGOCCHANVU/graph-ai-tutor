--------------------------------------------------------------------------------
algorithm: prim
doc_type: theory
language: vi
level: foundation
version: 1.0
phase_coverage: [init, select_min, update_keys]
intent_tags: [how_it_works, why, invariant, edge_case]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này mô tả lý thuyết nền của thuật toán Prim theo dạng có cấu trúc để module ingestion cắt chunk ổn định và module orchestrator map đúng với trạng thái runtime, đặc biệt chú trọng việc phân biệt cơ chế chọn đỉnh của Prim so với Dijkstra.

#### Snapshot Mapping (theory <-> runtime)
* Thuật ngữ chuẩn trong giải thích:
  * `Tập đỉnh đã thuộc cây khung`: Tập hợp các đỉnh đã được kết nạp vào cây khung nhỏ nhất (MST).
  * `Trọng số cạnh nhỏ nhất kết nối vào cây`: Giá trị lưu chi phí rẻ nhất để nối một đỉnh bên ngoài vào một đỉnh bất kỳ đã có trong MST.
  * `Hàng đợi ưu tiên (Min-Heap)`: Cấu trúc dữ liệu lưu các đỉnh chưa thuộc MST, ưu tiên đỉnh có trọng số kết nối nhỏ nhất.
* Key runtime tương ứng từ snapshot JSON:
  * `mst_set[]` (hoặc `visited[]` tùy cài đặt) -> `Tập đỉnh đã thuộc cây khung`
  * `key[]` (hoặc `d[]` theo Lê Minh Hoàng) -> `Trọng số cạnh nhỏ nhất kết nối vào cây`
  * `priority_queue` -> `Hàng đợi ưu tiên (Min-Heap)`

#### Phase 1: Initialization
* phase_id: init
* Goal: Chọn đỉnh xuất phát, khởi tạo trọng số kết nối và đưa vào Heap.
* Input state keys: source, nodes.
* Trigger condition: Bắt đầu chạy thuật toán.
* Core update:
  * `key[start] = 0`
  * `key[v] = +infinity` với mọi đỉnh `v != start`
  * Đưa tất cả các đỉnh vào `priority_queue` (Min-Heap) dựa trên mảng `key`.
  * `mst_set[v] = false` với mọi đỉnh `v`.
* Invariant: Cây khung ban đầu rỗng, đỉnh xuất phát có chi phí kết nối bằng 0 để đảm bảo được rút ra đầu tiên.
* Teaching hint: Giải thích rõ `+infinity` ở đây mang ý nghĩa là "đỉnh này hiện chưa có cạnh nào nối thẳng vào các đỉnh trong cây khung".
* Common misconception: Nhầm lẫn `key[]` với khoảng cách đường đi. Phải nhắc nhở học viên `key[]` chỉ là trọng số của MỘT cạnh duy nhất nối vào cây.
* Giải thích ngắn: Thuật toán bắt đầu bằng cách chọn một đỉnh làm gốc của cây (chi phí 0). Các đỉnh khác bị coi là xa vô tận vì ta chưa khám phá ra đường nối nào tới chúng.

#### Phase 2: Select Min
* phase_id: select_min
* Goal: Chọn đỉnh gần cây khung nhất để kết nạp vào cây.
* Input state keys: priority_queue, mst_set.
* Trigger condition: Khi Heap không rỗng, bắt đầu một vòng lặp mới.
* Core update:
  * `u = priority_queue.pop()` (rút đỉnh có `key[u]` nhỏ nhất).
  * `mst_set[u] = true`
* Invariant: Đỉnh `u` được chọn luôn là đỉnh nằm ngoài MST có cạnh nối rẻ nhất tới một đỉnh bất kỳ đã nằm trong MST.
* Teaching hint: Đây là biểu hiện của nguyên lý tham lam (greedy) - luôn mở rộng cây bằng cách nhặt "trái ngọt" gần nhất.
* Giải thích ngắn: Thuật toán nhìn quanh rìa của cây khung hiện tại, tìm xem có đỉnh nào bên ngoài mà chi phí nối vào cây là rẻ nhất thì rút ra và "kết nạp" ngay đỉnh đó vào tập cây khung.

#### Phase 3: Update Keys
* phase_id: update_keys
* Goal: Dùng đỉnh `u` vừa kết nạp để cập nhật lại cơ hội kết nối cho các đỉnh kề xung quanh nó.
* Input state keys: u, adjacency, mst_set[], key[], priority_queue.
* Trigger condition: Ngay sau khi đỉnh `u` được đưa vào `mst_set`.
* Core update:
  * Với mỗi đỉnh kề `v` của `u`:
  * Nếu `mst_set[v] == false` VÀ `weight(u, v) < key[v]`:
    * `key[v] = weight(u, v)`
    * Cập nhật lại vị trí của `v` trong `priority_queue` (Decrease-Key / UpHeap).
* Invariant: Mảng `key[]` tại mọi thời điểm luôn lưu giữ trọng số của cạnh rẻ nhất từ tập đỉnh bên ngoài nối vào tập đỉnh `mst_set`.
* Teaching hint: Đối chiếu thẳng với Dijkstra để người học nhận ra sự khác biệt: Prim dùng `weight(u, v)` thay vì cộng dồn `d[u] + weight(u, v)` như Dijkstra [1].
* Giải thích ngắn: Khi cây khung vừa nới rộng thêm đỉnh `u`, ta dùng `u` làm đòn bẩy để xem xét các đỉnh lân cận. Nếu dùng cạnh nối thẳng từ `u` tới `v` mang lại một chi phí rẻ hơn so với các kỷ lục trước đó của `v`, ta sẽ cập nhật lại giá trị cho `v`.

#### Boundary và Failure Conditions
* Đồ thị không liên thông (Disconnected graph): Heap rỗng do không còn cạnh nối từ MST ra phần còn lại, nhưng vẫn còn đỉnh có `mst_set = false` (hoặc có `key = +infinity`). Thuật toán kết luận không thể tạo Cây khung hoàn chỉnh.
* Đồ thị có trọng số âm (Negative Weights): Prim VẪN chạy đúng và ra kết quả MST hoàn hảo, do cơ chế greedy trên cạnh chứ không cộng dồn đường đi.

#### Query Hints cho Retrieval
* intent why: Ưu tiên chunk có Invariant và phân biệt Prim vs Dijkstra.
* intent how_it_works: Ưu tiên chunk có Core update của update_keys.
* intent edge_case: Ưu tiên phần Đồ thị không liên thông.

#### Snapshot Examples theo Phase (JSON Mapping)
* Example A - phase init:
  `{"phase_id": "init", "priority_queue": [{"node":1,"key":0}, {"node":2,"key":999}], "mst_set": {"1":false, "2":false}, "key": {"1":0, "2":999}}`
* Example B - phase select_min:
  `{"phase_id": "select_min", "current_node": 1, "priority_queue": [{"node":2,"key":999}], "mst_set": {"1":true, "2":false}}`
* Example C - phase update_keys:
  `{"phase_id": "update_keys", "current_node": 1, "neighbors": [{"v":2, "w":5}], "action": "decrease_key", "priority_queue": [{"node":2,"key":5}], "key": {"1":0, "2":5}}`