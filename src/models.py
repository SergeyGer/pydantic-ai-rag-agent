"""Pydantic models shared between the RAG agent and its API."""
from typing import List

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Structured answer produced by the agent."""

    answer: str = Field(description="Основной ответ на вопрос")
    sections: List[str] = Field(description="Разделы ответа для лучшей организации")
    sources: List[str] = Field(description="Источники информации")
    confidence: float = Field(description="Уверенность в ответе (0-1)", ge=0, le=1)


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    sections: List[str]
    sources: List[str]
    confidence: float


class LoadUrlRequest(BaseModel):
    url: str
