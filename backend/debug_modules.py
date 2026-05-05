"""
Debug script để kiểm tra 3 module RAG Pipeline:
- Module 1: Ingestion (ChromaDB có data không?)
- Module 2: Simulation Engine (Session có snapshot không?)
- Module 3: Orchestrator (call_llm_stream có lỗi không?)
"""

import os
import sys
import json
from dotenv import load_dotenv

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

print("=" * 80)
print("🔍 DEBUG MODULES: RAG Pipeline")
print("=" * 80)

# ============================================================================
# MODULE 1: DEBUG INGESTION (ChromaDB)
# ============================================================================
print("\n\n📦 MODULE 1: INGESTION (ChromaDB)")
print("-" * 80)

try:
    from app.services.rag_orchestrator import _get_chroma_store, COLLECTION_NAME
    
    vector_store = _get_chroma_store()
    collection = vector_store._collection
    
    print(f"✅ ChromaDB connected!")
    print(f"   Collection name: {COLLECTION_NAME}")
    print(f"   Total documents in collection: {collection.count()}")
    
    # Check what algorithms are in ChromaDB
    print(f"\n   Checking metadata breakdown...")
    try:
        # Get all documents to see what algorithms are stored
        all_docs = collection.get(include=["metadatas"])
        if all_docs and all_docs["metadatas"]:
            algos = set()
            for meta in all_docs["metadatas"]:
                if meta:
                    algo = meta.get("algorithm", "unknown")
                    algos.add(algo)
            print(f"   Algorithms in ChromaDB: {algos}")
        else:
            print(f"   ⚠️ No documents found in ChromaDB!")
    except Exception as e:
        print(f"   ⚠️ Error checking ChromaDB metadata: {e}")
        
except Exception as e:
    print(f"❌ ChromaDB Error: {e}")

# ============================================================================
# MODULE 2: DEBUG SIMULATION ENGINE (Database)
# ============================================================================
print("\n\n🗄️  MODULE 2: SIMULATION ENGINE (Database)")
print("-" * 80)

try:
    from app.db.session import SessionLocal
    from app.models import models
    
    db = SessionLocal()
    
    # Check if session exists
    session_id = "sess-8cb83d67"
    algo_session = db.query(models.AlgoSession).filter(
        models.AlgoSession.session_id == session_id
    ).first()
    
    if algo_session:
        print(f"✅ Session found: {session_id}")
        print(f"   Algorithm: {algo_session.algo_name}")
        print(f"   Start node: {algo_session.start_node}")
        print(f"   Total steps: {algo_session.total_steps}")
        
        # Check snapshots
        snapshots = db.query(models.ExecutionState).filter(
            models.ExecutionState.session_id == session_id
        ).all()
        print(f"   Total snapshots: {len(snapshots)}")
        
        # Check step 4 specifically
        step_4 = db.query(models.ExecutionState).filter(
            models.ExecutionState.session_id == session_id,
            models.ExecutionState.step_index == 4
        ).first()
        
        if step_4:
            print(f"\n   ✅ Step 4 snapshot found!")
            print(f"      Description: {step_4.description}")
            print(f"      Step data: {json.dumps(step_4.step_data_json, ensure_ascii=False, indent=8)[:500]}...")
        else:
            print(f"   ❌ Step 4 snapshot NOT FOUND!")
    else:
        print(f"❌ Session NOT FOUND: {session_id}")
        
    db.close()
    
except Exception as e:
    print(f"❌ Database Error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# MODULE 3: DEBUG RAG ORCHESTRATOR (call_llm_stream)
# ============================================================================
print("\n\n🤖 MODULE 3: RAG ORCHESTRATOR (LLM Streaming)")
print("-" * 80)

try:
    from app.services.rag_query import call_llm_stream, call_llm
    
    print(f"✅ LLM modules imported successfully")
    
    # Test a simple prompt
    test_prompt = "Giải thích ngắn gọn thuật toán Dijkstra là gì?"
    
    print(f"\n   Testing call_llm() (non-streaming)...")
    try:
        result = call_llm(test_prompt)
        print(f"   ✅ Success! Received: {result[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {type(e).__name__}: {str(e)[:200]}")
    
    print(f"\n   Testing call_llm_stream()...")
    try:
        chunks = []
        for chunk in call_llm_stream(test_prompt):
            chunks.append(chunk)
            if len(chunks) <= 3:
                print(f"      Chunk {len(chunks)}: {chunk[:50]}...")
        print(f"   ✅ Stream completed! Total chunks: {len(chunks)}")
    except Exception as e:
        print(f"   ❌ Stream Error: {type(e).__name__}: {str(e)[:200]}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"❌ LLM Module Error: {e}")
    import traceback
    traceback.print_exc()

print("\n\n" + "=" * 80)
print("✅ Debug complete!")
print("=" * 80)