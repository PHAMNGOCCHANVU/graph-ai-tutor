from fastapi import FastAPI

from app.api.rag import router as rag_router

app = FastAPI(title="Graph AI Tutor Backend")

app.include_router(rag_router)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
