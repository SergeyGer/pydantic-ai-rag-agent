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
    return db.search_company_info(user_query)

@agent.tool
def get_policy(ctx, user_query: str) -> str:
    """Search for corporate policies and regulations."""
    return db.search_policy(user_query)

@agent.tool
def get_faq(ctx, user_query: str) -> str:
    """Search for frequently asked questions and answers."""
    return db.search_faq(user_query)

@agent.tool
def get_product_data(ctx, user_query: str) -> str:
    """Search for product information and specifications."""
    return db.search_product_data(user_query)