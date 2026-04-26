---
algorithm: dijkstra
doc_type: theory
language: vi
level: foundation
version: 1.0
phase_coverage: [init, select, relax, heap_update]
intent_tags: [how_it_works, why, invariant, edge_case]
source_scope: static_knowledge
---

## Mục tiêu tài liệu

Tài liệu này mô tả lý thuyết nền của Dijkstra theo dạng có cấu trúc để module ingestion cắt chunk ổn định và module orchestrator map đúng với trạng thái runtime.

## Snapshot Mapping (theory <-> runtime)

- Thuật ngữ chuẩn trong giải thích:
	- `d[v]`: nhãn khoảng cách
	- `Free[v]`: trạng thái nhãn tự do hay đã cố định
	- `Heap`: hàng đợi ưu tiên
- Key runtime tương ứng từ snapshot JSON:
	- `dist[]` -> `d[]`
	- `visited[]` -> `Free[]` với quy ước `Free[v] = not visited[v]`
	- `priority_queue` -> `Heap`

## Phase 1: Initialization

- phase_id: `init`
- Goal: đặt cận trên ban đầu cho toàn bộ đỉnh.
- Input state keys: `source`, `nodes`.
- Trigger condition: bắt đầu chạy thuật toán tại step đầu tiên.
- Core update:
	- `d[source] = 0`
	- `d[v] = +infinity` với mọi `v != source`
	- `Free[v] = true` với mọi đỉnh
- Invariant: mọi `d[v]` đang là cận trên của khoảng cách ngắn nhất thật.
- Teaching hint: nhấn mạnh `+infinity` nghĩa là "chưa tìm thấy đường" chứ không phải lỗi dữ liệu.
- Common misconception: cho rằng đỉnh không phải source cần khởi tạo bằng 0.

Giải thích ngắn:
Khởi tạo đặt nền cho toàn bộ quá trình tối ưu. Khi `d[source] = 0` và các đỉnh khác là `+infinity`, thuật toán có một mốc chắc chắn để lan truyền thông tin đường đi tốt hơn ở các phase sau.

## Phase 2: Vertex Selection (fix label)

- phase_id: `select`
- Goal: chọn đỉnh tự do có nhãn nhỏ nhất để cố định.
- Input state keys: `dist[]`, `visited[]` hoặc `Free[]`, `priority_queue`.
- Trigger condition: sau init hoặc sau khi relax xong một vòng lặp.
- Core update:
	- lấy `u` có `d[u]` nhỏ nhất trong tập tự do
	- chuyển `u` sang trạng thái đã cố định
- Invariant: với trọng số không âm, `d[u]` sau khi cố định là tối ưu tuyệt đối.
- Teaching hint: giải thích vì sao điều kiện trọng số không âm là bắt buộc cho bước chốt nhãn.
- Common misconception: nghĩ rằng vẫn có thể giảm `d[u]` sau khi đã cố định.

Giải thích ngắn:
Do các cạnh không âm, mọi đường vòng để quay lại `u` đều không thể cho chi phí thấp hơn nhãn nhỏ nhất hiện có. Vì vậy chọn min rồi chốt là hợp lệ về mặt toán học.

## Phase 3: Edge Relaxation

- phase_id: `relax`
- Goal: thử cải thiện nhãn của các đỉnh kề.
- Input state keys: `current_node`, `dist[]`, `adjacency`, `visited[]`.
- Trigger condition: ngay sau khi một đỉnh `u` được cố định.
- Core update:
	- với mỗi đỉnh kề `v` còn tự do, cập nhật
	- `d[v] = min(d[v], d[u] + w(u, v))`
	- nếu giảm nhãn thành công thì cập nhật trace và độ ưu tiên trong heap
- Invariant: sau mỗi lần relax, cận trên của đỉnh bị ảnh hưởng không tăng.
- Teaching hint: liên hệ trực tiếp với Bellman optimality principle.
- Common misconception: relax là "xác nhận" kết quả cuối cùng cho `v`.

Giải thích ngắn:
Relaxation là cơ chế lan truyền đường đi tốt hơn. Nó không chốt nhãn cho mọi đỉnh, mà chỉ thử giảm chi phí tạm thời bằng cách đi qua đỉnh vừa cố định.

## Phase 4: Priority Queue Update

