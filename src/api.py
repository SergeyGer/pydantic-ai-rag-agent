from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import agent
import asyncio

app = FastAPI(title="RAG AI Agent API", version="1.0.0")

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sections: list[str]
    sources: list[str]
    confidence: float

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        result = await agent.run(request.question)
        # result.output может быть str или dict
        if hasattr(result.output, 'answer'):
            return AnswerResponse(
                answer=result.output.answer,
                sections=result.output.sections,
                sources=result.output.sources,
                confidence=result.output.confidence
            )
        else:
            # Если str, вернуть как answer
            return AnswerResponse(
                answer=str(result.output),
                sections=[],
                sources=[],
                confidence=0.5
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class LoadUrlRequest(BaseModel):
    url: str

@app.post("/load_url")
async def load_url(request: LoadUrlRequest):
    try:
        result = await agent.run(f"Load content from {request.url}")
        return {"message": "Content loaded", "result": str(result.output)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "RAG AI Agent API", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)