--------------------------------------------------------------------------------
algorithm: bfs
doc_type: glossary
language: vi
canonical_terms_version: 1.0
intent_tags: [terminology_alignment, style_guardrail, variable_mapping]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này chuẩn hóa cách gọi biến giữa runtime JSON và ngôn ngữ sư phạm để module orchestrator sinh câu trả lời nhất quán, tránh ảo giác (hallucination) trong sinh văn bản.

#### Bảng ánh xạ thuật ngữ chính
##### Term 1
* runtime_name: queue
* canonical_name: Queue
* learner_friendly_name: Hàng đợi (Queue)
* aliases: [hàng đợi, danh sách chờ]
* forbidden_confusions: [ngăn xếp, stack, danh sách LIFO]
* mapping_rule: Ánh xạ 1:1, ưu tiên từ "hàng đợi" kèm tiếng Anh trong ngoặc.
* phase_usage:
  * init: thêm đỉnh khởi đầu.
  * dequeue_visit: lấy đỉnh ra để xét.
  * explore_neighbors: đẩy các đỉnh kề mới vào.

##### Term 2
* runtime_name: visited[]
* canonical_name: visited[]
* learner_friendly_name: Trạng thái đã duyệt
* aliases: [đã thăm, explored, marked]
* forbidden_confusions: [đã cố định nhãn như Dijkstra, Free[]]
* mapping_rule: Ánh xạ thành mảng đánh dấu các đỉnh đã/chưa vào Queue.
* phase_usage:
  * init: đánh dấu đỉnh nguồn là true.
  * explore_neighbors: kiểm tra và đổi thành true khi kết nạp lân cận.

##### Term 3
* runtime_name: level[] (hoặc dist[])
* canonical_name: level[]
* learner_friendly_name: Mức / Khoảng cách không trọng số
* aliases: [khoảng cách, số bước, số cạnh]
* forbidden_confusions: [tổng chi phí, nhãn trọng số]
* formula_anchor: `level[v] = level[u] + 1`
* phase_usage:
  * init: level của source bằng 0.
  * explore_neighbors: cập nhật level cho các đỉnh mới.

#### Response Style Rules cho Orchestrator
1. Trong câu trả lời cho người học, ưu tiên tên sư phạm: Hàng đợi (Queue), Trạng thái đã duyệt, Mức (level).
2. Khi cần nối với trạng thái runtime, nhắc thêm cặp ánh xạ một lần: "Hàng đợi (tương ứng với biến `queue`)...".
3. Nhấn mạnh từ khóa "Loang" (broadcasting/ripple effect) và "Theo từng mức" (level-by-level) để người học dễ hình dung bản chất BFS.

#### Conflict Resolution Rules
* Nếu input prompt người dùng hỏi về `dist[]` (có thể do quen miệng từ Dijkstra), AI phải tự động chuẩn hóa cách gọi thành `level[]` hoặc "Khoảng cách không trọng số" để phân định rõ ngữ cảnh BFS.
* Nếu user thắc mắc giữa duyệt kề trước/sau, luôn bám vào nguyên lý FIFO của mảng `queue`.

#### Micro Explanations (Mẫu ngắn)
1. Mẫu cho phase init: "Khởi tạo, ta đưa đỉnh xuất phát vào hàng đợi và đánh dấu đã duyệt để bắt đầu quá trình loang ra xung quanh."
2. Mẫu cho phase dequeue_visit: "Ta lấy đỉnh ở đầu hàng đợi ra (đỉnh được đưa vào sớm nhất) để xét các đỉnh kề của nó."
3. Mẫu cho phase explore_neighbors: "Kiểm tra các đỉnh kề, nếu chưa duyệt, ta đánh dấu ngay lập tức, gán mức bằng mức hiện tại cộng 1, và xếp hàng vào queue để chờ duyệt sau."

#### Validation Checklist
* Câu trả lời có nhầm lẫn BFS với DFS (Stack) hay Dijkstra (Priority Queue) không?
* Từ khóa `trọng số` (weight) có vô tình bị sử dụng khi giải thích khoảng cách không? Cần tuyệt đối cấm.
* Mọi giải thích cập nhật khoảng cách đều phải sử dụng thao tác cộng 1.

#### Anti-Hallucination Rules
1. Tuyệt đối KHÔNG giả định có mảng `trace[]` hoặc `parent[]` nếu runtime JSON snapshot chưa cung cấp mảng này. Chỉ giải thích về truy vết đường đi nếu user hỏi rõ hoặc snapshot có.
2. KHÔNG giải thích cơ chế rút đỉnh min theo độ ưu tiên. Queue của BFS chỉ pop phần tử index .
3. Nếu người dùng thắc mắc BFS có tìm được đường ngắn nhất không, AI PHẢI rào trước điều kiện: "Chỉ đúng khi trên đồ thị không có trọng số hoặc trọng số các cạnh đều bằng nhau".