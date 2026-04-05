# Graph AI Tutor + RAG

Ung dung web giao duc ho tro hoc thuat toan do thi bang mo phong truc quan tung buoc, ket hop tro ly AI su dung RAG de giai thich ngu canh thuat toan.

## Tong quan kien truc

```text
Frontend (Next.js, TypeScript, Tailwind)
				<-> REST API
Backend (FastAPI, Python)
				<-> SQLAlchemy (SQL DB)
				<-> ChromaDB (Vector DB)
				<-> Gemini API (LLM)
```

## Muc tieu du an

- Minh hoa thao tac do thi theo tung buoc (Visualization).
- Cho phep di chuyen Next/Back step thong qua co che Snapshot.
- Giai thich ly do thuc hien moi buoc bang tro ly AI theo ngu canh.
- Ho tro hoi dap theo ngu canh buoc thuat toan dang chay.

## Yeu cau he thong

- Python 3.12
- Node.js LTS (khuyen nghi 20+)
- Git

## Quick Start

1. Clone repository

```bash
git clone <repo-url>
cd graph-ai-tutor
```

2. Chay Backend (FastAPI)

```bash
cd backend
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. Chay Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

4. Truy cap he thong

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs

## Cau truc thu muc chinh

```text
backend/
	app/
		api/        # Endpoint va router FastAPI
		core/       # Cau hinh, constants, helper dung chung
		db/         # Ket noi DB, session, migration utility
		models/     # SQLAlchemy models
		schemas/    # Pydantic schema (request/response)
		services/   # Nghiep vu: algorithm, rag_query

frontend/
	src/
		app/        # App Router (layout, page, global styles)
		components/ # UI component va graph/chat component
		hooks/      # React hooks tai su dung
		services/   # API service goi backend
		types/      # Kieu TypeScript dung chung
```

## Danh sach thanh vien

| Vai tro | Thanh vien | Nhiem vu chinh |
|---|---|---|
| Nhom truong | TBD | Dieu phoi chung, review kien truc, quan ly tien do |
| Backend Developer | TBD | FastAPI, SQLAlchemy, RAG pipeline, API docs |
| Frontend Developer | TBD | Next.js UI, graph visualization, chat UI, API integration |

## Ghi chu

- Backend dung moi truong ao trong backend/.venv.
- Frontend uu tien component-based va type-safe.
- Cau hinh bien moi truong chi tiet nam trong backend/README.md va frontend/README.md.
