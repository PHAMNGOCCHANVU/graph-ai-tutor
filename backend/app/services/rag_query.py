from __future__ import annotations

from app.services.rag_orchestrator import build_prompt, retrieve_snapshot, retrieve_theory


def call_llm(prompt: str) -> str:
    # Placeholder: replace with LangChain + Gemini invocation.
    return f"[Demo response] Explanation generated for prompt:\n{prompt}"


def explain_step(step_id: int, question: str | None = None) -> dict:
    snapshot = retrieve_snapshot(step_id)
    theory_chunks = retrieve_theory(snapshot.get("algorithm", "graph"), question)
    llm_prompt = build_prompt(snapshot, theory_chunks, question)
    answer = call_llm(llm_prompt)

    return {
        "step_id": step_id,
        "answer": answer,
        "snapshot": snapshot,
        "theory_chunks": [
            {"chunk_id": chunk.chunk_id, "score": chunk.score}
            for chunk in theory_chunks
        ],
    }
