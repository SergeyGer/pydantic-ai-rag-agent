# Contributing

Thanks for your interest in improving **pydantic-ai-rag-agent**! This document
explains how to set up the project, run the checks and submit changes.

## Prerequisites

- Python 3.11+ (the Docker image uses 3.11)
- Docker & Docker Compose (optional, for the containerised stack)
- An OpenAI API key (only needed to actually run the agent end-to-end)

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env             # then set OPENAI_API_KEY
```

## Running the checks

Unit tests run fully offline (embeddings are stubbed, Qdrant is in-memory):

```bash
pytest
```

If you change the Docker files, also validate:

```bash
docker compose config --quiet
docker compose up --build        # requires a valid OPENAI_API_KEY
```

## Project layout

```
src/
  agent.py      # Pydantic-AI agent + retrieval tools (structured output)
  api.py        # FastAPI service (/ask, /load_url, /health)
  database.py   # VectorStore: loading, chunking, embedding, search
  main.py       # interactive CLI
  models.py     # shared Pydantic models
tests/          # pytest unit tests
scripts/        # manual integration scripts (need a running API)
```

## Code style

- Keep the code PEP 8 compatible and fully type-hinted where practical.
- Prefer small, focused functions; add docstrings for public methods.
- Log via `loguru` (`logger.info/warning/error`), avoid bare `print` outside the CLI.
- Never commit secrets. `.env` is git-ignored; document new variables in
  `.env.example` and the README.

## Commit messages

Use short, imperative subjects, optionally following
[Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Qdrant Cloud support via QDRANT_URL
fix: do not crash the service when startup indexing fails
docs: document the /health endpoint
```

## Pull requests

1. Create a topic branch from `main`.
2. Make your change and add/update tests.
3. Ensure `pytest` passes and the CI is green.
4. Update `README.md` / `CHANGELOG.md` when behaviour changes.
5. Fill in the pull-request template and open the PR.

## Reporting bugs & requesting features

Use the GitHub issue templates. For security issues, please **do not** open a
public issue — contact the maintainer directly instead.
