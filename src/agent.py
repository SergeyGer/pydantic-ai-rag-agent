"""Pydantic-AI agent exposing retrieval tools backed by the local vector store."""
from loguru import logger
from pydantic_ai import Agent

from src.database import VectorStore
from src.models import SearchResult

INSTRUCTIONS = (
    "Ты — корпоративный ассистент. Отвечай на вопросы пользователя, опираясь только "
    "на данные, полученные через инструменты поиска по базе знаний. Всегда указывай "
    "источники и оценивай уверенность в ответе числом от 0 до 1."
)


def build_agent(db: "VectorStore") -> Agent:
    """Create an agent configured for structured output and register its tools."""
    agent = Agent(
        "openai:gpt-4o",
        output_type=SearchResult,
        instructions=INSTRUCTIONS,
    )

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

    return agent


# Module-level singletons shared by the CLI and the API.
db = VectorStore()
agent = build_agent(db)
logger.debug("RAG agent initialised with {} indexed points", db._points_count())
