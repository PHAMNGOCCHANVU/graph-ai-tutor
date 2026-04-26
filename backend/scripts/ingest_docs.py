from __future__ import annotations

import argparse
import logging
from pathlib import Path
from pprint import pprint
from dotenv import load_dotenv

from app.services.rag_ingestion.parser import build_chunk_records, load_documents
from app.services.rag_ingestion.pipeline import run_ingestion, run_smoke_queries
from app.services.rag_ingestion.vector_store import IngestionVectorStore, validate_environment


def preview_chunks(
    source: Path,
    chunk_size: int,
    overlap: int,
    preview_limit: int,
    preview_max_chars: int,
) -> None:
    docs = load_documents(source)
    shown = 0

    print("\nChunk preview")
    print("-" * 60)

    for file_path, content in docs:
        records = build_chunk_records(
            source_root=source,
            file_path=file_path,
            content=content,
            chunk_size=chunk_size,
            overlap=overlap,
        )
        if not records:
            continue

        for chunk_id, text_chunk, metadata in records:
            shown += 1
            if shown > preview_limit:
                print(f"... preview stopped at {preview_limit} chunks")
                return

            text_preview = text_chunk[:preview_max_chars]
            if len(text_chunk) > preview_max_chars:
                text_preview += "..."

            print(f"\n[{shown}] file={metadata.get('source_path')} chunk_id={chunk_id}")
            pprint(
                {
                    "heading_path": metadata.get("heading_path"),
                    "phase_id": metadata.get("phase_id"),
                    "doc_type": metadata.get("doc_type"),
                    "algorithm": metadata.get("algorithm"),
                    "text_preview": text_preview,
                },
                sort_dicts=False,
                width=120,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest markdown docs for RAG")
    parser.add_argument(
        "--source",
        default="../docs/algorithms",
        help="Path to source markdown docs folder (Module 1 scope: docs/algorithms)",
    )
    parser.add_argument(
        "--collection",
        default="graph_ai_tutor_knowledge",
        help="Chroma collection name",
    )
    parser.add_argument("--chunk-size", type=int, default=800, help="Fallback chunk size")
    parser.add_argument("--overlap", type=int, default=120, help="Fallback chunk overlap")
    parser.add_argument("--batch-size", type=int, default=32, help="Embedding/upsert batch size")
    parser.add_argument(
        "--embedding-model",
        default="gemini-embedding-2-preview",
        help="Gemini embedding model name",
    )
    parser.add_argument(
        "--chroma-dir",
        default=None,
        help="Override CHROMA_PERSIST_DIRECTORY",
    )
    parser.add_argument(
        "--record-manager-db-url",
        default="sqlite:///./data/record_manager_cache.sql",
        help="SQLAlchemy URL used by LangChain SQLRecordManager",
    )
    parser.add_argument(
        "--record-manager-namespace",
        default=None,
        help="Optional RecordManager namespace override",
    )
    parser.add_argument("--reset", action="store_true", help="Delete and recreate collection")
    parser.add_argument(
        "--cleanup",
        default="incremental",
        choices=["none", "incremental", "full", "scoped_full"],
        help="LangChain indexing cleanup mode",
    )
    parser.add_argument(
        "--source-id-key",
        default="source_path",
        help="Metadata key used as source id for incremental cleanup",
    )
    parser.add_argument(
        "--cleanup-batch-size",
        type=int,
        default=1000,
        help="Cleanup batch size for RecordManager key deletion",
    )
    parser.add_argument("--force-update", action="store_true", help="Force re-index even if content hash matches")
    parser.add_argument(
        "--key-encoder",
        default="sha256",
        choices=["sha1", "sha256", "sha512", "blake2b"],
        help="Hashing algorithm used by LangChain indexing",
    )
    parser.add_argument(
        "--show-chunk-preview",
        action="store_true",
        help="Print sample chunks before ingestion",
    )
    parser.add_argument(
        "--preview-limit",
        type=int,
        default=5,
        help="Number of chunks to preview",
    )
    parser.add_argument(
        "--preview-max-chars",
        type=int,
        default=280,
        help="Max characters per previewed chunk",
    )
    parser.add_argument(
        "--smoke-check",
        action="store_true",
        help="Run smoke retrieval queries after ingestion",
    )
    parser.add_argument("--top-k", type=int, default=3, help="Top-k for smoke retrieval checks")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed ingestion logs")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s - %(message)s",
    )

    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    source = Path(args.source).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source docs folder not found: {source}")
    if args.preview_limit < 0:
        raise ValueError("preview_limit must be >= 0")
    if args.preview_max_chars <= 0:
        raise ValueError("preview_max_chars must be > 0")

    chroma_dir = validate_environment(args.chroma_dir)
    if args.batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    if args.show_chunk_preview and args.preview_limit > 0:
        preview_chunks(
            source=source,
            chunk_size=args.chunk_size,
            overlap=args.overlap,
            preview_limit=args.preview_limit,
            preview_max_chars=args.preview_max_chars,
        )
        return

    vector_store = IngestionVectorStore(
        chroma_dir=chroma_dir,
        collection_name=args.collection,
        embedding_model=args.embedding_model,
        record_manager_db_url=args.record_manager_db_url,
        record_manager_namespace=args.record_manager_namespace or f"rag_ingestion/{args.collection}",
    )

    if args.reset:
        vector_store.reset_collection()
        print(f"Deleted and recreated collection: {args.collection}")

    stats = run_ingestion(
        source=source,
        vector_store=vector_store,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
        batch_size=args.batch_size,
        cleanup=None if args.cleanup == "none" else args.cleanup,
        source_id_key=args.source_id_key,
        cleanup_batch_size=args.cleanup_batch_size,
        force_update=args.force_update,
        key_encoder=args.key_encoder,
    )

    print("\nIngestion summary")
    print("-" * 60)
    print(f"Source folder: {source}")
    print(f"Collection: {args.collection}")
    print(f"Files scanned: {stats.files_scanned}")
    print(f"Files ingested: {stats.files_ingested}")
    print(f"Files skipped: {stats.files_skipped}")
    print(f"Chunks prepared: {stats.chunks_upserted}")
    print(f"Indexing added: {stats.num_added}")
    print(f"Indexing updated: {stats.num_updated}")
    print(f"Indexing skipped: {stats.num_skipped}")
    print(f"Indexing deleted: {stats.num_deleted}")

    if args.smoke_check:
        smoke_results = run_smoke_queries(vector_store=vector_store, top_k=args.top_k)
        print("\nSmoke retrieval check")
        print("-" * 60)
        for item in smoke_results:
            print(f"Query: {item['query']}")
            for hit in item["hits"]:
                print(
                    "  "
                    f"{hit['rank']}. source={hit['source_path']}, "
                    f"phase={hit['phase_id']}, doc_type={hit['doc_type']}, "
                    f"distance={hit['distance']}"
                )
            print()


if __name__ == "__main__":
    main()
