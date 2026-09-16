"""Shared pytest configuration.

The agent builds a real OpenAI-backed vector store on import. To keep the unit
tests fully offline we:
  * make the project root importable as the ``src`` package parent,
  * provide a dummy API key and force an in-memory Qdrant,
  * replace the embedding call with a deterministic in-memory stub,
  * point the default data directory at an empty path.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("OPENAI_API_KEY", "sk-test")

# Always use the in-memory backend, regardless of the developer's local .env.
for _var in ("QDRANT_HOST", "QDRANT_URL", "QDRANT_API_KEY"):
    os.environ.pop(_var, None)

from src import database as _database  # noqa: E402

_DUMMY_VECTOR = [0.1] * _database.VectorStore.VECTOR_SIZE


def _fake_embed_texts(self, texts):
    return [list(_DUMMY_VECTOR) for _ in texts]


_database.VectorStore._embed_texts = _fake_embed_texts
_database.VectorStore._default_data_dir = staticmethod(
    lambda: str(ROOT / "tests" / "_no_data")
)
