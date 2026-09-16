from fastapi.testclient import TestClient

from src.api import app
from src.models import SearchResult

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "RAG AI Agent API"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["indexed_points"], int)


def test_ask_returns_structured_answer(monkeypatch):
    class _FakeResult:
        output = SearchResult(answer="42", sections=["a"], sources=["doc"], confidence=0.9)

    class _FakeAgent:
        async def run(self, question):
            return _FakeResult()

    monkeypatch.setattr("src.api.agent", _FakeAgent())

    response = client.post("/ask", json={"question": "meaning of life?"})
    assert response.status_code == 200
    assert response.json() == {
        "answer": "42",
        "sections": ["a"],
        "sources": ["doc"],
        "confidence": 0.9,
    }


def test_load_url_calls_vector_store(monkeypatch):
    class _FakeDb:
        def load_from_url(self, url):
            return f"Loaded content from {url}"

    monkeypatch.setattr("src.api.db", _FakeDb())

    response = client.post("/load_url", json={"url": "https://example.com"})
    assert response.status_code == 200
    assert response.json()["message"] == "Loaded content from https://example.com"
