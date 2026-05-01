"""
Manual test script for Module 3 (RAG Orchestrator)
---------------------------------------------------
Cach dung:
  1. Mo terminal backend: cd backend && .venv\Scripts\activate
  2. Chay server: uvicorn app.main:app --reload
  3. Mo terminal moi, chay: python test_rag.py

Script nay se:
  - Buoc 1: Goi POST /api/v1/init de tao session Dijkstra
  - Buoc 2: Goi GET /api/v1/rag/explain/{session_id}?step_index=0 de test RAG
  - Buoc 3: Goi GET /api/v1/rag/explain/{session_id}/stream?step_index=0 de test SSE
"""

import requests
import json

# --- CONFIG ---
BASE_URL = "http://localhost:8000/api/v1"
GRAPH_ID = 1
START_NODE = "A"
ALGORITHM = "Dijkstra"


def test_init_session():
    """Buoc 1: Khoi tao session thuat toan."""
    print("=" * 60)
    print("BUOC 1: Khoi tao Session thuat toan")
    print("=" * 60)
    print(f"  POST {BASE_URL}/init")
    print(f"  Payload: graph_id={GRAPH_ID}, start_node={START_NODE}, algorithm={ALGORITHM}")

    init_payload = {
        "graph_id": GRAPH_ID,
        "start_node": START_NODE,
        "algorithm": ALGORITHM,
    }
    resp = requests.post(f"{BASE_URL}/init", json=init_payload)

    if resp.status_code != 200:
        print(f"  THAT BAI (status={resp.status_code})")
        print(f"  Response: {resp.text}")
        return None

    data = resp.json()
    session_id = data.get("session_id")
    total_steps = data.get("total_steps")
    print(f"  THANH CONG")
    print(f"  session_id : {session_id}")
    print(f"  total_steps: {total_steps}")
    print()
    return session_id, total_steps


def test_rag_explain(session_id: str, step_index: int):
    """Buoc 2: Test RAG explain (non-streaming)."""
    print("=" * 60)
    print(f"BUOC 2: RAG Explain - step {step_index}")
    print("=" * 60)
    print(f"  GET {BASE_URL}/rag/explain/{session_id}?step_index={step_index}")

    resp = requests.get(f"{BASE_URL}/rag/explain/{session_id}", params={"step_index": step_index})

    if resp.status_code != 200:
        print(f"  THAT BAI (status={resp.status_code})")
        print(f"  Response: {resp.text}")
        return

    data = resp.json()
    print(f"  THANH CONG")
    print(f"  Thuat toan : {data.get('algorithm')}")
    print(f"  Phase      : {data.get('phase_id')}")
    print(f"  Mo ta      : {data.get('description')}")
    print(f"\n  --- Loi giai thich tu Gemini ---")
    print(f"  {data.get('answer')}")
    print(f"\n  --- Theory chunks da dung ---")
    for i, chunk in enumerate(data.get("theory_chunks", []), 1):
        print(f"  {i}. {chunk.get('source_path')} (score={chunk.get('score'):.3f}, phase={chunk.get('phase_id')})")
    print()


def test_rag_stream(session_id: str, step_index: int):
    """Buoc 3: Test RAG explain streaming (SSE)."""
    print("=" * 60)
    print(f"BUOC 3: RAG Explain STREAMING - step {step_index}")
    print("=" * 60)
    print(f"  GET {BASE_URL}/rag/explain/{session_id}/stream?step_index={step_index}")
    print(f"  (Dang nhan du lieu SSE...)")
    print()

    resp = requests.get(
        f"{BASE_URL}/rag/explain/{session_id}/stream",
        params={"step_index": step_index},
        stream=True,
    )

    if resp.status_code != 200:
        print(f"  THAT BAI (status={resp.status_code})")
        print(f"  Response: {resp.text}")
        return

    full_text = ""
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith("event: meta"):
            data_line = next(resp.iter_lines(decode_unicode=True))
            if data_line and data_line.startswith("data: "):
                meta = json.loads(data_line[6:])
                print(f"  [META] session_id={meta['session_id']}, step_index={meta['step_index']}")
        elif line.startswith("event: chunk"):
            data_line = next(resp.iter_lines(decode_unicode=True))
            if data_line and data_line.startswith("data: "):
                chunk_data = json.loads(data_line[6:])
                text = chunk_data.get("text", "")
                full_text += text
                print(text, end="", flush=True)
        elif line.startswith("event: done"):
            print()
            print(f"\n  Streaming hoan tat ({len(full_text)} ky tu)")
            print()

    resp.close()


def main():
    print()
    print("=== MODULE 3 - MANUAL TEST SCRIPT ===")
    print()

    # Buoc 1: Init session
    result = test_init_session()
    if result is None:
        print("Khong the tiep tuc vi init session that bai.")
        return
    session_id, total_steps = result

    # Buoc 2: Test RAG explain cho step 0
    test_rag_explain(session_id, 0)

    # Neu co nhieu step, test them step giua
    if total_steps > 2:
        mid_step = total_steps // 2
        test_rag_explain(session_id, mid_step)

    # Buoc 3: Test SSE streaming
    test_rag_stream(session_id, 0)

    print("=" * 60)
    print("KIEM TRA HOAN TAT")
    print("=" * 60)


if __name__ == "__main__":
    main()