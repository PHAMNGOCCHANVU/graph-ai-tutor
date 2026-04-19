from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from app.services.rag_ingestion.parser import build_chunk_records, load_documents
from app.services.rag_ingestion.vector_store import IngestionVectorStore

logger = logging.getLogger(__name__)

DEFAULT_SMOKE_QUERIES = [
    "Tai sao Dijkstra khong dung voi canh am?",
    "Hay giai thich buoc relax trong Dijkstra.",
    "Khi nao co the early stop khi tim source-target?",
]


@dataclass
class IngestionStats:
    files_scanned: int = 0
    files_ingested: int = 0
    files_skipped: int = 0
    chunks_upserted: int = 0
    num_added: int = 0
    num_deleted: int = 0
    num_skipped: int = 0
    num_updated: int = 0


def run_ingestion(
    source: Path,
    vector_store: IngestionVectorStore,
    chunk_size: int,
    overlap: int,
    batch_size: int,
    cleanup: str | None,
    source_id_key: str | None,
    cleanup_batch_size: int,
    force_update: bool,
    key_encoder: str,
) -> IngestionStats:
    docs = load_documents(source)
    stats = IngestionStats(files_scanned=len(docs))
    all_documents: list[Document] = []

    for file_path, content in docs:
        records = build_chunk_records(
            source_root=source,
            file_path=file_path,
            content=content,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        if not records:
            stats.files_skipped += 1
            logger.info("Skipped empty/unusable markdown: %s", file_path)
            continue

        for chunk_id, text_chunk, metadata in records:
            doc_metadata = dict(metadata)
            doc_metadata["chunk_id"] = chunk_id
            all_documents.append(Document(page_content=text_chunk, metadata=doc_metadata))

        stats.files_ingested += 1
        stats.chunks_upserted += len(records)
        logger.info(
            "Ingested %s chunks from %s",
            len(records),
            file_path.relative_to(source),
        )

    if all_documents:
        indexing_result = vector_store.index_documents(
            documents=all_documents,
            batch_size=batch_size,
            cleanup=cleanup,
            source_id_key=source_id_key,
            cleanup_batch_size=cleanup_batch_size,
            force_update=force_update,
            key_encoder=key_encoder,
        )
        stats.num_added = int(indexing_result.get("num_added", 0))
        stats.num_deleted = int(indexing_result.get("num_deleted", 0))
        stats.num_skipped = int(indexing_result.get("num_skipped", 0))
        stats.num_updated = int(indexing_result.get("num_updated", 0))

    return stats


def run_smoke_queries(vector_store: IngestionVectorStore, top_k: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for query in DEFAULT_SMOKE_QUERIES:
        metadatas, distances = vector_store.smoke_query(query=query, top_k=top_k)
        hits: list[dict[str, Any]] = []
        for idx, metadata in enumerate(metadatas):
            score = distances[idx] if idx < len(distances) else None
            source_path = metadata.get("source_path", "unknown") if metadata else "unknown"
            phase_id = metadata.get("phase_id", "n/a") if metadata else "n/a"
            doc_type = metadata.get("doc_type", "n/a") if metadata else "n/a"
            hits.append(
                {
                    "rank": idx + 1,
                    "source_path": source_path,
                    "phase_id": phase_id,
                    "doc_type": doc_type,
                    "distance": score,
                }
            )
        results.append({"query": query, "hits": hits})
    return results
