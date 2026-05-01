from __future__ import annotations

import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.db.session import get_db
from app.services.rag_query import explain_step, explain_step_stream

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.get("/explain/{session_id}")
def explain_algorithm_step(
    session_id: str,
    step_index: int = Query(..., description="Step index to explain"),
    question: str | None = Query(None, description="Optional student question"),
    db: Session = Depends(get_db),
) -> dict:
    """Return hybrid explanation based on snapshot + retrieved theory + Gemini.

    - session_id: The algorithm session ID (e.g. sess-abc12345)
    - step_index: The step number to explain
    - question: Optional follow-up question from the student
    """
    try:
        result = explain_step(
            session_id=session_id,
            step_index=step_index,
            db=db,
            question=question,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/explain/{session_id}/stream")
async def explain_algorithm_step_stream(
    session_id: str,
    step_index: int = Query(..., description="Step index to explain"),
    question: str | None = Query(None, description="Optional student question"),
    db: Session = Depends(get_db),
):
    """Streaming SSE endpoint for real-time explanation.

    Returns Server-Sent Events with text chunks from Gemini.
    """
    try:
        async def event_generator() -> AsyncGenerator[str, None]:
            # Send initial metadata event
            meta = {
                "session_id": session_id,
                "step_index": step_index,
            }
            yield f"event: meta\ndata: {json.dumps(meta, ensure_ascii=False)}\n\n"

            # Stream text chunks from Gemini
            for text_chunk in explain_step_stream(
                session_id=session_id,
                step_index=step_index,
                db=db,
                question=question,
            ):
                yield f"event: chunk\ndata: {json.dumps({'text': text_chunk}, ensure_ascii=False)}\n\n"

            # Send done event
            yield "event: done\ndata: {}\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))