--------------------------------------------------------------------------------
algorithm: kruskal
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
* intent_id: why_sort_edges
* phase_id: init
* difficulty: basic
* related_terms: [sorted_edges, greedy]
* question: Tại sao Kruskal lại phải sắp xếp tất cả các cạnh ngay từ đầu?
* direct_answer: Việc sắp xếp theo trọng số tăng dần đảm bảo thuật toán luôn ưu tiên chọn những cạnh có chi phí rẻ nhất trước. Đây là bản chất của chiến lược tham lam (greedy) giúp xây dựng cây khung nhỏ nhất [4].
* why_it_matters: Đảm bảo tính tối ưu toàn cục. Nếu không sắp xếp, thuật toán có thể nhặt ngẫu nhiên các cạnh đắt tiền và phá hỏng kết quả.
* tie_to_snapshot: Mảng `sorted_edges` trong snapshot luôn thể hiện trọng số `w` tăng dần từ index 0.

#### QA-02
* intent_id: why_use_disjoint_set
* phase_id: cycle_check_union
* difficulty: intermediate
* related_terms: [disjoint_set, union, find, cycle]
* question: Tại sao thuật toán lại sử dụng cấu trúc Disjoint Set (Union-Find) thay vì DFS/BFS để kiểm tra chu trình?
* direct_answer: Sử dụng DFS/BFS để duyệt lại đồ thị mỗi lần thêm cạnh sẽ mất thời gian O(V+E). Cấu trúc Disjoint Set với hàm Find và Union cho phép kiểm tra hai đỉnh có thuộc cùng một tập hợp (cùng một cây) hay không chỉ trong thời gian gần như O(1) [2, 3].
* why_it_matters: Đây là chìa khóa giúp Kruskal đạt được hiệu năng cao O(E log E) trên đồ thị [6].
* tie_to_snapshot: Khi `action` là `skip_cycle`, gốc của `u` và `v` trong mảng `parent` của `disjoint_set` là giống hệt nhau.

#### QA-03
* intent_id: edge_case_disconnected
* phase_id: edge_case
* difficulty: basic
* related_terms: [mst_edges, disconnected]
* question: Thuật toán Kruskal xử lý đồ thị không liên thông như thế nào?
* direct_answer: Nếu đồ thị không liên thông, thuật toán sẽ cạn kiệt danh sách `sorted_edges` nhưng số lượng cạnh thu được trong `mst_edges` vẫn nhỏ hơn N-1. Lúc này, thuật toán sẽ dừng và kết luận không thể tạo thành Cây khung nhỏ nhất hoàn chỉnh [4, 5].
* why_it_matters: Dạy học viên cách kiểm tra tính liên thông của đồ thị sau khi chạy xong Kruskal.
* tie_to_snapshot: Khi kết thúc, length của `mst_edges` < N-1.

#### Negative Examples (Để giảm retrieve sai)

##### NEG-01
* intent_id: negative_negative_weights
* phase_id: out_of_scope
* user_query: "Đồ thị của tôi có trọng số âm, tôi phải đổi sang thuật toán nào vì Kruskal sẽ chạy sai giống Dijkstra?"
* expected_behavior: Khẳng định ngay với người dùng rằng Kruskal VẪN hoạt động hoàn toàn chính xác với trọng số âm. Kruskal chỉ dựa vào thao tác sắp xếp và cấu trúc tập hợp rời rạc, không bị ảnh hưởng bởi dấu của trọng số như thuật toán tìm đường ngắn nhất Dijkstra.
* must_not_retrieve: Các chunk liên quan đến lỗi trọng số âm của Dijkstra.

##### NEG-02
* intent_id: negative_shortest_path
* phase_id: out_of_scope
* user_query: "Thuật toán Kruskal tìm đường đi ngắn nhất từ đỉnh A đến đỉnh B như thế nào?"
* expected_behavior: Đính chính ngay lập tức sự nhầm lẫn của người học. Kruskal dùng để tìm Cây khung nhỏ nhất (Minimum Spanning Tree) kết nối TẤT CẢ các đỉnh với tổng chi phí nhỏ nhất, chứ KHÔNG phải tìm đường đi ngắn nhất giữa 2 đỉnh [1]. Gợi ý họ dùng Dijkstra hoặc Bellman-Ford [7, 8].
* must_not_retrieve: Bất kỳ chunk nào mô tả thao tác pick_edge mà ngầm xác nhận việc tìm đường đi.

#### Retrieval Evaluation Set (v1)
* EVAL-WHY: Tại sao bắt buộc phải dùng Union-Find thay vì mảng Visited thông thường?
* EVAL-HOW: Thao tác Union gộp hai tập hợp diễn ra như thế nào?
* EVAL-EDGE: Dấu hiệu nào cho thấy đồ thị không liên thông sau khi Kruskal chạy xong?