import asyncio
from dotenv import load_dotenv
from agent import agent

load_dotenv()

async def main():
    print("--- Smartclip AI Agent ---")
    question = "Where is the office located and what about the 4-day week?"
    result = await agent.run(question)
    print(f"Question: {question}")
    print(f"Answer: {result.output}")
    
if __name__ == "__main__":
    asyncio.run(main())
