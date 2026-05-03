# Pydantic-AI RAG Agent
AI Agent for Documentation Analysis

## Overview
This is a  sample of RAG (Retrieval-Augmented Generation) agent. It demonstrates structured output validation and tool-calling using **Pydantic-AI**.

## Tech Stack
- **Framework:** Pydantic-AI
- **LLM:** OpenAI GPT-4o
- **Vector Storage:** Qdrant (In-memory for demo)
- **Environment:** Docker & Docker Compose

## How to Run
1. Add your `OPENAI_API_KEY` to `.env`.
2. Run via Docker:
   ```bash
   docker-compose up --build
   ```
