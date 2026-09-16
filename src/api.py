"""FastAPI wrapper around the RAG agent."""
import os

import uvicorn
from fastapi import FastAPI, HTTPException
from loguru import logger

from src.agent import agent, db
from src.models import AnswerResponse, LoadUrlRequest, QuestionRequest, SearchResult

app = FastAPI(title="RAG AI Agent API", version="1.0.0")


@app.get("/")
async def root() -> dict:
    return {"message": "RAG AI Agent API", "version": "1.0.0"}


@app.get("/health")
async def health() -> dict:
    """Liveness/readiness probe used by Docker and orchestrators."""
    return {"status": "ok", "indexed_points": db._points_count()}


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest) -> AnswerResponse:
    """Answer a question using the RAG agent."""
    try:
        result = await agent.run(request.question)
    except Exception:
        logger.exception("Failed to answer question: {!r}", request.question)
        raise HTTPException(status_code=500, detail="Failed to answer the question")

    output = result.output
    if isinstance(output, SearchResult):
        return AnswerResponse(
            answer=output.answer,
            sections=output.sections,
            sources=output.sources,
            confidence=output.confidence,
        )

    # Defensive fallback: the model did not return the structured output.
    logger.warning("Agent returned a non-structured output of type {}", type(output).__name__)
    return AnswerResponse(answer=str(output), sections=[], sources=[], confidence=0.5)


@app.post("/load_url")
async def load_url(request: LoadUrlRequest) -> dict:
    """Fetch and index a web URL so it can be queried later."""
    try:
        message = db.load_from_url(request.url)
    except Exception:
        logger.exception("Failed to load URL {}", request.url)
        raise HTTPException(status_code=500, detail="Failed to load the URL")
    return {"message": message}


if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
