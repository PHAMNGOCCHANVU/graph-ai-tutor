--------------------------------------------------------------------------------
algorithm: kruskal
doc_type: glossary
language: vi
canonical_terms_version: 1.0
intent_tags: [terminology_alignment, style_guardrail, variable_mapping]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Tài liệu này chuẩn hóa cách gọi biến giữa runtime JSON và ngôn ngữ sư phạm để module orchestrator sinh câu trả lời nhất quán, tránh ảo giác (hallucination), đặc biệt là làm nổi bật cấu trúc Disjoint Set đặc trưng của Kruskal [2, 3].

#### Bảng ánh xạ thuật ngữ chính
##### Term 1
* runtime_name: edge_list & sorted_edges
* canonical_name: Danh sách cạnh
* learner_friendly_name: Danh sách cạnh đã sắp xếp
* aliases: [tập cạnh, mảng cạnh]
* forbidden_confusions: [danh sách kề, ma trận kề]
* mapping_rule: Nhấn mạnh đây là danh sách toàn cục chứa mọi cạnh, không bám theo đỉnh.
* phase_usage:
  * init: Đưa vào thuật toán sắp xếp [4].
  * pick_edge: Lần lượt bốc từng cạnh ra theo thứ tự.

##### Term 2
* runtime_name: disjoint_set (gồm parent/rank)
* canonical_name: Disjoint Set
* learner_friendly_name: Cấu trúc Disjoint Set (Union-Find)
* aliases: [tập hợp rời rạc, mảng đại diện, mảng cha]
* forbidden_confusions: [mảng visited[], mảng Free[], mảng Trace[]]
* mapping_rule: Ánh xạ 1:1 với cơ chế quản lý tập hợp đỉnh.
* phase_usage:
  * init: Mỗi đỉnh tự làm cha (gốc) của chính nó [2].
  * cycle_check_union: Dùng Find để tìm gốc, dùng Union để gộp gốc [3].

##### Term 3
* runtime_name: mst_edges
* canonical_name: MST Edges
* learner_friendly_name: Tập cạnh cây khung
* aliases: [cây khung, kết quả, bộ khung]
* forbidden_confusions: [đường đi ngắn nhất, shortest path]
* phase_usage:
  * cycle_check_union: Được push thêm cạnh nếu cạnh đó không tạo chu trình [2].

#### Response Style Rules cho Orchestrator
1. Ưu tiên sử dụng cách ví von sư phạm: Coi mỗi đỉnh ban đầu là một "quốc gia độc lập", các cạnh là các "đề xuất xây cầu", và Union-Find là cơ chế kiểm tra xem hai quốc gia đã "thông thương" với nhau chưa.
2. Tuyệt đối dùng thuật ngữ `Cấu trúc Disjoint Set` hoặc `Union-Find` khi giải thích bước chống chu trình [2].
3. Nhấn mạnh cụm từ `Tham lam` (Greedy) khi giải thích việc bốc cạnh rẻ nhất [4, 5].

#### Conflict Resolution Rules
* Nếu input prompt người dùng hỏi về `visited[]` hay `Trace[]`, AI PHẢI sửa lại cho đúng: "Kruskal không dùng mảng visited để duyệt đỉnh, mà dùng cấu trúc Disjoint Set để quản lý các tập hợp đỉnh liên thông" [2, 3].
* Nếu user thắc mắc "cạnh âm có làm sai Kruskal không", AI phải tự tin khẳng định là KHÔNG, giải thích rằng Kruskal chỉ quan tâm thứ tự sắp xếp chứ không cộng dồn trọng số để rẽ nhánh như Dijkstra.

#### Micro Explanations (Mẫu ngắn)
1. Mẫu cho phase init: "Khởi tạo, ta sắp xếp toàn bộ danh sách cạnh từ rẻ đến đắt, đồng thời thiết lập cấu trúc Disjoint Set sao cho mỗi đỉnh tự tạo thành một tập hợp rời rạc." [2, 4]
2. Mẫu cho phase pick_edge: "Rút cạnh có chi phí rẻ nhất tiếp theo ra khỏi danh sách đã sắp xếp để xét duyệt."
3. Mẫu cho phase cycle_check_union: "Sử dụng phép Find để xem hai đầu của cạnh đã thuộc cùng một tập hợp chưa. Vì chúng khác tập hợp (không tạo chu trình), ta kết nạp cạnh này vào cây khung và dùng phép Union gộp hai tập hợp lại." [2, 3]

#### Validation Checklist
* Câu trả lời có phân biệt rõ ràng Kruskal (xét cạnh) với Prim/Dijkstra (xét đỉnh) không?
* Thuật ngữ `Union-Find` hoặc `Disjoint Set` có được sử dụng đúng chỗ khi đề cập đến chu trình không?
* Có tuyệt đối tránh từ "đường đi ngắn nhất" không?

#### Anti-Hallucination Rules
1. KHÔNG tự bịa ra quá trình duyệt các đỉnh kề (như dùng danh sách kề). Kruskal thuần túy làm việc trên một danh sách cạnh tuyến tính [4, 9, 10].
2. KHÔNG giải thích vòng lặp kết thúc khi "đã thăm hết các đỉnh". Vòng lặp Kruskal kết thúc khi tập `mst_edges` thu thập đủ `N-1` cạnh hoặc đã duyệt hết mảng cạnh [4, 5].