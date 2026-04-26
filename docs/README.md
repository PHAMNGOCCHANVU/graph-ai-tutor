# Source Documents for RAG

This folder stores static algorithm learning materials used by the ingestion module.

## Suggested structure

- `algorithms/`: theory and step-by-step explanations by algorithm.
- `glossary/`: shared terms and definitions.
- `examples/`: worked graph examples.

Use Markdown (`.md`) as the default authoring format.

## Authoring rules (RAG-ready)

1. Every file should start with YAML frontmatter metadata.
2. Keep one main topic per section to improve chunk quality.
3. Include explicit tags for algorithm, phase, and intent.
4. Write in a teaching style, but keep terms consistent with runtime variables.

## Minimal metadata template

```yaml
---
algorithm: dijkstra
doc_type: theory | glossary | qa_examples
language: vi
level: foundation
version: 1.0
intent_tags: [why, how, edge_case]
source_scope: static_knowledge
---
```

## Required content by folder

- `algorithms/`
	- phase_id blocks (`init`, `select`, `relax`, `heap_update`)
	- snapshot mapping from runtime keys to canonical theory terms
	- boundary and failure conditions

- `glossary/`
	- runtime_name and canonical_name mapping
	- aliases and forbidden confusions
	- response style rules for orchestrator output

- `examples/`
	- intent_id per Q/A
	- phase_id and related_terms
	- short answer format: direct_answer, why_it_matters, tie_to_snapshot
