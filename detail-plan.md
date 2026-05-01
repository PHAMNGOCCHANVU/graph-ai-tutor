### Module 1: Ingestion Pipeline (Xử lý tài liệu & Xây dựng VectorDB)

**Mục tiêu:** Chuyển hóa sách giáo trình, tài liệu lý thuyết thuật toán (PDF, Markdown) thành các vector ngữ nghĩa để AI có thể tra cứu chính xác.

**Tech Stack:** Python, LangChain / LlamaIndex, OpenAI Embeddings (hoặc BGE-M3 nếu muốn chạy local), ChromaDB.

**Kế hoạch thực thi (Task Breakdown):**
1.  **Data Extraction (Trích xuất):** Viết script dùng `PyPDF2` hoặc `Unstructured` để đọc text từ PDF và Markdown. Lọc bỏ các header/footer, số trang không cần thiết.
2.  **Chunking Strategy (Chia nhỏ dữ liệu):**
    * Tuyệt đối **không** chia cắt theo số lượng ký tự ngẫu nhiên (sẽ làm đứt gãy ngữ nghĩa).
    * Sử dụng `RecursiveCharacterTextSplitter` hoặc `MarkdownHeaderTextSplitter` để cắt theo từng chương, từng phần logic (VD: Cắt riêng mục "Định nghĩa Relaxation", "Cấu trúc Hàng đợi ưu tiên").
3.  **Embedding & Upsert:**
    * Tạo vector cho từng chunk dữ liệu.
    * Lưu vào ChromaDB. **Lưu ý:** Cần đính kèm `metadata` cho mỗi chunk (ví dụ: `{"algorithm": "Dijkstra", "topic": "Relaxation"}`) để sau này truy vấn chính xác hơn bằng metadata filtering.
4.  **Tự động hóa:** Đóng gói script thành `ingest.py` có thể chạy bằng command line: `python ingest.py --file dijkstra.pdf --algo dijkstra`.

---

### Module 2: Simulation Engine (Chạy thuật toán & Lưu vết vào SQL)

**Mục tiêu:** Tính toán sẵn toàn bộ vòng đời của thuật toán từ đầu đến cuối và lưu lại từng "khung hình" (Snapshot) vào Database.

**Tech Stack:** Python, SQLAlchemy / asyncpg, PostgreSQL (bắt buộc dùng kiểu dữ liệu `JSONB` cho trạng thái).

**Kế hoạch thực thi:**
1.  **Thiết kế Database Schema:**
    * Bảng `GraphSession`: `session_id`, `algorithm_name`, `graph_data` (lưu đồ thị gốc).
    * Bảng `StepSnapshot`: `id`, `session_id` (Foreign Key), `step_index`, `snapshot_data` (cột JSONB chứa toàn bộ trạng thái hàng đợi, khoảng cách, đỉnh đang xét), `action_description` (mô tả ngắn).
2.  **Xây dựng Algorithm Runner:**
    * Viết các class thuật toán (VD: `DijkstraRunner`).
    * Chèn logic "bắt trạng thái" vào vòng lặp `while/for` cốt lõi. Mỗi khi có sự kiện (lấy đỉnh khỏi queue, dãn cạnh), đóng gói dữ liệu mảng, object vào một dictionary và `append` vào danh sách kết quả.
3.  **Bulk Insert (Tối ưu hiệu năng):** Không insert từng dòng vào DB. Thuật toán chạy xong sẽ sinh ra mảng hàng trăm steps, sử dụng `bulk_insert` của SQLAlchemy để ghi vào PostgreSQL trong 1 transaction duy nhất.

---

### Module 3: Orchestrator (RAG API - Trái tim của hệ thống)

**Mục tiêu:** Cung cấp API nhận vào `step_id`, kết hợp dữ liệu cứng (SQL) và lý thuyết (VectorDB) để sinh ra lời giải thích từ LLM.

**Tech Stack:** FastAPI (hỗ trợ Async), LangChain, OpenAI API / Claude API.

**Kế hoạch thực thi:**
1.  **Xây dựng Endpoint:** `GET /api/explain/{session_id}?step_index=5`
2.  **Query SQL (Dữ liệu động):** Truy vấn `StepSnapshot` để lấy ra cấu trúc `snapshot_data` tại bước số 5 (Ví dụ: `{"current_node": "A", "distances": {"B": 5}}`).
3.  **Query VectorDB (Lý thuyết):**
    * Dựa vào `action_description` của bước 5, biến đổi thành câu query.
    * Gọi ChromaDB lấy ra top 2 chunks tài liệu liên quan nhất.
4.  **Prompt Engineering (Gom dữ liệu):** Xây dựng System Prompt với cấu trúc:
    * *Context 1 (Lý thuyết):* [Kết quả từ ChromaDB].
    * *Context 2 (Thực tế):* [Dữ liệu JSONB từ SQL].
    * *Nhiệm vụ:* "Là một gia sư, hãy giải thích ngắn gọn tại sao ở bước này thuật toán lại chọn đỉnh X và thay đổi khoảng cách, dựa vào hai bối cảnh trên".
5.  **Streaming Response:** Trả kết quả về Frontend dưới dạng `Server-Sent Events (SSE)` để tạo hiệu ứng chữ gõ ra từ từ (typing effect), giúp UI không bị đơ khi chờ LLM xử lý.

---

### Module 4: UI Engine (Điều hướng & Hiển thị)

**Mục tiêu:** Render đồ thị mượt mà, quản lý state điều hướng (Next/Back) và hiển thị lời giải thích AI.

**Tech Stack:** Next.js (React), React Flow (vẽ đồ thị), Zustand (quản lý state toàn cục), TailwindCSS.

**Kế hoạch thực thi:**
1.  **Graph Canvas:** Tích hợp `React Flow`. Map dữ liệu từ API thành danh sách `nodes` và `edges` của React Flow. Thiết lập các class CSS động (ví dụ: `node-visited`, `node-active`) dựa trên dữ liệu.
2.  **State Management (Zustand):**
    * Tạo store lưu `currentStepIndex`, `totalSteps`, `currentGraphState`.
    * Viết hàm `handleNext()` và `handleBack()` để tăng giảm Index.
3.  **Sync Logic (Đồng bộ UI & Backend):**
    * Dùng `useEffect` lắng nghe sự thay đổi của `currentStepIndex`.
    * Khi Index đổi, gọi API Module 3 (Orchestrator).
    * **Senior Tip (Debounce):** Nếu người dùng bấm "Next" liên tục 5 lần rất nhanh, không gọi API sinh giải thích 5 lần (tốn tiền API và lag). Dùng kỹ thuật `Debounce` (chờ người dùng dừng bấm 500ms mới gọi hàm fetch lời giải thích RAG), trong lúc đó đồ thị vẫn đổi màu bình thường nhờ dữ liệu Snapshot đã có sẵn.
4.  **AI Chatbox:** Parse dữ liệu streaming text trả về từ Backend. Sử dụng thư viện `react-markdown` để render các công thức toán học hoặc in đậm/in nghiêng nếu LLM trả về định dạng Markdown.

