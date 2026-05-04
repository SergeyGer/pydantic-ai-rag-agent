from pydantic_ai import Agent
from pydantic import BaseModel, Field
from typing import List
from database import VectorStore

class SearchResult(BaseModel):
    answer: str = Field(description="Основной ответ на вопрос")
    sections: List[str] = Field(description="Разделы ответа для лучшей организации")
    sources: List[str] = Field(description="Источники информации")
    confidence: float = Field(description="Уверенность в ответе (0-1)", ge=0, le=1)

# Создаем агента с OpenAI
agent = Agent[SearchResult]('openai:gpt-4o')
db = VectorStore()

@agent.tool
def get_company_info(ctx, user_query: str) -> dict:
    """Search for information about company rules and location."""
    return db.search_company_info(user_query)

@agent.tool
def get_policy(ctx, user_query: str) -> dict:
    """Search for corporate policies and regulations."""
    return db.search_policy(user_query)

@agent.tool
def get_faq(ctx, user_query: str) -> dict:
    """Search for frequently asked questions and answers."""
    return db.search_faq(user_query)

@agent.tool
def get_product_data(ctx, user_query: str) -> dict:
    """Search for product information and specifications."""
    return db.search_product_data(user_query)

@agent.tool
def load_web_content(ctx, url: str) -> str:
    """Load and index content from a web URL for future queries."""
    return db.load_from_url(url)