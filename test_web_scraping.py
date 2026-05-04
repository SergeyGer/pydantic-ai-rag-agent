import asyncio
import sys
sys.path.append("src")
from agent import agent
from database import VectorStore

async def test_web_scraping():
    db = VectorStore()
    
    # Тестовые URLs
    test_urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/html",
        "https://example.com",
    ]
    
    print("=== Web Scraping Test ===\n")
    
    # Тест 1: Загрузка контента из URL
    for url in test_urls:
        print(f"Loading: {url}")
        result = db.load_from_url(url)
        print(f"Result: {result}\n")
    
    # Тест 2: Задание вопросов на основе загруженного контента
    test_questions = [
        "What information is available in the loaded content?",
        "Summarize what you found from the web content.",
        "What is the main content type from the URLs?",
    ]
    
    print("\n=== Testing Questions ===\n")
    for question in test_questions:
        print(f"Question: {question}")
        result = await agent.run(question)
        print(f"Answer: {result.output.answer}\n")
        print(f"Confidence: {result.output.confidence}\n")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_web_scraping())
