Khi chuyển từ Google AI Studio sang **OpenRouter**, bạn **không cần đổi sang model khác** (vẫn dùng được Gemini LLM và Gemini Embedding), nhưng bạn **phải thay đổi cách cấu hình trong code**.

Việc này không đơn giản là "thay mỗi key là xong" mà cần điều chỉnh 3 yếu tố sau:

### 1. Thay đổi SDK/Thư viện
Google AI Studio dùng thư viện riêng (`google-generativeai`). OpenRouter thì sử dụng chuẩn của **OpenAI**. 
* **Nếu đang dùng thư viện của Google:** Bạn phải chuyển sang dùng thư viện `openai` (Python/JS) hoặc gọi qua thư viện của OpenRouter.

### 2. Cấu hình Endpoint (Base URL)
Bạn phải trỏ code của mình về server của OpenRouter thay vì Google:
* **Base URL:** `https://openrouter.ai/api/v1`

### 3. Cấu hình Model ID
Tên model trên OpenRouter cần có thêm tiền tố của nhà cung cấp (`google/`):
* **LLM:** Chuyển từ `gemini-1.5-pro` thành `google/gemini-pro-1.5` (hoặc bản mới nhất có sẵn).
* **Embedding:** Chuyển từ `text-embedding-004` thành `google/gemini-embedding-001` (hoặc các bản tương đương mà OpenRouter hỗ trợ).

---

### Bảng so sánh cấu hình

| Thành phần | Google AI Studio (Free) | OpenRouter (Paid) |
| :--- | :--- | :--- |
| **API Key** | Lấy từ Google AI Studio | Lấy từ OpenRouter.ai |
| **Base URL** | Mặc định của SDK Google | `https://openrouter.ai/api/v1` |
| **Model ID** | `gemini-1.5-flash` | `google/gemini-flash-1.5` |
| **Embedding** | `text-embedding-004` | `google/gemini-embedding-2-preview` |

