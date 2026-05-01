--------------------------------------------------------------------------------
algorithm: dfs
doc_type: glossary
language: vi
canonical_terms_version: 1.0
intent_tags: [terminology_alignment, style_guardrail, variable_mapping]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này chuẩn hóa cách gọi biến giữa runtime JSON và ngôn ngữ sư phạm để module orchestrator sinh câu trả lời nhất quán, tránh ảo giác (hallucination) trong sinh văn bản, đặc biệt là duy trì giới tuyến rõ ràng giữa DFS và BFS.

#### Bảng ánh xạ thuật ngữ chính
##### Term 1
* runtime_name: stack (hoặc call_stack)
* canonical_name: Stack
* learner_friendly_name: Ngăn xếp / Đệ quy
* aliases: [ngăn xếp, chuỗi đệ quy, LIFO]
* forbidden_confusions: [hàng đợi, queue, FIFO, priority queue]
* mapping_rule: Ánh xạ 1:1, ưu tiên từ "Ngăn xếp" cho mô hình lặp, "Đệ quy" cho mô hình hàm.
* phase_usage:
  * init: Đưa đỉnh gốc vào.
  * explore_deep: Đẩy đỉnh kề mới vào đỉnh stack.
  * backtrack: Pop đỉnh hiện tại ra khỏi stack.

##### Term 2
* runtime_name: visited[]
* canonical_name: visited[]
* learner_friendly_name: Trạng thái đã duyệt
* aliases: [đã thăm, explored, marked, mảng Free[]]
* forbidden_confusions: [nhãn khoảng cách, d[]]
* mapping_rule: Khẳng định đỉnh đã được đẩy vào hàm xử lý.
* phase_usage:
  * visit_node: Đánh dấu thành true.
  * explore_deep: Kiểm tra điều kiện `visited == false` trước khi đi tiếp.

#### Response Style Rules cho Orchestrator
1. Ưu tiên sử dụng động từ mạnh về sự dịch chuyển: "Đi sâu xuống" (dive deep), "Chạm ngõ cụt" (dead-end), "Quay lui" (backtrack).
2. Khi giải thích runtime: Luôn dùng thuật ngữ "Ngăn xếp (Stack)" để giải thích tại sao đỉnh kề cuối cùng lại được ưu tiên móc ra đầu tiên.
3. Cấm nhầm lẫn tính chất: Không bao giờ được hứa hẹn DFS tìm được đường ngắn nhất, hoặc loang theo mức (level).

#### Conflict Resolution Rules
* Nếu input prompt người dùng dùng từ "hàng đợi" (queue) khi hỏi về DFS, AI PHẢI sửa lại cho đúng: "DFS sử dụng Ngăn xếp (Stack) hoặc Đệ quy, không dùng Hàng đợi".
* Nếu người dùng sử dụng thuật ngữ `Free[]` từ giáo trình của thầy Lê Minh Hoàng, AI ngầm hiểu đó chính là `visited[]` nhưng có trạng thái logic đảo ngược (`Free[v] = true` tức là chưa duyệt, `visited = false`). 

#### Micro Explanations (Mẫu ngắn)
1. Mẫu cho phase visit_node: "Ngay khi đặt chân đến đỉnh, ta đánh dấu trạng thái đã duyệt để đảm bảo sẽ không đi vòng tròn nếu đồ thị có chu trình."
2. Mẫu cho phase explore_deep: "Từ đỉnh này, ta tìm thấy một đỉnh kề chưa duyệt. Tạm gác lại các con đường khác, ta đi sâu ngay vào nhánh mới này."
3. Mẫu cho phase backtrack: "Bởi vì xung quanh đỉnh này không còn nơi nào chưa duyệt, thuật toán buộc phải quay lui (rút khỏi ngăn xếp) để lùi về ngã ba trước đó."

#### Validation Checklist
* Các thuật ngữ LIFO, Stack, Recursion có được sử dụng chính xác không?
* Có phân định rạch ròi cơ chế của DFS so với BFS (FIFO, Queue) không?
* Trong bước backtrack, thao tác "Lùi lại" có được giải thích mạch lạc không?

#### Anti-Hallucination Rules
1. Tuyệt đối KHÔNG giả định có trọng số (weights) trong bài toán duyệt DFS thông thường nếu snapshot JSON không có.
2. KHÔNG giải thích DFS theo chiều rộng. Cấm sử dụng từ "loang ra xung quanh".
3. Nếu người dùng thắc mắc về độ phức tạp, luôn bám sát lý thuyết nền: DFS có độ phức tạp thời gian là `O(V + E)` trên danh sách kề, giống hệt BFS, điểm khác biệt là cấu trúc dữ liệu lưu trữ trạng thái.