"""
Test script cho Module 3 - RAG Orchestrator
"""
import os
import sys
import json
import requests
from pathlib import Path
from sqlalchemy import text

# Thêm path backend vào sys.path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models import models

print("=" * 60)
print("TEST MODULE 3 - RAG ORCHESTRATOR")
print("=" * 60)

# ========== TEST 1: Kiểm tra kết nối DB ==========
print("\n[TEST 1] Kiểm tra kết nối Database...")
try:
    db = SessionLocal()
    # Thử query 1 bảng đơn giản để test kết nối
    count = db.query(models.Graph).count()
    db.close()
    print("✅ Database kết nối thành công")
except Exception as e:
    print(f"❌ Lỗi kết nối Database: {e}")
    sys.exit(1)

# ========== TEST 2: Kiểm tra dữ liệu Graph ==========
print("\n[TEST 2] Kiểm tra dữ liệu Graph trong database...")
db = SessionLocal()
try:
    graphs = db.query(models.Graph).all()
    print(f"Tổng số graph: {len(graphs)}")
    if len(graphs) == 0:
        print("⚠️  Không có graph nào trong database!")
        print("   Hãy tạo graph mới qua endpoint POST /api/v1/graphs trước")
    else:
        for g in graphs[:3]:  # Hiển thị 3 graph đầu
            print(f"\n  - Graph ID: {g.graph_id}")
            print(f"    Name: {g.name}")
            print(f"    Data: {json.dumps(g.data_json, indent=2)[:200]}...")
finally:
    db.close()

# ========== TEST 3: Kiểm tra ChromaDB ==========
print("\n[TEST 3] Kiểm tra ChromaDB vector store...")
try:
    from langchain_chroma import Chroma
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    
    CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma")
    COLLECTION_NAME = "graph_ai_tutor_knowledge"
    
    embedder = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
    chroma = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedder,
        persist_directory=CHROMA_DIR,
    )
    count = chroma._collection.count()
    print(f"✅ ChromaDB kết nối thành công")
    print(f"   Documents trong collection: {count}")
    if count == 0:
        print("   ⚠️  Không có document trong ChromaDB!")
        print("   Hãy chạy: python -m scripts.ingest_docs --source ../docs")
except Exception as e:
    print(f"❌ Lỗi ChromaDB: {e}")

# ========== TEST 4: Test API endpoint (nếu server chạy) ==========
print("\n[TEST 4] Kiểm tra API endpoint...")
db = SessionLocal()
try:
    graphs = db.query(models.Graph).first()
    if graphs:
        graph_id = graphs.graph_id
        graph_data = graphs.data_json
        nodes = graph_data.get("nodes", [])
        
        if nodes:
            start_node = nodes[0]["id"] if isinstance(nodes[0], dict) else nodes[0]
            
            print(f"Chuẩn bị test với:")
            print(f"  - Graph ID: {graph_id}")
            print(f"  - Start Node: {start_node}")
            print(f"  - Algorithm: Dijkstra")
            
            # Test gọi API
            try:
                response = requests.post(
                    "http://localhost:8000/api/v1/init",
                    json={
                        "graph_id": graph_id,
                        "start_node": start_node,
                        "algorithm": "Dijkstra"
                    },
                    timeout=10
                )
                print(f"\n📡 Response Status: {response.status_code}")
                print(f"📡 Response Body: {json.dumps(response.json(), indent=2)}")
                
                if response.status_code == 200:
                    print("✅ API /init thành công!")
                    session_id = response.json().get("session_id")
                    
                    # Test endpoint explain RAG
                    print(f"\nTest endpoint RAG /explain/{session_id}?step_index=0...")
                    rag_response = requests.get(
                        f"http://localhost:8000/api/v1/rag/explain/{session_id}?step_index=0",
                        timeout=15
                    )
                    print(f"📡 RAG Response Status: {rag_response.status_code}")
                    if rag_response.status_code == 200:
                        print("✅ RAG endpoint thành công!")
                    else:
                        print(f"❌ RAG endpoint lỗi: {rag_response.text[:200]}")
                else:
                    print(f"❌ API /init lỗi: {response.text}")
            except requests.exceptions.ConnectionError:
                print("⚠️  Không thể kết nối server (http://localhost:8000)")
                print("   Hãy chạy: uvicorn app.main:app --reload")
            except Exception as e:
                print(f"❌ Lỗi khi test API: {e}")
        else:
            print("❌ Graph không có nodes!")
    else:
        print("❌ Không có graph trong database để test!")
finally:
    db.close()

print("\n" + "=" * 60)
print("Kết thúc test Module 3")
print("=" * 60)