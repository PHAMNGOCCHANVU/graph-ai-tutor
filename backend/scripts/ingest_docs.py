from __future__ import annotations

import argparse
from pathlib import Path


def chunk_markdown(text: str, chunk_size: int = 800, overlap: int = 120) -> list[str]:
    """Simple chunker for markdown content before embedding."""
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def load_documents(source_dir: Path) -> list[tuple[Path, str]]:
    docs: list[tuple[Path, str]] = []
    for file_path in source_dir.rglob("*.md"):
        docs.append((file_path, file_path.read_text(encoding="utf-8")))
    return docs


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest markdown docs for RAG")
    parser.add_argument(
        "--source",
        default="../docs",
        help="Path to source markdown docs folder",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    source = (script_dir / args.source).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Source docs folder not found: {source}")

    docs = load_documents(source)
    total_chunks = 0

    for file_path, content in docs:
        chunks = chunk_markdown(content)
        total_chunks += len(chunks)
        # Placeholder: replace with actual embedding + Chroma upsert.
        print(f"Prepared {len(chunks)} chunks from {file_path}")

    print(f"Ingestion finished. Files: {len(docs)}, Chunks: {total_chunks}")


if __name__ == "__main__":
    main()
