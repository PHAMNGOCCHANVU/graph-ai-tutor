from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import GenerateContentConfig
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.models import models
from app.services.rag_orchestrator import (
    RetrievedTheory,
    build_prompt,
    retrieve_snapshot,
    retrieve_theory,
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash-lite"


def _get_gemini_client() -> Client:
    """Create a Gemini API client."""
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY. Add it to backend/.env or environment.")
    return Client(api_key=GEMINI_API_KEY)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def call_llm(prompt: str) -> str:
    """Call Gemini API with retry + exponential backoff."""
    client = _get_gemini_client()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=GenerateContentConfig(
            max_output_tokens=500,
            temperature=0.7,
            top_p=0.9,
        ),
    )
    return response.text if response.text else ""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def call_llm_stream(prompt: str):
    """Call Gemini API with streaming + retry + exponential backoff."""
    client = _get_gemini_client()
    stream = client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=prompt,
        config=GenerateContentConfig(
            max_output_tokens=500,
            temperature=0.7,
            top_p=0.9,
        ),
    )
    for chunk in stream:
        if chunk.text:
            yield chunk.text


def _get_cached_explanation(session_id: str, step_index: int, db: Session) -> str | None:
    """Kiểm tra cache trong DB trước khi gọi Gemini."""
    cached = (
        db.query(models.AiExplanation)
        .filter(
            models.AiExplanation.session_id == session_id,
            models.AiExplanation.step_index == step_index,
        )
        .first()
    )
    return cached.explanation_text if cached else None


def _save_explanation_cache(session_id: str, step_index: int, text: str, db: Session):
    """Lưu lời giải thích vào DB cache."""
    cached = models.AiExplanation(
        session_id=session_id,
        step_index=step_index,
        explanation_text=text,
    )
    db.add(cached)
    db.commit()


def explain_step(
    session_id: str,
    step_index: int,
    db: Session,
    question: str | None = None,
) -> dict[str, Any]:
    """Full RAG pipeline: check cache -> fetch snapshot -> retrieve theory -> build prompt -> call LLM."""

    # 1. Kiểm tra cache trước
    cached_answer = _get_cached_explanation(session_id, step_index, db)
    if cached_answer:
        # Vẫn fetch snapshot để lấy metadata
        snapshot = retrieve_snapshot(session_id, step_index, db)
        return {
            "session_id": session_id,
            "step_index": step_index,
            "algorithm": snapshot.get("algorithm", "graph"),
            "phase_id": snapshot.get("phase_id"),
            "description": snapshot.get("description", ""),
            "answer": cached_answer,
            "theory_chunks": [],
            "cached": True,
        }

    # 2. Fetch real snapshot from SQL
    snapshot = retrieve_snapshot(session_id, step_index, db)

    # 3. Retrieve relevant theory from ChromaDB
    algorithm = snapshot.get("algorithm", "graph")
    phase_id = snapshot.get("phase_id")
    theory_chunks = retrieve_theory(
        algorithm=algorithm,
        phase_id=phase_id,
        question=question,
        top_k=3,
    )

    # 4. Build the prompt
    llm_prompt = build_prompt(snapshot, theory_chunks, question)

    # 5. Call Gemini API (với retry)
    answer = call_llm(llm_prompt)

    # 6. Lưu cache
    if answer:
        _save_explanation_cache(session_id, step_index, answer, db)

    return {
        "session_id": session_id,
        "step_index": step_index,
        "algorithm": algorithm,
        "phase_id": phase_id,
        "description": snapshot.get("description", ""),
        "answer": answer,
        "theory_chunks": [
            {
                "chunk_id": chunk.chunk_id,
                "score": chunk.score,
                "source_path": chunk.source_path,
                "phase_id": chunk.phase_id,
                "doc_type": chunk.doc_type,
            }
            for chunk in theory_chunks
        ],
        "cached": False,
    }


def explain_step_stream(
    session_id: str,
    step_index: int,
    db: Session,
    question: str | None = None,
):
    """Streaming version: check cache -> fetch snapshot -> retrieve theory -> stream Gemini."""

    # 1. Kiểm tra cache trước
    cached_answer = _get_cached_explanation(session_id, step_index, db)
    if cached_answer:
        # Stream từ cache (yield toàn bộ text như 1 chunk)
        yield cached_answer
        return

    # 2. Fetch real snapshot from SQL
    snapshot = retrieve_snapshot(session_id, step_index, db)

    # 3. Retrieve relevant theory from ChromaDB
    algorithm = snapshot.get("algorithm", "graph")
    phase_id = snapshot.get("phase_id")
    theory_chunks = retrieve_theory(
        algorithm=algorithm,
        phase_id=phase_id,
        question=question,
        top_k=3,
    )

    # 4. Build the prompt
    llm_prompt = build_prompt(snapshot, theory_chunks, question)

    # 5. Stream Gemini response (với retry)
    full_text = ""
    for text_chunk in call_llm_stream(llm_prompt):
        full_text += text_chunk
        yield text_chunk

    # 6. Lưu cache
    if full_text:
        _save_explanation_cache(session_id, step_index, full_text, db)