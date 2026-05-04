import asyncio
from dotenv import load_dotenv
from agent import agent

load_dotenv()

async def main():
    print("--- RAG AI Agent ---")
    while True:
        question = await asyncio.to_thread(input, "Enter your question (or 'exit' to quit): ")
        if question.lower() == 'exit':
            break
        result = await agent.run(question)
        print(f"Question: {question}")
        print(f"Answer: {result.output}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
