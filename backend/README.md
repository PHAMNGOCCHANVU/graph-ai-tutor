## Backend - Graph AI Tutor

Tai lieu ky thuat danh cho thanh vien phat trien Backend (FastAPI + RAG).

## 1) Cong nghe chinh

- Python 3.12
- FastAPI
- SQLAlchemy (SQL database)
- ChromaDB (vector database) + local embeddings (sentence-transformers)
- OpenRouter API (OpenAI-compatible) cho LLM (GPT-3.5 Turbo)
- LangChain cho RAG orchestration

## 2) Cai dat moi truong

Tu thu muc backend, chay cac lenh sau:

```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Neu dung macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Bien moi truong (.env)

Tao file backend/.env voi cac key toi thieu:

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
DATABASE_URL=sqlite:///./data/app.db
CHROMA_PERSIST_DIRECTORY=./data/chroma
RECORD_MANAGER_DB_URL=sqlite:///./data/record_manager_cache.sql
RECORD_MANAGER_NAMESPACE=graph_ai_tutor_knowledge
```

Giai thich nhanh:

- OPENROUTER_API_KEY: Khoa API de goi model OpenRouter (OpenAI-compatible API wrapper).
- DATABASE_URL: Chuoi ket noi SQL de luu graph, session va snapshot.
- CHROMA_PERSIST_DIRECTORY: Thu muc luu vector store (ChromaDB).
- RECORD_MANAGER_DB_URL: SQLAlchemy URL cho LangChain SQLRecordManager (theo doi lifecycle index).
- RECORD_MANAGER_NAMESPACE: Namespace de phan biet cac collection trong indexing lifecycle.

## 3.1) Chay Module 1 (Ingestion -> Chroma)

Tu thu muc backend:

```bash
python -m scripts.ingest_docs --source ../docs/algorithms --collection graph_ai_tutor_knowledge
```

Lenh tren se:

- Doc toan bo file markdown trong docs/algorithms/.
- Tach frontmatter + heading de tao chunk co metadata.
- Embed bang local embeddings (sentence-transformers - khong can API).
- Upsert vao ChromaDB voi LangChain indexing (incremental cleanup).

**Luu y:** Ingestion chi can Google GenAI API key la **KHONG** (dung local embeddings).

Lenh hay dung khi can reset collection va test retrieval nhanh:

```bash
python -m scripts.ingest_docs --source ../docs/algorithms --collection graph_ai_tutor_knowledge --reset --verbose
```

Mot so tuy chon chinh:

- --chunk-size: kich thuoc chunk fallback (mac dinh 800)
- --overlap: overlap fallback (mac dinh 120)
- --batch-size: so chunk moi batch embed/upsert (mac dinh 32)
- --embedding-model: **IGNORE** - dung local embeddings mac dinh (khong can model param nua)
- --chroma-dir: ghi de CHROMA_PERSIST_DIRECTORY tu CLI
- --record-manager-db-url: db url cho LangChain SQLRecordManager (mac dinh sqlite:///./data/record_manager_cache.sql)
- --record-manager-namespace: namespace theo collection de theo doi lifecycle index
- --cleanup: che do cleanup index (none|incremental|full|scoped_full), mac dinh incremental
- --source-id-key: metadata key lam source id cho cleanup incremental (mac dinh source_path)
- --cleanup-batch-size: batch size cho pha cleanup record keys (mac dinh 1000)
- --force-update: bat buoc index lai ngay ca khi hash noi dung khong doi
- --key-encoder: thuat toan hash cho LangChain index (mac dinh sha256)
- --reset: xoa va tao lai collection tren ChromaDB (dung khi can re-ingest)
- --smoke-check: sau khi ingest xong, chay test retrieval queries de dam bao quality
- --top-k: so ket qua top-k cho smoke-check (mac dinh 3)
- --verbose: bat log chi tiet trong qua trinh ingest

## 4) Cau truc thu muc backend

```text
backend/
	app/
		main.py              # Diem khoi tao FastAPI app
		api/                 # Dinh nghia endpoint va router
		core/                # Cau hinh he thong, constants
		db/                  # Ket noi DB, session, utility lien quan DB
		models/              # SQLAlchemy models
		schemas/             # Pydantic schemas (request/response)
		services/
			algorithms.py      # API endpoint: thuong doan chay thuat toan, init session, get step
			rag.py             # API endpoint: RAG explain (stream + non-stream)
			rag_query.py       # Logic: cong LLM via OpenRouter, stream generation
			rag_orchestrator.py # Logic: retrieval from ChromaDB, prompt building
	data/                  # Du lieu local (db, chroma, snapshot, cache)
	scripts/               # Script ho tro import/indexing/seed
```

## 4.1) Luu y SSL verification (Development only)

Neu mac OpenRouter API bi SSL certificate errors (Windows development):

```python
# backend/app/services/rag_query.py - _get_openrouter_client()
import httpx

http_client = httpx.Client(verify=False)  # ⚠️ Chi su dung trong development
return OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    http_client=http_client,
)
```

**Khong nen dung trong PRODUCTION.** Thay vao do, cai dat CA certificates:

```bash
pip install certifi
python -c "import certifi; print(certifi.where())"
```

Sau do them vao backend/.env:

```
REQUESTS_CA_BUNDLE=/path/to/cacert.pem
CURL_CA_BUNDLE=/path/to/cacert.pem
```

## 5) Chay server

```bash
uvicorn app.main:app --reload
```

Mac dinh server chay tai: http://localhost:8000

**Luu y:** Truoc khi chay, dam bao Module 1 (Ingestion) da hoan thanh:

```bash
python -m scripts.ingest_docs --source ../docs/algorithms --collection graph_ai_tutor_knowledge --reset
```

## 6) Test RAG Pipeline

Script test SSE stream endpoint:

```bash
python test_stream.py
```

Script debug tung module RAG (Ingestion, DB, LLM):

```bash
python debug_modules.py
```

## 7) Tai lieu API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Hay kiem tra /docs sau moi thay doi endpoint de dam bao contract Frontend-Backend luon khop.

### Cac endpoint chinh:

- `POST /api/v1/graphs` - Tao do thi moi
- `POST /api/v1/init` - Khoi tao session chay thuat toan
- `GET /api/v1/step/{session_id}` - Lay snapshot tai step
- `GET /api/v1/rag/explain/{session_id}/stream` - SSE stream RAG explanation (video typing effect)
- `GET /api/v1/rag/explain/{session_id}` - Non-stream RAG explanation (raw response)

## 8) Quy uoc code

- Tach ro endpoint (api) va nghiep vu (services).
- Moi request/response deu di qua schema trong schemas/.
- Uu tien type hint day du, dat ten bien va ham ro nghia.
- Khong hard-code secret trong source code; dung .env.
- Dung local embeddings cho ingestion (khong can call embedding API multiple times).
- Cache AI explanations theo (session_id, step_index) de tranh re-call LLM.
