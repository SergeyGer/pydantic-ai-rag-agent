"""Manual smoke test: load web content and query it with the agent.

Run from the project root:

    python -m scripts.test_web_scraping

Note: this imports the shared ``db`` singleton from ``src.agent`` (instead of
creating a second, isolated ``VectorStore``) so the agent can actually see the
content that was loaded here.
"""
import asyncio

from src.agent import agent, db


async def main() -> None:
    test_urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/html",
        "https://example.com",
    ]

    print("=== Web Scraping Test ===\n")

    for url in test_urls:
        print(f"Loading: {url}")
        print(f"Result: {db.load_from_url(url)}\n")

    test_questions = [
        "What information is available in the loaded content?",
        "Summarize what you found from the web content.",
        "What is the main content type from the URLs?",
    ]

    print("\n=== Testing Questions ===\n")
    for question in test_questions:
        result = await agent.run(question)
        print(f"Question: {question}")
        print(f"Answer: {result.output.answer}")
        print(f"Confidence: {result.output.confidence}")
        print("-" * 50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
