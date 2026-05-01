--------------------------------------------------------------------------------
algorithm: bfs
doc_type: qa_examples
language: vi
level: foundation
version: 1.0
intent_set: [why, how, edge_case, complexity]
source_scope: static_knowledge
--------------------------------------------------------------------------------

#### Mục tiêu tài liệu
Bộ câu hỏi này được viết để retrieve theo intent. Mỗi mục gồm: câu trả lời trực tiếp, ý nghĩa sư phạm, và cách nối với snapshot runtime.

#### QA-01
* intent_id: why_use_queue
* phase_id: dequeue_visit
* difficulty: basic
* related_terms: [queue, FIFO]
* question: Tại sao BFS lại sử dụng Hàng đợi (Queue) mà không phải Ngăn xếp (Stack)?
* direct_answer: Queue hoạt động theo nguyên lý FIFO (Vào trước ra trước). Điều này giúp thuật toán xử lý trọn vẹn tất cả các đỉnh ở mức hiện tại trước khi chuyển sang mức tiếp theo (tính chất loang rộng). Nếu dùng Stack, nó sẽ trở thành DFS.
* why_it_matters: Đây là nền tảng cốt lõi định hình hành vi và tên gọi của "Duyệt theo chiều rộng".
* tie_to_snapshot: Khi xem runtime, đỉnh được pop luôn là phần tử ở đầu mảng queue.

#### QA-02
* intent_id: why_mark_visited_on_push
* phase_id: explore_neighbors
* difficulty: intermediate
* related_terms: [visited[], queue]
* question: Tại sao lại đánh dấu visited ngay khi đưa đỉnh vào queue thay vì lúc lấy ra?
* direct_answer: Việc đánh dấu sớm khi đưa vào queue giúp tránh tình trạng một đỉnh bị các đỉnh kề khác nhau cùng nhìn thấy và đẩy vào queue nhiều lần, làm lãng phí bộ nhớ và thời gian.
* why_it_matters: Giúp tối ưu không gian bộ nhớ (Space Complexity) tránh việc Queue phình to bất thường trong đồ thị dày.
* tie_to_snapshot: Trạng thái visited của đỉnh kề lân cận được set thành `true` ngay lập tức cùng lúc với lệnh enqueue.

#### QA-03
* intent_id: how_level_calculated
* phase_id: explore_neighbors
* difficulty: basic
* related_terms: [level[], dist[]]
* question: Mức (level) của một đỉnh được tính như thế nào?
* direct_answer: Khi đỉnh kề `v` được khám phá từ `current_node`, mức của `v` được tính bằng mức của `current_node` cộng thêm 1 (công thức: `level[v] = level[u] + 1`).
* why_it_matters: BFS đảm bảo đây là số lượng cạnh ít nhất (khoảng cách ngắn nhất) từ nguồn đến `v` trên đồ thị không trọng số.
* tie_to_snapshot: Khi `neighbors` được duyệt, các key trong `level` object của JSON tăng lên +1 so với `current_node`.

#### QA-04
* intent_id: edge_case_disconnected
* phase_id: edge_case
* difficulty: basic
* related_terms: [visited[], disconnected_graph]
* question: Chuyện gì xảy ra nếu đồ thị không liên thông?
* direct_answer: BFS chỉ lan truyền được tới các đỉnh nằm cùng thành phần liên thông với đỉnh nguồn. Các đỉnh thuộc thành phần khác sẽ không bao giờ được đưa vào queue và mảng visited của chúng giữ nguyên giá trị false.
* why_it_matters: Dạy người học cách sử dụng vòng lặp ngoài gọi BFS nhiều lần nếu muốn duyệt/tìm các thành phần liên thông.
* tie_to_snapshot: Khi hàng đợi rỗng và thuật toán dừng, sẽ có những đỉnh trong mảng `visited` mang giá trị `false`.

#### Negative Examples (Để giảm retrieve sai)

##### NEG-01
* intent_id: negative_weighted_shortest_path
* phase_id: out_of_scope
* user_query: "Tại sao BFS của tôi tìm sai đường đi ngắn nhất khi các đường đi có chi phí khác nhau?"
* expected_behavior: Từ chối phân tích lỗi code BFS và giải thích rằng BFS KHÔNG hoạt động đúng trên đồ thị có trọng số khác nhau. Hướng người học sang thuật toán Dijkstra.
* must_not_retrieve: Các chunk giải thích việc BFS tìm đường đi ngắn nhất mà thiếu chữ "không trọng số".

##### NEG-02
* intent_id: negative_backtracking
* phase_id: out_of_scope
* user_query: "Làm sao để tôi quay lui (backtrack) trong BFS?"
* expected_behavior: Giải thích nhanh rằng BFS không dùng cơ chế đệ quy/quay lui như DFS. Đề xuất đổi sang DFS nếu bản chất bài toán là quay lui.
* must_not_retrieve: Các chunk liên quan đến `dequeue_visit` nhưng áp dụng tư duy gọi đệ quy.

#### Retrieval Evaluation Set (v1)
* EVAL-WHY: Tại sao lại cần Queue trong thuật toán này?
* EVAL-HOW: Mảng level thay đổi ra sao khi duyệt đỉnh kề?
* EVAL-EDGE: Làm sao biết đồ thị không liên thông sau khi chạy BFS?
