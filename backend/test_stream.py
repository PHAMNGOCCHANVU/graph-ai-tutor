import requests
import json

# Thay thế bằng một session_id có thật từ log backend của bạn
# Ví dụ lấy request gần nhất từ log: sess-8cb83d67, step_index: 4
SESSION_ID = "sess-8cb83d67" 
STEP_INDEX = 4
BASE_URL = f"http://127.0.0.1:8000/api/v1/rag/explain/{SESSION_ID}/stream?step_index={STEP_INDEX}"

def debug_stream():
    print(f"🔗 Đang kết nối trực tiếp đến: {BASE_URL}")
    try:
        # Stream=True giúp đọc dữ liệu SSE từng luồng
        with requests.get(BASE_URL, stream=True, timeout=10) as response:
            print(f"📦 Status Code: {response.status_code}")
            print(f"📋 Headers: {json.dumps(dict(response.headers), indent=2)}\n")
            
            print("⏳ Đang lắng nghe luồng sự kiện (SSE)...")
            # iter_lines() tách các block SSE
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"⬅️ Nhận: {decoded_line}")
                    
        print("\n✅ Kết nối stream đã đóng bình thường.")            
    except Exception as e:
        print(f"\n❌ LỖI KẾT NỐI: {str(e)}")

if __name__ == "__main__":
    debug_stream()