- phase_id: `heap_update`
- Goal: duy trì cấu trúc heap đúng sau khi một số nhãn thay đổi.
- Input state keys: `priority_queue`, `dist[]`.
- Trigger condition: một đỉnh `v` vừa giảm nhãn ở phase relax.
- Core update:
	- push lại cặp `(d[v], v)` hoặc decrease-key tùy cài đặt
	- đảm bảo phần tử ở đỉnh heap luôn có nhãn nhỏ nhất
- Invariant: thao tác lấy phần tử kế tiếp luôn trả về đỉnh tự do có nhãn nhỏ nhất.
- Teaching hint: phân biệt rõ heap tối ưu tốc độ, không thay đổi bản chất chứng minh đúng.
- Common misconception: heap làm thay đổi đáp án, không chỉ độ phức tạp.

Giải thích ngắn:
Heap giúp bước chọn đỉnh nhanh hơn, từ quét tuyến tính xuống logarit. Điều này đặc biệt hiệu quả trên đồ thị thưa nhưng không thay đổi logic cốt lõi của Dijkstra.

## Boundary và Failure Conditions

- Negative weight: Dijkstra không đảm bảo đúng khi tồn tại cạnh âm.
- Disconnected graph: một số đỉnh sẽ giữ `d[v] = +infinity` đến cuối.
- Early stop: nếu chỉ cần đường đi từ `s` tới `t`, có thể dừng khi `t` được cố định.

## Query Hints cho Retrieval

- intent `why`: ưu tiên chunk có `Invariant` và `Common misconception`.
- intent `how_it_works`: ưu tiên chunk có `Core update` và `Trigger condition`.
- intent `edge_case`: ưu tiên phần Boundary và Failure Conditions.

## Snapshot Examples theo Phase

### Example A - phase `init`

- use_case: bat dau mo phong tu dinh `A`
- snapshot_minimal:

```json
{
	"algorithm": "dijkstra",
	"phase_id": "init",
	"source": "A",
	"dist": {"A": 0, "B": 1e18, "C": 1e18},
	"visited": {"A": false, "B": false, "C": false},
	"priority_queue": [[0, "A"]]
}
```

- retrieval_focus: khai niem khoi tao nhan va y nghia `+infinity`.

### Example B - phase `select`

- use_case: chon dinh min tiep theo de co dinh nhan
- snapshot_minimal:

```json
{
	"algorithm": "dijkstra",
	"phase_id": "select",
	"current_node": "B",
	"dist": {"A": 0, "B": 3, "C": 7},
	"visited": {"A": true, "B": false, "C": false},
	"priority_queue": [[3, "B"], [7, "C"]]
}
```

- retrieval_focus: vi sao co the co dinh nhan cua `B`.

### Example C - phase `relax`

- use_case: thu cai thien nhan cua dinh ke
- snapshot_minimal:

```json
{
	"algorithm": "dijkstra",
	"phase_id": "relax",
	"current_node": "B",
	"neighbors": [{"to": "C", "weight": 2}],
	"dist_before": {"A": 0, "B": 3, "C": 8},
	"dist_after": {"A": 0, "B": 3, "C": 5},
	"trace_after": {"C": "B"}
}
```

- retrieval_focus: y nghia cong thuc min va tac dong len `trace`.

### Example D - phase `heap_update`

- use_case: cap nhat uu tien sau khi giam nhan
- snapshot_minimal:

```json
{
	"algorithm": "dijkstra",
	"phase_id": "heap_update",
	"updated_node": "C",
	"new_dist": 5,
	"priority_queue_before": [[8, "C"], [10, "D"]],
	"priority_queue_after": [[5, "C"], [10, "D"]]
}
```

- retrieval_focus: ly do phai re-heap de buoc select tiep theo dung.

## Coverage Matrix (intent x phase)

| intent | init | select | relax | heap_update | edge_case |
|---|---|---|---|---|---|
| why | yes | yes | yes | yes | yes |
| how_it_works | yes | yes | yes | yes | no |
| invariant | yes | yes | yes | yes | no |
| edge_case | no | no | no | no | yes |

## Gold Assertions cho Evaluation

1. Query ve trong so am phai truy xuat chunk co noi dung "Dijkstra khong dam bao dung voi canh am".
2. Query ve d[v] thay doi phai truy xuat chunk co cong thuc relax.
3. Query ve tie-break trong heap khong duoc lam thay doi ket qua cuoi cung.