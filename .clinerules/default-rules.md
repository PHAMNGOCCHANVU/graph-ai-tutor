# Anti-Looping & System Safety
- STRICT LIMIT: Chỉ được phép thử sửa một lỗi (bug) hoặc chạy lại một lệnh terminal lỗi tối đa 2 lần.
- Nếu thất bại sau 2 lần, BẮT BUỘC dừng lại và sử dụng công cụ hỏi người dùng (`ask_user`) để xin chỉ thị mới. Tuyệt đối không tự đoán mò.
- KHÔNG tự động viết hoặc thực thi các đoạn script có vòng lặp `while/for` trong terminal nếu không thiết lập sẵn timeout (thời gian ngắt tự động).
- Trước khi thực hiện thay đổi lớn hoặc cài đặt thư viện mới, phải liệt kê ngắn gọn các bước và chờ người dùng xác nhận (`approve`).