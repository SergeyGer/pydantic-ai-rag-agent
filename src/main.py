import asyncio
from dotenv import load_dotenv
from agent import agent

load_dotenv()

async def main():
    print("--- Smartclip AI Agent ---")
    while True:
        question = await asyncio.to_thread(input, "Введите вопрос (или 'exit' для выхода): ")
        if question.lower() == 'exit':
            break
        result = await agent.run(question)
        print(f"Вопрос: {question}")
        print(f"Ответ: {result.output}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
