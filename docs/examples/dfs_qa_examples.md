--------------------------------------------------------------------------------
algorithm: dfs
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
* intent_id: why_use_stack_or_recursion
* phase_id: explore_deep
* difficulty: basic
* related_terms: [stack, LIFO, đệ quy]
* question: Tại sao DFS sử dụng Ngăn xếp (Stack) hoặc Đệ quy?
* direct_answer: Stack tuân theo nguyên lý LIFO (Vào sau ra trước). Điều này buộc thuật toán phải ưu tiên xử lý những đỉnh rẽ nhánh gần nhất vừa mới được phát hiện, do đó liên tục đào sâu thay vì tản ngang. Hệ thống đệ quy bản chất cũng sử dụng Call Stack của máy tính để làm việc này.
* why_it_matters: Đây là khác biệt cốt lõi sinh ra tên gọi "Theo chiều sâu" (Depth-First).
* tie_to_snapshot: Khi `next_target` được đưa vào `stack`, nó sẽ là đỉnh nằm ở đỉnh Stack và được pop ra ngay trong step kế tiếp.

#### QA-02
* intent_id: why_backtrack
* phase_id: backtrack
* difficulty: intermediate
* related_terms: [backtrack, ngõ cụt]
* question: Thuật toán làm gì khi chạm vào một đỉnh mà tất cả các đỉnh kề đều đã được thăm?
* direct_answer: Thuật toán sẽ thực hiện quá trình "quay lui" (backtrack). Nó lấy đỉnh hiện tại ra khỏi Ngăn xếp (hoặc thoát khỏi hàm đệ quy hiện tại) để lùi về đỉnh liền trước đó, nhằm tiếp tục kiểm tra các nhánh rẽ khác chưa được khám phá.
* why_it_matters: Dạy tư duy vét cạn (exhaustive search), đảm bảo không bỏ sót bất cứ đỉnh nào liên thông với nguồn.
* tie_to_snapshot: Chiều dài của mảng `stack` đột ngột giảm xuống (pop), `current_node` lùi về đỉnh nằm dưới.

#### QA-03
* intent_id: edge_case_cycles
* phase_id: visit_node
* difficulty: basic
* related_terms: [visited[], chu trình]
* question: Chuyện gì xảy ra nếu đồ thị có chu trình mà ta không dùng mảng visited?
* direct_answer: Thuật toán sẽ bị kẹt trong một vòng lặp vô hạn (Infinite Loop). Nó sẽ đi vòng quanh chu trình và liên tục đưa các đỉnh cũ vào Stack, dẫn đến tràn bộ nhớ (Stack Overflow). Mảng visited đóng vai trò là "chốt chặn" để ngắt mạch lặp này.
* why_it_matters: Bài học kinh điển về lập trình đồ thị và đệ quy.
* tie_to_snapshot: Ở phase explore_deep, đỉnh kề được bỏ qua nếu trạng thái `visited` của nó đã là `true`.

#### QA-04
* intent_id: how_path_is_formed
* phase_id: explore_deep
* difficulty: intermediate
* related_terms: [cây DFS, trace]
* question: Đường đi trong DFS có phải là đường ngắn nhất không?
* direct_answer: Không. Trái ngược với BFS, đường đi sinh ra bởi cây DFS có xu hướng đi sâu và dài ngoằng ngoèo nhất có thể. Nó chỉ đảm bảo có đường đi, chứ không tối ưu số lượng cạnh hay chi phí.
* why_it_matters: Giúp người học tránh việc dùng nhầm DFS vào các bài toán tìm đường ngắn nhất.
* tie_to_snapshot: Truy vết thông qua stack sẽ thấy hành trình tiến sâu xuống mà không tản đều theo các mức (levels) như BFS.

#### Negative Examples (Để giảm retrieve sai)

##### NEG-01
* intent_id: negative_shortest_path
* phase_id: out_of_scope
* user_query: "Làm sao để tôi sửa DFS lại cho nó tìm đường đi ngắn nhất như Dijkstra?"
* expected_behavior: Từ chối yêu cầu. Trả lời rằng DFS không được thiết kế để tìm đường ngắn nhất tối ưu cục bộ. Hãy khuyên người học chuyển sang dùng BFS (cho đồ thị không trọng số) hoặc Dijkstra (có trọng số).
* must_not_retrieve: Các chunk liên quan đến `explore_deep` mà thiếu cảnh báo về đường đi tối ưu.

##### NEG-02
* intent_id: negative_level_order
* phase_id: out_of_scope
* user_query: "Mảng level[] trong DFS được tính như thế nào?"
* expected_behavior: Đính chính rằng DFS thường không dùng mảng `level[]` vì nó không duyệt theo từng mức giống BFS. Khái niệm phù hợp trong DFS là `thời điểm bắt đầu thăm` (discovery time) hoặc `chiều sâu đệ quy` (depth).
* must_not_retrieve: Chunk nhầm lẫn kiến thức BFS.

#### Retrieval Evaluation Set (v1)
* EVAL-WHY: Tại sao bắt buộc phải đánh dấu đỉnh ngay khi thăm?
* EVAL-HOW: Cơ chế quay lui hoạt động ra sao khi dùng Ngăn xếp?
* EVAL-EDGE: Đồ thị có chu trình ảnh hưởng thế nào đến DFS?
