from pathlib import Path

import pytest

from src import database
from src.database import SUPPORTED_EXTENSIONS, VectorStore, build_qdrant_client


@pytest.fixture
def store():
    # No data loading: tests drive indexing explicitly via _index_document.
    return VectorStore(load_data=False)


def test_supported_extensions_include_docx():
    assert ".docx" in SUPPORTED_EXTENSIONS


def test_chunk_short_text_is_single_chunk(store):
    document = {"source": "s.txt", "content": "hello", "doc_type": "general", "metadata": {}}
    chunks = store._chunk_text(document)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "hello"


def test_chunk_long_text_produces_overlapping_chunks(store):
    text = "abcdefghij" * 200  # 2000 chars -> more than CHUNK_SIZE
    document = {"source": "s.txt", "content": text, "doc_type": "general", "metadata": {}}
    chunks = store._chunk_text(document)
    assert len(chunks) > 1
    overlap = VectorStore.CHUNK_OVERLAP
    assert chunks[0]["text"][-overlap:] == chunks[1]["text"][:overlap]


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("Company_info.txt", "company_info"),
        ("office_loc.md", "company_info"),
        ("policy.txt", "policy"),
        ("faq.md", "faq"),
        ("product_spec.txt", "product_data"),
        ("data.json", "data"),
        ("manual.pdf", "document"),
        ("notes.txt", "general"),
    ],
)
def test_guess_doc_type(store, filename, expected):
    assert store._guess_doc_type(Path(filename)) == expected


def test_read_json_roundtrip(store, tmp_path):
    path = tmp_path / "d.json"
    path.write_text('{"a": 1}', encoding="utf-8")
    assert '"a": 1' in store._read_json(path)


def test_index_and_search_returns_sources(store):
    store._index_document(
        {"source": "doc.txt", "content": "hello world", "doc_type": "faq", "metadata": {}}
    )
    result = store._search("hello", doc_type="faq")
    assert result["sources"] == ["doc.txt"]
    assert 0.0 <= result["confidence"] <= 1.0


def test_search_on_empty_collection_is_safe(store):
    result = store._search("anything")
    assert result["sources"] == []
    assert result["confidence"] == 0.0


class _CapturingQdrantClient:
    """Stand-in for QdrantClient that records how it was constructed."""

    calls: list = []

    def __init__(self, *args, **kwargs):
        _CapturingQdrantClient.calls.append((args, kwargs))


def test_build_qdrant_client_uses_in_memory_by_default(monkeypatch):
    _CapturingQdrantClient.calls = []
    monkeypatch.delenv("QDRANT_HOST", raising=False)
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.setattr(database, "QdrantClient", _CapturingQdrantClient)

    build_qdrant_client()

    assert _CapturingQdrantClient.calls == [((":memory:",), {})]


def test_build_qdrant_client_uses_host_and_port(monkeypatch):
    _CapturingQdrantClient.calls = []
    monkeypatch.setenv("QDRANT_HOST", "qdrant")
    monkeypatch.setenv("QDRANT_PORT", "6333")
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.setattr(database, "QdrantClient", _CapturingQdrantClient)

    build_qdrant_client()

    args, kwargs = _CapturingQdrantClient.calls[0]
    assert args == ()
    assert kwargs["host"] == "qdrant"
    assert kwargs["port"] == 6333


def test_build_qdrant_client_prefers_url(monkeypatch):
    _CapturingQdrantClient.calls = []
    monkeypatch.setenv("QDRANT_URL", "https://example.qdrant.io:6333")
    monkeypatch.setenv("QDRANT_HOST", "ignored")
    monkeypatch.setenv("QDRANT_API_KEY", "secret")
    monkeypatch.setattr(database, "QdrantClient", _CapturingQdrantClient)

    build_qdrant_client()

    args, kwargs = _CapturingQdrantClient.calls[0]
    assert kwargs["url"] == "https://example.qdrant.io:6333"
    assert kwargs["api_key"] == "secret"


def test_startup_indexing_failure_is_non_fatal(monkeypatch):
    def _boom(self, data_dir):
        raise RuntimeError("embedding backend unavailable")

    monkeypatch.setattr(VectorStore, "load_documents", _boom)

    # Constructing the store must not raise even though the initial indexing fails.
    store = VectorStore(load_data=True, data_dir="unused")
    assert store is not None
