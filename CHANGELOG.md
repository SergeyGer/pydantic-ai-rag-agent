# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-09-16

### Added
- Structured output (`SearchResult`) for the agent: `/ask` returns a validated
  `answer`, `sections`, `sources` and `confidence`.
- `GET /health` liveness/readiness probe (used by the Docker health check).
- External Qdrant support via `QDRANT_URL` / `QDRANT_HOST` / `QDRANT_PORT` /
  `QDRANT_API_KEY` / `QDRANT_COLLECTION`, with an in-memory fallback.
- `.env.example` template plus `DATA_DIR` and `API_PORT` configuration.
- `.docx` document support (via `python-docx`).
- Docker Compose stack with a `qdrant` service, health checks and
  `depends_on: qdrant: condition: service_healthy`.
- Offline unit-test suite (`tests/`, `pytest.ini`).
- GitHub Actions CI, release pipeline (GitHub Release + GHCR image) and Dependabot.
- `CONTRIBUTING.md`, `CHANGELOG.md`, pull-request and issue templates.

### Changed
- Shared Pydantic models moved to `src/models.py`.
- `src` is now a proper package; run via `python -m src.api` / `python -m src.main`.
- All dependency versions pinned in `requirements.txt`.
- Container hardened: non-root user, read-only root filesystem, `tmpfs` `/tmp`,
  `no-new-privileges`, read-only `data/` mount.
- Manual integration scripts moved from the repo root to `scripts/`.
- Qdrant image pinned (`v1.17.1`) to match `qdrant-client`.

### Fixed
- Structured output was not applied (`Agent[SearchResult](...)` set the dependency
  type instead of the output type).
- Port mismatch between `docker-compose.yml` (8000) and the API (8001).
- Startup indexing is now best-effort: failures are logged with a traceback and no
  longer crash-loop the service.
- Document-directory resolution no longer depends on the working directory; the
  container uses `/app/data`.
- `.env` is excluded from the Docker image via `.dockerignore`.
- `confidence` is clamped to the `0..1` range.

### Removed
- Debug script `inspect_qdrant.py`.
- Scattered root-level integration scripts (replaced by `scripts/` and `tests/`).

[Unreleased]: https://github.com/SergeyGer/pydantic-ai-rag-agent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/SergeyGer/pydantic-ai-rag-agent/releases/tag/v1.0.0
