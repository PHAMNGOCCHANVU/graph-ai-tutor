from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievedTheory:
    chunk_id: str
    content: str
    score: float


def retrieve_snapshot(step_id: int) -> dict:
    # Placeholder: fetch snapshot from SQL store (PostgreSQL/SQLite).
    return {
        "step_id": step_id,
        "algorithm": "bfs",
        "state": {
            "current_node": "A",
            "visited": ["A", "B"],
            "queue": ["C", "D"],
        },
    }


def retrieve_theory(algorithm: str, question: str | None = None) -> list[RetrievedTheory]:
    # Placeholder: retrieve relevant chunks from ChromaDB.
    query = question or f"Explain the current step of {algorithm}."
    return [
        RetrievedTheory(
            chunk_id="theory-001",
            content=f"Theory context for query: {query}",
            score=0.82,
        )
    ]


def build_prompt(snapshot: dict, theory_chunks: list[RetrievedTheory], question: str | None) -> str:
    lines = [
        "You are an algorithm tutor.",
        f"Step ID: {snapshot.get('step_id')}",
        f"Algorithm: {snapshot.get('algorithm')}",
        f"State: {snapshot.get('state')}",
        "Theory:",
    ]
    lines.extend([f"- {chunk.content}" for chunk in theory_chunks])
    if question:
        lines.append(f"Student question: {question}")
    return "\n".join(lines)
