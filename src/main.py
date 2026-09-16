"""Interactive CLI for the RAG agent."""
import asyncio

from dotenv import load_dotenv
from loguru import logger

from src.agent import agent

load_dotenv()


async def main() -> None:
    logger.info("RAG AI Agent CLI started (type 'exit' to quit)")
    while True:
        question = await asyncio.to_thread(input, "Enter your question (or 'exit' to quit): ")
        if question.strip().lower() == "exit":
            break
        if not question.strip():
            continue

        result = await agent.run(question)
        output = result.output
        print(f"Question: {question}")
        print(f"Answer: {output.answer}")
        print(f"Sources: {output.sources}")
        print(f"Confidence: {output.confidence}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
