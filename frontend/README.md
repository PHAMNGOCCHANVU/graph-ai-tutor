## Frontend - Graph AI Tutor

Tai lieu ky thuat danh cho thanh vien phat trien Frontend (Next.js + TypeScript).

## 1) Cong nghe chinh

- Next.js (App Router)
- React + TypeScript
- Tailwind CSS
- Cytoscape.js (visualization do thi)
- Axios (goi API)

## 2) Cai dat

Tu thu muc frontend, chay:

```bash
npm install
```

## 3) Bien moi truong

Tao file frontend/.env va khai bao:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Luu y:

- Bien bat dau bang NEXT_PUBLIC_ se duoc expose cho browser.
- Khong dua token/secret nhay cam vao bien NEXT_PUBLIC_.

## 4) Cau truc src/

```text
src/
	app/           # App Router (layout.tsx, page.tsx, globals.css)
	components/    # UI component va component theo tinh nang (graph/chat)
	hooks/         # React hooks tai su dung
	services/      # apiService va logic goi REST API
	types/         # Interface/type dung chung cho UI va API contract
```

Quy uoc su dung:

- components/: chi chua UI va logic giao dien, khong goi API truc tiep neu co the tach sang services.
- hooks/: xu ly state/phien lam viec phuc tap de component gon hon.
- services/: gom ham goi backend, mapping payload va xu ly loi co ban.
- types/: de tat ca model giao tiep frontend-backend duoc type-safe.

## 5) Coding style

- Uu tien Tailwind CSS cho giao dien.
- Bat buoc TypeScript, tranh dung any (chi dung khi bat kha khang va co ghi chu ro ly do).
- Component-based: tach nho component theo trach nhiem ro rang.
- API access thong nhat qua apiService trong services/.

## 6) Chay development

```bash
npm run dev
```

Ung dung mac dinh chay tai: http://localhost:3000

## 7) Kiem tra truoc khi merge

```bash
npm run lint
npm run build
```

Dam bao frontend build thanh cong va contract API khop voi Swagger ben backend.

