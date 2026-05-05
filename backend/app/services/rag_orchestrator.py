from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from sqlalchemy.orm import Session

from app.models import models

load_dotenv()

CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma")
COLLECTION_NAME = "graph_ai_tutor_knowledge"

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class DefaultEmbeddings(Embeddings):
    """Local default embeddings using sentence-transformers (no API needed)."""
    def __init__(self) -> None:
        try:
            from chromadb.utils import embedding_functions
            self._ef = embedding_functions.DefaultEmbeddingFunction()
        except ImportError:
            raise RuntimeError("chromadb embeddings not available")

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query text."""
        return self._ef([text])[0]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple documents."""
        return self._ef(texts)


@dataclass
class RetrievedTheory:
    chunk_id: str
    content: str
    score: float
    algorithm: str
    phase_id: str | None
    doc_type: str
    source_path: str


def _get_chroma_store() -> Chroma:
    """Create a read-only Chroma vector store for retrieval using local embeddings."""
    embedder = DefaultEmbeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedder,
        persist_directory=CHROMA_DIR,
    )


def retrieve_snapshot(session_id: str, step_index: int, db: Session) -> dict[str, Any]:
    """Fetch a real ExecutionState snapshot from SQL."""
    snapshot = (
        db.query(models.ExecutionState)
        .filter(
            models.ExecutionState.session_id == session_id,
            models.ExecutionState.step_index == step_index,
        )
        .first()
    )
    if not snapshot:
        raise ValueError(
            f"Snapshot not found for session_id={session_id}, step_index={step_index}"
        )

    # Get the algorithm name from the session
    algo_session = (
        db.query(models.AlgoSession)
        .filter(models.AlgoSession.session_id == session_id)
        .first()
    )
    algo_name = algo_session.algo_name if algo_session else "unknown"

    step_data = snapshot.step_data_json or {}
    return {
        "session_id": session_id,
        "step_index": step_index,
        "algorithm": algo_name,
        "description": snapshot.description or "",
        "phase_id": step_data.get("phase_id", "unknown"),
        "current_node": step_data.get("current_node"),
        "target_node": step_data.get("target_node"),
        "visited": step_data.get("visited", []),
        "distances": step_data.get("distances", {}),
        "queue": step_data.get("queue", []),
    }


def retrieve_theory(
    algorithm: str,
    phase_id: str | None = None,
    question: str | None = None,
    top_k: int = 3,
) -> list[RetrievedTheory]:
    """Retrieve relevant theory chunks from ChromaDB with metadata filtering."""
    vector_store = _get_chroma_store()

    # Build the query text
    query = question or f"Explain the {phase_id or 'current'} step of {algorithm}."

    # Build metadata filter for precise retrieval
    algo_lower = algorithm.lower()
    filter_dict: dict[str, Any] = {"algorithm": algo_lower}
    if phase_id and phase_id != "unknown":
        filter_dict = {"$and": [{"algorithm": algo_lower}, {"phase_id": phase_id}]}

    # Try 1: Search with metadata filter (algorithm + phase_id)
    docs_with_scores = vector_store.similarity_search_with_score(
        query=query,
        k=top_k,
        filter=filter_dict,
    )

    results: list[RetrievedTheory] = []
    for doc, score in docs_with_scores:
        meta = doc.metadata or {}
        results.append(
            RetrievedTheory(
                chunk_id=meta.get("chunk_id", "unknown"),
                content=doc.page_content,
                score=float(score),
                algorithm=meta.get("algorithm", algorithm),
                phase_id=meta.get("phase_id"),
                doc_type=meta.get("doc_type", "unknown"),
                source_path=meta.get("source_path", "unknown"),
            )
        )

    # Fallback 1: if no results with filter, retry with algorithm filter only (lowercase)
    if not results:
        docs_with_scores = vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
            filter={"algorithm": algo_lower},
        )
        for doc, score in docs_with_scores:
            meta = doc.metadata or {}
            results.append(
                RetrievedTheory(
                    chunk_id=meta.get("chunk_id", "unknown"),
                    content=doc.page_content,
                    score=float(score),
                    algorithm=meta.get("algorithm", algorithm),
                    phase_id=meta.get("phase_id"),
                    doc_type=meta.get("doc_type", "unknown"),
                    source_path=meta.get("source_path", "unknown"),
                )
            )
    
    # Fallback 2: if still no results, retry without any metadata filter
    if not results:
        docs_with_scores = vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
        )
        for doc, score in docs_with_scores:
            meta = doc.metadata or {}
            results.append(
                RetrievedTheory(
                    chunk_id=meta.get("chunk_id", "unknown"),
                    content=doc.page_content,
                    score=float(score),
                    algorithm=meta.get("algorithm", algorithm),
                    phase_id=meta.get("phase_id"),
                    doc_type=meta.get("doc_type", "unknown"),
                    source_path=meta.get("source_path", "unknown"),
                )
            )

    return results


def build_prompt(
    snapshot: dict[str, Any],
    theory_chunks: list[RetrievedTheory],
    question: str | None = None,
) -> str:
    """Build a structured system prompt combining snapshot data + theory context."""
    algo = snapshot.get("algorithm", "unknown")
    phase_id = snapshot.get("phase_id", "unknown")
    description = snapshot.get("description", "")
    current_node = snapshot.get("current_node", "N/A")
    visited = snapshot.get("visited", [])
    distances = snapshot.get("distances", {})
    queue = snapshot.get("queue", [])

    lines: list[str] = [
        "Bạn là một gia sư thuật toán chuyên nghiệp. Nhiệm vụ của bạn là giải thích từng bước của thuật toán dựa trên dữ liệu thực tế và lý thuyết.",
        "",
        f"## Thông tin thuật toán",
        f"- Thuật toán: {algo}",
        f"- Phase hiện tại: {phase_id}",
        f"- Mô tả bước: {description}",
        "",
        f"## Trạng thái thực tế (Snapshot từ mô phỏng)",
        f"- Đỉnh đang xét: {current_node}",
        f"- Các đỉnh đã duyệt: {visited}",
        f"- Khoảng cách: {distances}",
        f"- Hàng đợi: {queue}",
        "",
        "## Lý thuyết liên quan (từ tài liệu học thuật)",
    ]

    for i, chunk in enumerate(theory_chunks, 1):
        lines.append(f"### Tài liệu {i} (độ tương đồng: {chunk.score:.2f})")
        lines.append(f"Nguồn: {chunk.source_path}")
        lines.append(f"Nội dung: {chunk.content}")
        lines.append("")

    lines.append("## Yêu cầu")
    lines.append(
        "Hãy giải thích ngắn gọn (2-4 câu) về bước hiện tại của thuật toán. "
        "Sử dụng ngôn ngữ dễ hiểu, liên hệ giữa lý thuyết và trạng thái thực tế. "
        "Nếu có thể, hãy giải thích tại sao thuật toán thực hiện hành động này."
    )

    if question:
        lines.append("")
        lines.append(f"Câu hỏi của học viên: {question}")
        lines.append("Hãy trả lời câu hỏi dựa trên ngữ cảnh ở trên.")

    return "\n".join(lines)