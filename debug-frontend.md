Vấn đề 1. Kết quả 429 TooMayRequests ở Usage Google AI Studio
Vấn đề 2. Next tự động và UI không kịp load dữ liệu hiển thị lên đồ thị
Vấn đề 3. Luồng state step thuật toán với chat AI giải thích bước hiện tại đang đồng bộ nhau dẫn đến quá nhiều requests đến Google AI Studio nên cho chức năng AI Tutor là nâng cao và thêm phần giải thích mặc định giống như VisualAlgo.net 
Vấn đề 4. UI khi chạy thuật toán hiển thị timeout of 15000ms exceeded
Vấn đề 5. Thanh tìm kiếm không có thực hiện được
Vấn đề 6. Có thuật toán chạy, có thuật toán không chạy. Thuật toán Kruskal, Prim, Dijkstra cần trọng số cạnh nhưng chưa thấy ở đồ thị khởi tạo mặc định
Vấn đề 7. Khung chat AI đang làm có nhiều dòng dữ chat thì làm cả trang dài ra thay vì làm khung chat AI có thanh cuộn không làm cả trang dài ra
Vấn đề 8. Hình như có vấn đề giao tiếp giữa Frontend và Backend

Giải pháp ở Frontend: 
- UI đồ thị thuật toán mặc định nên thêm trọng số cạnh ở thuật toán Kruskal, Prim, Dijkstra để chạy
- Khung chat AI nên làm kiểu khung chat hiện đại ở các trình duyệt có thể thu vào khi không cần dùng và có thể click vào để mở
- Thêm giao diện hiển thị code từng bước và giải thích mặc định như VisualAlgo
- Nên xây dựng chat AI như tính nâng cao. Khi user mở khung chat AI sao đó click giải thích bước hiện tại mới giải thích mới thực hiện gửi request, không gửi request tự động.
- Kiểm tra xem kênh giao tiếp Frontend và Backend có vấn đề gì không? 

Giải pháp ở Backend: Kiểm tra là log khi run xem có vấn đề gì ở Backend không? 