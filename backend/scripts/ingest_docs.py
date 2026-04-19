from __future__ import annotations

import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

from app.services.rag_ingestion.pipeline import run_ingestion, run_smoke_queries
from app.services.rag_ingestion.vector_store import IngestionVectorStore, validate_environment


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest markdown docs for RAG")
    parser.add_argument(
        "--source",
        default="../docs",
        help="Path to source markdown docs folder",
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
        default="models/text-embedding-004",
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

    load_dotenv()

    source = Path(args.source).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source docs folder not found: {source}")

    chroma_dir = validate_environment(args.chroma_dir)
    if args.batch_size <= 0:
        raise ValueError("batch_size must be > 0")

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
