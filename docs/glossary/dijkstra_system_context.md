---
algorithm: dijkstra
doc_type: glossary
language: vi
canonical_terms_version: 1.0
intent_tags: [terminology_alignment, style_guardrail, variable_mapping]
source_scope: static_knowledge
---

## Mục tiêu tài liệu

Tài liệu này chuẩn hoa cach goi bien giua runtime JSON va ngon ngu su pham de module orchestrator sinh cau tra loi nhat quan.

## Bang anh xa thuat ngu chinh

### Term 1

- runtime_name: `dist[]`
- canonical_name: `d[]`
- learner_friendly_name: nhan khoang cach
- aliases: [distance, distance_label]
- forbidden_confusions: [khoang cach cuoi cung ngay tu dau]
- formula_anchor: `d[v] = min(d[v], d[u] + w(u,v))`
- phase_usage:
    - `init`: khoi tao 0 va +infinity
    - `select`: dung de chon dinh min
    - `relax`: co the giam nhan
    - `heap_update`: cap nhat do uu tien

### Term 2

- runtime_name: `visited[]`
- canonical_name: `Free[]`
- learner_friendly_name: trang thai nhan
- aliases: [fixed_set, unvisited]
- forbidden_confusions: [visited true la nhan tu do]
- mapping_rule: `Free[v] = not visited[v]`
- phase_usage:
    - `init`: tat ca dinh la tu do
    - `select`: dinh duoc chon chuyen sang da co dinh
    - `relax`: chi xet dinh con tu do

### Term 3

- runtime_name: `priority_queue`
- canonical_name: `Heap`
- learner_friendly_name: hang doi uu tien
- aliases: [min_heap, queue]
- forbidden_confusions: [heap quyet dinh dap an]
- phase_usage:
    - `select`: lay dinh co nhan nho nhat
    - `heap_update`: push lai hoac decrease-key khi nhan thay doi

## Response Style Rules cho Orchestrator

1. Trong cau tra loi cho nguoi hoc, uu tien ten su pham: `nhan khoang cach d[v]`, `nhan tu do/co dinh`, `heap`.
2. Khi can noi voi runtime, nhac them cap anh xa mot lan dau tien: "`dist[]` (tuong ung `d[]`)".
3. Khong doi qua doi lai giua `visited` va `Free` trong cung doan van. Chon mot cach dien dat va giu on dinh.
4. Neu snapshot khong co `priority_queue`, van duoc phep giai thich theo logic chon min bang quet mang, nhung phai noi ro khac biet hieu nang.

## Conflict Resolution Rules

- Neu co ca `d[]` va `dist[]` trong input prompt: dung `d[]` la canonical, `dist[]` chi la alias runtime.
- Neu co ca `visited[]` va `Free[]`: uu tien giai thich bang `Free[]` de giu ly thuyet co dinh nhan.
- Neu user hoi thuan ky thuat code: co the dao nguoc, uu tien ten runtime de sat code.

## Micro Explanations (mau ngan)

1. Mau cho phase `select`:
"Tai buoc nay, ta chon dinh tu do co `d[v]` nho nhat de co dinh nhan, vi voi trong so khong am thi khong con duong vong nao re hon."

2. Mau cho phase `relax`:
"Ta dang thu xem duong di qua dinh vua co dinh co lam giam nhan cua dinh ke hay khong theo cong thuc min."

3. Mau cho phase `heap_update`:
"Sau khi nhan giam, dinh can duoc cap nhat uu tien trong heap de dam bao lan pop tiep theo van lay dinh nho nhat."

## Validation Checklist

- Moi cau tra loi phai dung dung cap anh xa runtime-canonical.
- Khong su dung nguon tu moi ngoai bang anh xa trong tai lieu nay.
- Co nhac relation voi phase dang chay neu snapshot co thong tin phase.

## Output Schema de Orchestrator bam theo

```yaml
response_schema:
    required_fields:
        - intent_id
        - phase_id
        - direct_explanation
        - state_evidence
        - theory_anchor
        - next_step_hint
    constraints:
        direct_explanation_max_sentences: 3
        state_evidence_must_reference_snapshot_keys: true
        theory_anchor_must_include_canonical_term: true
        avoid_unmapped_terms: true
```

## Intent-specific Response Templates

### Template - intent `why`

- direct_explanation: tra loi ly do co so ly thuyet trong 2-3 cau.
- state_evidence: chi ra toi thieu 1 key tu snapshot (`dist`, `visited`, `priority_queue`).
- theory_anchor: bat buoc co mot trong cac tu `d[]`, `Free[]`, `Heap`.
- next_step_hint: goi y buoc tiep theo nguoi hoc nen quan sat.

### Template - intent `how`

- direct_explanation: mo ta quy trinh cap nhat theo trinh tu phase.
- state_evidence: neu co `dist_before` va `dist_after` thi phai neu ro su thay doi.
- theory_anchor: bat buoc nhac cong thuc hoac invariant lien quan.
- next_step_hint: du doan tac dong den phase ke tiep.

### Template - intent `edge_case`

- direct_explanation: ket luan nhanh trang thai hop le hay bat thuong.
- state_evidence: bat buoc noi ro dau hieu edge case trong snapshot.
- theory_anchor: lien ket voi dieu kien dung/sai cua Dijkstra.
- next_step_hint: de xuat hanh dong an toan (vi du: canh bao canh am).

## Anti-Hallucination Rules

1. Neu snapshot thieu key quan trong, phai noi ro "thieu du lieu" thay vi suy dien.
2. Khong duoc khang dinh co duong di neu `dist[target]` van la gia tri vo cung.
3. Khong gan nguyen nhan lien quan canh am neu snapshot khong co thong tin trong so.
4. Neu dua ra do phuc tap, chi dung cac dang da duoc cho phep: `O(n^2)` hoac `O((m+n)logn)`.

## Quick Eval Prompts cho Glossary Alignment

1. "Tai sao visited=true thi khong relax nua?"
2. "Dist va d co khac nhau khong?"
3. "Heap co lam thay doi dap an hay chi thay doi toc do?"

Expected: cau tra loi phai dung canonical mapping va khong doi thuat ngu tuy y.