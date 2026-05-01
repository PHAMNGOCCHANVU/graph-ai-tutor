from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import GenerateContentConfig
from sqlalchemy.orm import Session

from app.services.rag_orchestrator import (
    RetrievedTheory,
    build_prompt,
    retrieve_snapshot,
    retrieve_theory,
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.0-flash-lite"  # Fast model suitable for real-time explanations


def _get_gemini_client() -> Client:
    """Create a Gemini API client."""
    if not GEMINI_API_KEY:
        raise RuntimeError("Missing GEMINI_API_KEY. Add it to backend/.env or environment.")
    return Client(api_key=GEMINI_API_KEY)


def call_llm(prompt: str) -> str:
    """Call Gemini API with the given prompt and return the response text."""
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


def call_llm_stream(prompt: str):
    """Call Gemini API with streaming and yield text chunks."""
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


def explain_step(
    session_id: str,
    step_index: int,
    db: Session,
    question: str | None = None,
) -> dict[str, Any]:
    """Full RAG pipeline: fetch snapshot -> retrieve theory -> build prompt -> call LLM."""
    # 1. Fetch real snapshot from SQL
    snapshot = retrieve_snapshot(session_id, step_index, db)

    # 2. Retrieve relevant theory from ChromaDB
    algorithm = snapshot.get("algorithm", "graph")
    phase_id = snapshot.get("phase_id")
    theory_chunks = retrieve_theory(
        algorithm=algorithm,
        phase_id=phase_id,
        question=question,
        top_k=3,
    )

    # 3. Build the prompt
    llm_prompt = build_prompt(snapshot, theory_chunks, question)

    # 4. Call Gemini API
    answer = call_llm(llm_prompt)

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
    }


def explain_step_stream(
    session_id: str,
    step_index: int,
    db: Session,
    question: str | None = None,
):
    """Streaming version: yield SSE-formatted text chunks from Gemini."""
    # 1. Fetch real snapshot from SQL
    snapshot = retrieve_snapshot(session_id, step_index, db)

    # 2. Retrieve relevant theory from ChromaDB
    algorithm = snapshot.get("algorithm", "graph")
    phase_id = snapshot.get("phase_id")
    theory_chunks = retrieve_theory(
        algorithm=algorithm,
        phase_id=phase_id,
        question=question,
        top_k=3,
    )

    # 3. Build the prompt
    llm_prompt = build_prompt(snapshot, theory_chunks, question)

    # 4. Stream Gemini response
    for text_chunk in call_llm_stream(llm_prompt):
        yield text_chunk