## Backend - Graph AI Tutor

Tai lieu ky thuat danh cho thanh vien phat trien Backend (FastAPI + RAG).

## 1) Cong nghe chinh

- Python 3.12
- FastAPI
- SQLAlchemy (SQL database)
- ChromaDB (vector database)
- Gemini API qua LangChain

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
GEMINI_API_KEY=your_api_key
DATABASE_URL=sqlite:///./data/app.db
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

Giai thich nhanh:

- GEMINI_API_KEY: Khoa API de goi mo hinh Gemini.
- DATABASE_URL: Chuoi ket noi SQL de luu graph va snapshot.
- CHROMA_PERSIST_DIRECTORY: Thu muc luu vector store cho RAG.

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
			algorithm.py       # Logic chay thuat toan do thi
			rag_query.py       # Logic truy van RAG + Gemini
	data/                  # Du lieu local (db, chroma, snapshot)
	scripts/               # Script ho tro import/indexing/seed
```

## 5) Chay server

```bash
uvicorn app.main:app --reload
```

Mac dinh server chay tai: http://localhost:8000

## 6) Tai lieu API

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Hay kiem tra /docs sau moi thay doi endpoint de dam bao contract Frontend-Backend luon khop.

## 7) Quy uoc code

- Tach ro endpoint (api) va nghiep vu (services).
- Moi request/response deu di qua schema trong schemas/.
- Uu tien type hint day du, dat ten bien va ham ro nghia.
- Khong hard-code secret trong source code; dung .env.
