---
algorithm: dijkstra
doc_type: qa_examples
language: vi
level: foundation
version: 1.0
intent_set: [why, how, edge_case, complexity]
source_scope: static_knowledge
---

## Muc tieu tai lieu

Bo cau hoi nay duoc viet de retrieve theo intent. Moi muc gom: cau tra loi truc tiep, y nghia su pham, va cach noi voi snapshot runtime.

## QA-01

- intent_id: `why_negative_weight_invalid`
- phase_id: `select`
- difficulty: `basic`
- related_terms: [`d[]`, `Free[]`]
- question: Tai sao Dijkstra khong ap dung cho do thi co trong so am?
- direct_answer: Vi buoc co dinh nhan dua tren gia dinh moi canh deu khong am. Canh am co the tao duong vong re hon sau khi mot dinh da bi chot.
- why_it_matters: Neu vi pham gia dinh nay, ket qua co the sai du logic code van chay.
- tie_to_snapshot: Neu phat hien edge weight < 0 trong input graph, can canh bao va chuyen sang Bellman-Ford.

## QA-02

- intent_id: `why_infinity_initialization`
- phase_id: `init`
- difficulty: `basic`
- related_terms: [`d[]`]
- question: Tai sao khoi tao `d[source] = 0`, con dinh khac la `+infinity`?
- direct_answer: Day la cach dat can tren ban dau cho bai toan tim min-cost tu source.
- why_it_matters: Giup thuat toan biet rang chi source da co duong di xac dinh.
- tie_to_snapshot: O step dau tien, `dist[source]` phai bang 0 va nhung dinh con lai rat lon.

## QA-03

- intent_id: `why_pick_min_free`
- phase_id: `select`
- difficulty: `basic`
- related_terms: [`d[]`, `Free[]`]
- question: Tai sao moi buoc phai chon dinh tu do co nhan nho nhat?
- direct_answer: Vi voi trong so khong am, dinh nho nhat hien tai khong the duoc cai thien boi duong vong sau do.
- why_it_matters: Day la ly do then chot giup Dijkstra dung.
- tie_to_snapshot: Dinh vua pop ra tu `priority_queue` duoc xem la dinh can co dinh nhan.

## QA-04

- intent_id: `why_early_stop_target`
- phase_id: `select`
- difficulty: `basic`
- related_terms: [`d[]`, `target`]
- question: Tai sao co the dung som khi dinh dich da co dinh nhan?
- direct_answer: Vi gia tri `d[target]` luc duoc chot la toi uu roi.
- why_it_matters: Giam thoi gian chay neu chi can mot cap source-target.
- tie_to_snapshot: Neu `current_node == target` va node da co dinh, co the ket thuc simulation.

## QA-05

- intent_id: `why_relaxation_formula`
- phase_id: `relax`
- difficulty: `basic`
- related_terms: [`d[]`, `relaxation`]
- question: Tai sao cong thuc sua nhan la `d[v] = min(d[v], d[u] + w(u,v))`?
- direct_answer: Vi ta so sanh ky luc hien tai voi mot ung vien duong di moi di qua `u`.
- why_it_matters: Day la thao tac cap nhat toi uu cuc bo lap lai de tao toi uu toan cuc.
- tie_to_snapshot: Moi lan cap nhat thanh cong can thay doi `dist[v]` va thong tin trace.

## QA-06

- intent_id: `why_need_state_set`
- phase_id: `select`
- difficulty: `basic`
- related_terms: [`Free[]`, `visited[]`]
- question: Tai sao can `Free[]` hoac `visited[]`?
- direct_answer: De tach ro dinh da chot ket qua va dinh con cho toi uu.
- why_it_matters: Tranh tinh lai vo ich va tranh pha vo tinh dung cua phep co dinh nhan.
- tie_to_snapshot: Trong giai doan relax, bo qua dinh co `visited = true`.

## QA-07

- intent_id: `why_trace_only_predecessor`
- phase_id: `relax`
- difficulty: `intermediate`
- related_terms: [`trace`, `path_reconstruction`]
- question: Tai sao `Trace[]` chi luu dinh lien truoc?
- direct_answer: Vi mot con tro moi dinh la du de truy vet nguoc duong di voi bo nho tuyen tinh.
- why_it_matters: Dat can bang tot giua bo nho va kha nang khoi phuc duong di.
- tie_to_snapshot: Moi lan giam nhan thanh cong thi cap nhat `trace[v] = u`.

## QA-08

- intent_id: `why_heap`
- phase_id: `heap_update`
- difficulty: `intermediate`
- related_terms: [`Heap`, `priority_queue`]
- question: Tai sao dung Heap trong Dijkstra?
- direct_answer: Heap giup lay dinh co nhan nho nhat nhanh hon duyet mang.
- why_it_matters: Cai thien lon ve hieu nang tren do thi thua.
- tie_to_snapshot: Cac cap `(distance, node)` trong `priority_queue` dai dien trang thai xep uu tien.

