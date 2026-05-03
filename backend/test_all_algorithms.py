"""
Test script toàn diện cho Module 3 - Test tất cả thuật toán
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
GRAPH_ID = 1  # Graph ID: dijkstra_eval (có 3 node A, B, C)

algorithms = ["Dijkstra", "BFS", "DFS", "Prim", "Kruskal"]
results = {}

print("=" * 70)
print("TEST MODULE 3 - TẤT CẢ CÁC THUẬT TOÁN")
print("=" * 70)

for algo in algorithms:
    print(f"\n{'=' * 70}")
    print(f"[TEST] Thuật toán: {algo}")
    print(f"{'=' * 70}")
    
    try:
        # 1. Gọi endpoint /init
        print(f"\n  1️⃣ Gọi POST /api/v1/init (graph_id={GRAPH_ID}, algorithm={algo})...")
        response = requests.post(
            f"{BASE_URL}/init",
            json={
                "graph_id": GRAPH_ID,
                "start_node": "A",
                "algorithm": algo
            },
            timeout=15
        )
        
        if response.status_code != 200:
            print(f"     ❌ Lỗi: {response.status_code}")
            print(f"     Response: {response.text}")
            results[algo] = {"status": "FAIL", "error": response.text}
            continue
        
        data = response.json()
        session_id = data["session_id"]
        total_steps = data["total_steps"]
        
        print(f"     ✅ Thành công")
        print(f"     Session ID: {session_id}")
        print(f"     Total steps: {total_steps}")
        
        # 2. Gọi endpoint /step/0 (lấy snapshot của bước 0)
        print(f"\n  2️⃣ Gọi GET /api/v1/step/{session_id}?step_index=0...")
        step_response = requests.get(
            f"{BASE_URL}/step/{session_id}?step_index=0",
            timeout=10
        )
        
        if step_response.status_code == 200:
            step_data = step_response.json()
            print(f"     ✅ Thành công")
            print(f"     Description: {step_data.get('description', 'N/A')}")
            print(f"     Data: {json.dumps(step_data.get('data', {}), indent=8)[:200]}...")
        else:
            print(f"     ⚠️ Cảnh báo: {step_response.status_code}")
        
        # 3. Gọi endpoint RAG /explain/step
        print(f"\n  3️⃣ Gọi GET /api/v1/rag/explain/{session_id}?step_index=0...")
        rag_response = requests.get(
            f"{BASE_URL}/rag/explain/{session_id}?step_index=0",
            timeout=30
        )
        
        if rag_response.status_code == 200:
            rag_data = rag_response.json()
            print(f"     ✅ Thành công")
            print(f"     Algorithm: {rag_data.get('algorithm', 'N/A')}")
            print(f"     Description: {rag_data.get('description', 'N/A')}")
            
            answer = rag_data.get('answer', 'N/A')
            if len(answer) > 200:
                print(f"     AI Answer: {answer[:200]}...")
            else:
                print(f"     AI Answer: {answer}")
            
            theory_chunks = rag_data.get('theory_chunks', [])
            print(f"     Theory chunks retrieved: {len(theory_chunks)}")
        else:
            print(f"     ❌ Lỗi: {rag_response.status_code}")
            print(f"     Response: {rag_response.text[:200]}")
        
        # 4. Test streaming endpoint
        print(f"\n  4️⃣ Gọi GET /api/v1/rag/explain/{session_id}/stream?step_index=0 (SSE)...")
        try:
            stream_response = requests.get(
                f"{BASE_URL}/rag/explain/{session_id}/stream?step_index=0",
                stream=True,
                timeout=30
            )
            
            if stream_response.status_code == 200:
                print(f"     ✅ Streaming thành công")
                events_count = 0
                text_chunks = []
                
                for line in stream_response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if line.startswith("data: "):
                        events_count += 1
                        data_str = line[6:]
                        try:
                            data_obj = json.loads(data_str)
                            if 'text' in data_obj:
                                text_chunks.append(data_obj['text'])
                        except:
                            pass
                
                full_text = "".join(text_chunks)
                print(f"     Received {events_count} events")
                print(f"     Text length: {len(full_text)} characters")
                if full_text:
                    print(f"     Preview: {full_text[:150]}...")
            else:
                print(f"     ⚠️ Cảnh báo: {stream_response.status_code}")
        except Exception as e:
            print(f"     ⚠️ Lỗi streaming: {str(e)[:100]}")
        
        # 5. Test step ở giữa
        if total_steps > 4:
            mid_step = total_steps // 2
            print(f"\n  5️⃣ Gọi /api/v1/rag/explain/{session_id}?step_index={mid_step}...")
            mid_response = requests.get(
                f"{BASE_URL}/rag/explain/{session_id}?step_index={mid_step}",
                timeout=30
            )
            
            if mid_response.status_code == 200:
                mid_data = mid_response.json()
                print(f"     ✅ Thành công")
                print(f"     Description: {mid_data.get('description', 'N/A')}")
            else:
                print(f"     ❌ Lỗi: {mid_response.status_code}")
        
        results[algo] = {"status": "PASS", "session_id": session_id, "total_steps": total_steps}
        
    except requests.exceptions.Timeout:
        print(f"  ❌ Timeout - request quá lâu")
        results[algo] = {"status": "TIMEOUT"}
    except Exception as e:
        print(f"  ❌ Lỗi: {str(e)[:100]}")
        results[algo] = {"status": "ERROR", "error": str(e)[:100]}

# =========== TÓMLƯỢC KẾT QUẢ ===========
print(f"\n\n{'=' * 70}")
print("📊 TÓM TẮT KẾT QUẢ")
print(f"{'=' * 70}")

for algo in algorithms:
    result = results.get(algo, {})
    status = result.get("status", "UNKNOWN")
    
    if status == "PASS":
        print(f"✅ {algo:15} - PASS (steps: {result.get('total_steps')})")
    elif status == "FAIL":
        print(f"❌ {algo:15} - FAIL ({result.get('error', 'unknown')[:50]})")
    elif status == "TIMEOUT":
        print(f"⏱️ {algo:15} - TIMEOUT")
    else:
        print(f"❓ {algo:15} - ERROR ({result.get('error', 'unknown')[:50]})")

print(f"\n{'=' * 70}")
print(f"Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'=' * 70}\n")