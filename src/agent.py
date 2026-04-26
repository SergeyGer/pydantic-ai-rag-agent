from pydantic_ai import Agent
from pydantic import BaseModel
from database import VectorStore

class SearchResult(BaseModel):
    answer: str
    source: str

# Создаем агента с OpenAI
agent = Agent[SearchResult]('openai:gpt-4o')
db = VectorStore()

@agent.tool
def get_company_info(ctx, user_query: str) -> str:
    """Search for information about company rules and location."""
    return db.search_docs(user_query)