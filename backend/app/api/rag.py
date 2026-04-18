from fastapi import APIRouter

from app.services.rag_query import explain_step

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.get("/explain/{step_id}")
def explain_algorithm_step(step_id: int, question: str | None = None) -> dict:
    """Return hybrid explanation based on snapshot + retrieved theory."""
    return explain_step(step_id=step_id, question=question)