## QA-09

- intent_id: `why_reheap_after_decrease`
- phase_id: `heap_update`
- difficulty: `intermediate`
- related_terms: [`Heap`, `d[]`]
- question: Tai sao giam nhan xong phai cap nhat lai heap?
- direct_answer: Vi thu tu uu tien da thay doi, neu khong cap nhat thi buoc select sau co the lay sai node.
- why_it_matters: Bao toan tinh dung cua co che chon min theo cau truc du lieu.
- tie_to_snapshot: Neu `dist[v]` giam, can push lai hoac decrease-key cho `v`.

## QA-10

- intent_id: `why_sparse_graph_benefit`
- phase_id: `heap_update`
- difficulty: `intermediate`
- related_terms: [`complexity`, `m`, `n`]
- question: Tai sao Dijkstra + Heap hop voi do thi thua hon do thi day?
- direct_answer: Vi do thi thua co so canh it, thanh phan logarit cua heap tao loi ich ro net.
- why_it_matters: Giup chon dung cach cai dat theo kieu du lieu dau vao.
- tie_to_snapshot: Khi so canh lon gan binh phuong so dinh, can so sanh voi ban cai dat quet mang.

## QA-11

- intent_id: `why_unreachable_nodes_remain_infinity`
- phase_id: `edge_case`
- difficulty: `basic`
- related_terms: [`d[]`, `disconnected_graph`]
- question: Tai sao co dinh den cuoi van giu gia tri `+infinity`?
- direct_answer: Vi khong ton tai duong di tu source den nhung dinh do trong thanh phan lien thong hien tai.
- why_it_matters: Tra ve ket qua "khong the toi" la dung, khong phai loi thuat toan.
- tie_to_snapshot: O step cuoi, nhung node nay co `dist[v]` lon va khong co trace hop le.

## QA-12

- intent_id: `how_handle_equal_distance_ties`
- phase_id: `select`
- difficulty: `intermediate`
- related_terms: [`priority_queue`, `tie_break`]
- question: Neu nhieu dinh cung co cung nhan nho nhat thi sao?
- direct_answer: Co the chon bat ky theo quy tac tie-break, ket qua khoang cach toi uu van dung.
- why_it_matters: Giai thich vi sao thu tu duyet co the khac nhau nhung dap an cuoi khong doi.
- tie_to_snapshot: Thu tu pop node co the khac giua cac lan chay neu tie-break khac, nhung `dist[]` cuoi cung van hop le.

## Negative Examples (de giam retrieve sai)

### NEG-01

- intent_id: `negative_not_dijkstra`
- phase_id: `out_of_scope`
- user_query: "Tai sao DFS can heap de tim duong ngan nhat?"
- expected_behavior: Tu choi lien ket voi Dijkstra, giai thich ngan gon rang day la cau hoi sai ngu canh.
- must_not_retrieve: chunk giai thich "heap la bo tang toc trong Dijkstra" theo cach khang dinh DFS cung can heap.

### NEG-02

- intent_id: `negative_unseen_weight_sign`
- phase_id: `out_of_scope`
- user_query: "Do thi nay chac chan co canh am nen Dijkstra sai."
- expected_behavior: Yeu cau bang chung tu snapshot truoc khi ket luan.
- must_not_retrieve: chunk ket luan canh am neu khong co du lieu trong so.

### NEG-03

- intent_id: `negative_force_path_exists`
- phase_id: `edge_case`
- user_query: "Target khong noi voi source nhung van phai co duong di."
- expected_behavior: Giu ket luan "khong the toi" neu `dist[target]` la vo cung.
- must_not_retrieve: noi dung khang dinh ton tai duong di khi khong co evidence.

## Retrieval Evaluation Set (v1)

### EVAL-WHY

1. Tai sao dinh co nhan nho nhat co the duoc co dinh ngay?
2. Tai sao sau khi giam nhan thi can cap nhat heap?
3. Tai sao co canh am lam hu buoc chot nhan?

### EVAL-HOW

1. Hay mo ta tu init den select trong Dijkstra.
2. Dist thay doi nhu the nao trong mot lan relax?
3. Heap duoc cap nhat o phase nao va vi sao?

### EVAL-EDGE

1. Neu target khong reachable thi ket qua nen hien thi gi?
2. Neu co nhieu node cung nhan nho nhat thi sao?
3. Co the dung som o buoc nao khi chi can source-target?

### Rubric cham nhanh

- Precision@3 >= 0.8: top 3 chunk phai co it nhat 2 chunk dung intent.
- Phase-match >= 0.85: cau tra loi phai map dung phase chinh.
- Terminology consistency = 1.0: khong mau thuan giua `dist/d`, `visited/Free`, `priority_queue/Heap`.