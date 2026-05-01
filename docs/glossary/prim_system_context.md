--------------------------------------------------------------------------------
algorithm: prim
doc_type: glossary
language: vi
canonical_terms_version: 1.0
intent_tags: [terminology_alignment, style_guardrail, variable_mapping]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này chuẩn hóa các thuật ngữ hệ thống giữa runtime JSON và ngôn ngữ giải thích (sư phạm), áp đặt Guardrails để ngăn LLM sinh ảo giác (hallucination) và tránh nhầm lẫn "chí tử" với thuật toán Dijkstra.

#### Bảng ánh xạ thuật ngữ chính
##### Term 1
* runtime_name: mst_set[] (hoặc visited[])
* canonical_name: mst_set[]
* learner_friendly_name: Tập đỉnh đã thuộc cây khung
* aliases: [tập MST, các đỉnh đã kết nạp, visited]
* forbidden_confusions: [đỉnh tự do/cố định nhãn của Dijkstra]
* mapping_rule: Ánh xạ 1:1, ưu tiên diễn đạt "đỉnh đã nằm trong cây".
* phase_usage:
  * init: mọi đỉnh đều = false.
  * select_min: đỉnh rút từ Heap được đổi thành true.
  * update_keys: chỉ cập nhật cho các đỉnh kề có giá trị false.

##### Term 2
* runtime_name: key[]
* canonical_name: key[]
* learner_friendly_name: Trọng số cạnh nhỏ nhất kết nối vào cây
* aliases: [trọng số rẻ nhất, key value]
* forbidden_confusions: [nhãn khoảng cách, độ dài đường đi, d[], dist[]]
* formula_anchor: `key[v] = weight(u, v)` (KHÔNG CÓ PHÉP CỘNG)
* phase_usage:
  * init: key của đỉnh nguồn = 0, còn lại = +infinity.
  * update_keys: cập nhật xuống giá trị của cạnh trực tiếp rẻ hơn.

##### Term 3
* runtime_name: priority_queue
* canonical_name: Priority Queue
* learner_friendly_name: Hàng đợi ưu tiên (Min-Heap)
* aliases: [heap, min-heap, hàng đợi]
* forbidden_confusions: [ngăn xếp, stack, danh sách LIFO]
* phase_usage:
  * select_min: lấy đỉnh có key nhỏ nhất.
  * update_keys: điều chỉnh lại vị trí (decrease-key) khi key nhỏ đi.

#### Response Style Rules cho Orchestrator
1. Luôn sử dụng từ khóa "Kết nạp" (include/add) thay vì "Cố định nhãn" khi nói về bước đưa đỉnh vào `mst_set`.
2. Phải mô tả quá trình như việc "Cây đang dần mọc ra xung quanh" thay vì "Lan truyền đường đi".
3. Khi nhắc đến việc cập nhật mảng `key[]`, LUÔN LUÔN tường minh nhắc nhở rằng "Giá trị này chỉ là trọng số cạnh, không cộng dồn độ dài đường đi từ nguồn".

#### Conflict Resolution Rules
* Nếu user nhập từ khóa `dist[]` hoặc "khoảng cách" khi hỏi về Prim, AI phải lập tức sửa lại: "Trong Prim ta dùng mảng `key[]` để lưu trọng số cạnh gần nhất nối vào cây khung, không phải mảng lưu độ dài đường đi từ nguồn".
* Nếu user dùng từ `visited` (kế thừa từ BFS/DFS), hãy uyển chuyển gọi đó là "Tập đỉnh đã thuộc cây khung (tương ứng với biến `mst_set` hoặc `visited`)".

#### Micro Explanations (Mẫu ngắn)
1. Mẫu cho phase init: "Khởi tạo cây bằng một đỉnh bất kỳ với trọng số kết nối bằng 0, các đỉnh còn lại chưa có đường nối nên mang giá trị vô cực."
2. Mẫu cho phase select_min: "Tìm xung quanh rìa của cây khung, rút từ Hàng đợi ưu tiên ra đỉnh có chi phí kết nối vào cây là rẻ nhất để kết nạp nó."
3. Mẫu cho phase update_keys: "Với đỉnh vừa được kết nạp, ta nhìn sang các đỉnh kề chưa vào cây. Nếu rẽ qua đây tốn ít chi phí hơn các kỷ lục trước đó, ta cập nhật lại 'báo giá' (key) và chỉnh lại mức ưu tiên trong Heap."

#### Validation Checklist
* Câu trả lời có nhầm lẫn thuật toán Prim với Dijkstra không? (Lỗi phổ biến nhất).
* Các biến như `mst_set` và `key` có được giải thích ý nghĩa sư phạm rõ ràng chưa?
* Công thức giảm nhãn ở `update_keys` TUYỆT ĐỐI KHÔNG CÓ PHÉP CỘNG.

#### Anti-Hallucination Rules
1. KHÔNG được nhầm lẫn giữa Kruskal (chọn cạnh rẻ nhất đồ thị) với Prim (chọn đỉnh có cạnh rẻ nhất NỐI VÀO CÂY HIỆN TẠI). Nếu user thắc mắc, hãy chỉ ra điểm này.
2. KHÔNG khẳng định Prim tìm ra cây khung duy nhất. Nếu đồ thị có nhiều cạnh cùng trọng số, Prim có thể sinh ra một trong nhiều phiên bản MST khác nhau.
3. KHÔNG sử dụng khái niệm "ngõ cụt" hay "quay lui" (backtrack) của DFS.