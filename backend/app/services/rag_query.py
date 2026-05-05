from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, APIConnectionError, RateLimitError
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

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
GEMINI_MODEL = "openai/gpt-3.5-turbo"  # OpenRouter model ID (using GPT-3.5 as fallback)


def _get_openrouter_client() -> OpenAI:
    """Create an OpenRouter client (OpenAI-compatible API)."""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Missing OPENROUTER_API_KEY. Add it to backend/.env or environment.")
    return OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_BASE_URL,
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=5, max=30),
    retry=retry_if_exception_type((APIConnectionError, RateLimitError, Exception)),
    reraise=True,
)
def call_llm(prompt: str) -> str:
    """Call OpenRouter Gemini API with retry + exponential backoff (max 30s wait)."""
    client = _get_openrouter_client()
    response = client.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.7,
        top_p=0.9,
        max_tokens=500,
    )
    return response.choices[0].message.content if response.choices[0].message.content else ""


def call_llm_stream(prompt: str):
    """Call OpenRouter Gemini API with streaming."""
    client = _get_openrouter_client()
    stream = client.chat.completions.create(
        model=GEMINI_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0.7,
        top_p=0.9,
        max_tokens=500,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


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

    # 5. Call OpenRouter Gemini API (với retry)
    try:
        answer = call_llm(llm_prompt)
    except (APIConnectionError, RateLimitError) as e:
        return {
            "session_id": session_id,
            "step_index": step_index,
            "algorithm": algorithm,
            "phase_id": phase_id,
            "description": snapshot.get("description", ""),
            "answer": "⚠️ Hệ thống AI đang quá tải hoặc có lỗi kết nối. Trạng thái đồ thị vẫn được cập nhật bình thường.",
            "theory_chunks": [],
            "cached": False,
            "error": str(e)[:200],
        }
    except Exception as e:
        return {
            "session_id": session_id,
            "step_index": step_index,
            "algorithm": algorithm,
            "phase_id": phase_id,
            "description": snapshot.get("description", ""),
            "answer": f"⚠️ Lỗi AI: {str(e)[:200]}",
            "theory_chunks": [],
            "cached": False,
            "error": str(e)[:200],
        }

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

    # 5. Stream Gemini response (với try/catch để không crash)
    full_text = ""
    try:
        for text_chunk in call_llm_stream(llm_prompt):
            full_text += text_chunk
            yield text_chunk
    except (APIConnectionError, RateLimitError) as e:
        fallback = "⚠️ Hệ thống AI đang quá tải hoặc có lỗi kết nối. Trạng thái đồ thị vẫn được cập nhật bình thường."
        yield fallback
        full_text = fallback
    except Exception as e:
        fallback = f"⚠️ Lỗi AI: {str(e)[:200]}"
        yield fallback
        full_text = fallback

    # 6. Lưu cache
    if full_text:
        _save_explanation_cache(session_id, step_index, full_text, db)