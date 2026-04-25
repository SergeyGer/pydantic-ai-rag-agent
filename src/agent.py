from pydantic_ai import Agent
from pydantic import BaseModel
from src.database import VectorStore

class SearchResult(BaseModel):
    answer: str
    source: str

# Создаем агента
agent = Agent('openai:gpt-4o', result_type=SearchResult)
db = VectorStore()

@agent.tool
def get_company_info(ctx, user_query: str) -> str:
    """Search for information about company rules and location."""
    return db.search_docs(user_query)
