--------------------------------------------------------------------------------
algorithm: prim
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
* intent_id: why_use_priority_queue
* phase_id: select_min
* difficulty: basic
* related_terms: [priority_queue, Heap, Min-Heap]
* question: Tại sao thuật toán Prim lại sử dụng Hàng đợi ưu tiên (Min-Heap)?
* direct_answer: Việc sử dụng Min-Heap giúp thuật toán lấy ra đỉnh có giá trị `key` (trọng số cạnh) nhỏ nhất một cách nhanh chóng (chỉ mất thời gian O(log V) thay vì duyệt mảng O(V)).
* why_it_matters: Tối ưu hóa thời gian chạy của thuật toán, đặc biệt trên các đồ thị thưa.
* tie_to_snapshot: Khi xem runtime, đỉnh được pop ra ở phase `select_min` luôn là đỉnh đứng đầu (gốc) của cấu trúc `priority_queue`.

#### QA-02
* intent_id: why_prim_differs_dijkstra
* phase_id: update_keys
* difficulty: intermediate
* related_terms: [key[], mst_set, Dijkstra]
* question: Mảng key[] trong Prim khác mảng dist[] trong Dijkstra ở chỗ nào?
* direct_answer: Mảng `dist[]` trong Dijkstra lưu TỔNG CHÍ PHÍ đường đi từ đỉnh nguồn đến đỉnh hiện tại. Ngược lại, mảng `key[]` trong Prim chỉ lưu TRỌNG SỐ CỦA DUY NHẤT MỘT CẠNH có chi phí nhỏ nhất nối từ một đỉnh bất kỳ trong cây khung ra đỉnh hiện tại.
* why_it_matters: Đây là điểm tử huyệt mà 90% sinh viên hay nhầm lẫn. Prim chỉ quan tâm nhặt cạnh rẻ nhất để nới rộng cây, Dijkstra quan tâm tích lũy độ dài đường đi.
* tie_to_snapshot: Ở phase `update_keys`, công thức gán là `key[v] = w(u,v)` chứ không hề có phép cộng dồn `key[v] = key[u] + w(u,v)`.

#### QA-03
* intent_id: why_check_mst_set
* phase_id: update_keys
* difficulty: basic
* related_terms: [mst_set, chu trình]
* question: Tại sao khi cập nhật key, ta phải kiểm tra điều kiện đỉnh đó chưa thuộc mst_set?
* direct_answer: Các đỉnh đã nằm trong `mst_set` là những đỉnh đã thuộc về cây khung và được tối ưu tuyệt đối. Nếu ta tiếp tục lấy các đỉnh này để cập nhật, ta sẽ tạo ra một chu trình (vòng lặp) và phá vỡ cấu trúc của Cây (Tree luôn không có chu trình).
* why_it_matters: Rèn tính tuân thủ định nghĩa Cây Khung Nhỏ Nhất.
* tie_to_snapshot: Hệ thống sẽ bỏ qua đỉnh lân cận nếu thuộc tính `mst_set` của nó đã mang giá trị `true`.

#### QA-04
* intent_id: edge_case_disconnected
* phase_id: edge_case
* difficulty: intermediate
* related_terms: [priority_queue, mst_set]
* question: Đồ thị không liên thông thì Prim hoạt động ra sao?
* direct_answer: Thuật toán sẽ rút cạn Hàng đợi ưu tiên (Heap rỗng) nhưng khi kiểm tra, số lượng đỉnh trong `mst_set` vẫn ít hơn tổng số lượng đỉnh ban đầu. Ta kết luận đồ thị không liên thông và không thể sinh ra cây khung nhỏ nhất hoàn chỉnh.
* why_it_matters: Dạy người học tư duy xử lý lỗi dữ liệu (Failure Condition) ở bài toán đồ thị.
* tie_to_snapshot: Ở bước cuối cùng, `priority_queue` = [], thuật toán dừng lại nhưng vẫn còn các đỉnh có `mst_set = false`.

#### Negative Examples (Để giảm retrieve sai)

##### NEG-01
* intent_id: negative_shortest_path
* phase_id: out_of_scope
* user_query: "Làm sao dùng Prim để tìm đường đi ngắn nhất từ A đến B?"
* expected_behavior: Cương quyết đính chính. Phải khẳng định Prim là thuật toán tìm Cây Khung Nhỏ Nhất (MST) kết nối tất cả các đỉnh, không phải thuật toán tìm đường đi ngắn nhất (Shortest Path). Hướng dẫn người dùng chuyển sang Dijkstra hoặc Bellman-Ford.
* must_not_retrieve: Các chunk giải thích việc tối ưu đường đi của Dijkstra.

##### NEG-02
* intent_id: negative_negative_weights
* phase_id: out_of_scope
* user_query: "Nếu đồ thị có cạnh âm, Prim sẽ bị lặp vô hạn và tính sai giống Dijkstra phải không?"
* expected_behavior: Phủ nhận giả định này. Nhấn mạnh rằng Prim VẪN CHẠY ĐÚNG và tối ưu với cạnh có trọng số âm, do Prim chỉ so sánh chọn cạnh rẻ nhất dựa trên mảng `mst_set` để kết nạp, không cộng dồn chi phí như Dijkstra nên không bao giờ đi lùi hay lặp vô hạn.
* must_not_retrieve: Các chunk giải thích giới hạn về trọng số âm của Dijkstra.

#### Retrieval Evaluation Set (v1)
* EVAL-WHY: Mảng key[] đại diện cho điều gì và khác gì với khoảng cách?
* EVAL-HOW: Trọng số của các đỉnh kề được cập nhật như thế nào khi một đỉnh mới vào cây?
* EVAL-EDGE: Dấu hiệu nhận biết đồ thị không liên thông khi Prim đang chạy?
