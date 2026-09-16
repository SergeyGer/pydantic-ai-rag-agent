"""Vector store used by the RAG agent.

Loads local documents (txt, md, csv, pdf, json, docx) and web pages, splits them
into chunks and indexes OpenAI embeddings for semantic search.

Storage backend is chosen from the environment:
  * ``QDRANT_URL``  - full URL of a hosted Qdrant instance (e.g. Qdrant Cloud);
  * ``QDRANT_HOST`` - host (+ ``QDRANT_PORT``) of a Qdrant server;
  * otherwise an in-memory Qdrant is used (data is not persisted).
"""
import csv
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger
from openai import OpenAI
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

try:  # python-docx is optional and only required to index .docx files
    from docx import Document
except ImportError:  # pragma: no cover - exercised only without the extra dependency
    Document = None

SUPPORTED_EXTENSIONS = {".txt", ".md", ".csv", ".pdf", ".json", ".docx"}

DEFAULT_COLLECTION = "documents"


def build_qdrant_client() -> QdrantClient:
    """Create a Qdrant client based on the environment configuration.

    Falls back to a fully in-memory instance when no external server is
    configured, which keeps the demo (and the test-suite) self-contained.
    """
    url = os.getenv("QDRANT_URL", "").strip()
    host = os.getenv("QDRANT_HOST", "").strip()
    api_key = os.getenv("QDRANT_API_KEY") or None

    if url:
        logger.info("Using external Qdrant via URL '{}'", url)
        return QdrantClient(url=url, api_key=api_key)

    if host:
        port = int(os.getenv("QDRANT_PORT", "6333"))
        logger.info("Using external Qdrant at {}:{}", host, port)
        return QdrantClient(host=host, port=port, api_key=api_key)

    logger.info("QDRANT_HOST/QDRANT_URL not set - using in-memory Qdrant (data is not persisted)")
    return QdrantClient(":memory:")


class VectorStore:
    COLLECTION_NAME = DEFAULT_COLLECTION
    EMBEDDING_MODEL = "text-embedding-3-large"
    VECTOR_SIZE = 3072
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

    def __init__(
        self,
        data_dir: Optional[str] = None,
        load_data: bool = True,
        collection_name: Optional[str] = None,
    ):
        self.COLLECTION_NAME = collection_name or os.getenv("QDRANT_COLLECTION", DEFAULT_COLLECTION)
        self.client = build_qdrant_client()
        self.openai = OpenAI()
        self._ensure_collection()
        if load_data:
            self._load_documents_safely(data_dir or self._default_data_dir())

    def _load_documents_safely(self, data_dir: str) -> None:
        """Index the knowledge base at startup without crashing the service.

        Failures here (invalid OPENAI_API_KEY, a transient OpenAI/network outage,
        an unreadable file, ...) must not prevent the API/CLI from starting: we
        log a detailed error and continue with a possibly empty index.
        """
        try:
            self.load_documents(data_dir)
        except Exception as exc:
            logger.exception(
                "Failed to index the knowledge base from '{}'. The service will "
                "start with a possibly empty/partial index. Likely causes: invalid "
                "OPENAI_API_KEY, no network access to OpenAI, or unreadable files "
                "in the data directory. Underlying error: {}: {}",
                data_dir,
                type(exc).__name__,
                exc,
            )

    @staticmethod
    def _default_data_dir() -> str:
        # <project_root>/data, resolved independently of the working directory
        env_dir = os.getenv("DATA_DIR")
        if env_dir:
            return env_dir
        return str(Path(__file__).resolve().parent.parent / "data")

    def _ensure_collection(self, retries: int = 5, delay: float = 2.0) -> None:
        """Make sure the collection exists, retrying while an external Qdrant starts up."""
        last_error: Optional[Exception] = None
        for attempt in range(1, retries + 1):
            try:
                self.client.get_collection(self.COLLECTION_NAME)
                return
            except Exception:
                try:
                    self.client.create_collection(
                        collection_name=self.COLLECTION_NAME,
                        vectors_config=rest.VectorParams(
                            size=self.VECTOR_SIZE,
                            distance=rest.Distance.COSINE,
                        ),
                    )
                    logger.info("Created Qdrant collection '{}'", self.COLLECTION_NAME)
                    return
                except Exception as exc:  # pragma: no cover - exercised with a remote backend
                    last_error = exc
                    if attempt < retries:
                        logger.warning(
                            "Qdrant not ready (attempt {}/{}): {}", attempt, retries, exc
                        )
                        time.sleep(delay)
        raise RuntimeError(
            f"Could not initialise Qdrant collection '{self.COLLECTION_NAME}': {last_error}"
        )

    def _points_count(self) -> int:
        try:
            return self.client.get_collection(self.COLLECTION_NAME).points_count or 0
        except Exception:
            return 0

    def load_documents(self, data_dir: str) -> None:
        if self._points_count() > 0:
            logger.debug("Collection already contains points, skipping document loading")
            return

        path = Path(data_dir)
        if not path.exists():
            logger.warning("Data directory '{}' does not exist, nothing to load", path)
            return

        indexed = 0
        for file_path in sorted(path.rglob("*")):
            if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            text = self._read_file(file_path)
            if not text:
                continue

            self._index_document(
                {
                    "source": file_path.name,
                    "content": text,
                    "doc_type": self._guess_doc_type(file_path),
                    "metadata": {
                        "file_path": str(file_path),
                        "modified_time": file_path.stat().st_mtime,
                    },
                }
            )
            indexed += 1

        logger.info("Indexed {} document(s) from '{}'", indexed, path)

    def _index_document(self, document: Dict[str, Any]) -> None:
        """Chunk a document, embed it and upsert the resulting points."""
        chunks = self._chunk_text(document)
        if not chunks:
            return

        embeddings = self._embed_texts([chunk["text"] for chunk in chunks])
        points = [
            rest.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "source": chunk["source"],
                    "doc_type": chunk["doc_type"],
                    "text": chunk["text"],
                    "metadata": chunk["metadata"],
                },
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]
        self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)

    def load_from_url(self, url: str, doc_type: str = "web") -> str:
        text = self._read_url(url)
        if not text or text.startswith("Error"):
            logger.warning("Failed to load web content from {}", url)
            return text  # propagate the error message back to the caller

        self._index_document(
            {
                "source": url,
                "content": text,
                "doc_type": doc_type,
                "metadata": {
                    "url": url,
                    "fetched_time": datetime.now(timezone.utc).isoformat(),
                },
            }
        )
        logger.info("Loaded web content from {}", url)
        return f"Loaded content from {url}"

    def _read_file(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            return self._read_csv(file_path)
        elif suffix == ".pdf":
            return self._read_pdf(file_path)
        elif suffix == ".json":
            return self._read_json(file_path)
        elif suffix == ".docx":
            return self._read_docx(file_path)
        return file_path.read_text(encoding="utf-8", errors="ignore")

    def _read_csv(self, file_path: Path) -> str:
        lines = []
        with file_path.open("r", encoding="utf-8", errors="ignore") as csv_file:
            for row in csv_file:
                lines.append(row.strip())
        return "\n".join(lines)

    def _read_pdf(self, file_path: Path) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()

    def _read_json(self, file_path: Path) -> str:
        with file_path.open("r", encoding="utf-8", errors="ignore") as json_file:
            data = json.load(json_file)
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _read_docx(self, file_path: Path) -> str:
        if Document is None:
            logger.warning(
                "python-docx is not installed - skipping '{}'. Add 'python-docx' to requirements.",
                file_path.name,
            )
            return ""
        document = Document(str(file_path))
        return "\n".join(p.text for p in document.paragraphs if p.text).strip()

    def _read_url(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            content_type = response.headers.get('content-type', '').lower()
            if 'json' in content_type:
                data = response.json()
                return json.dumps(data, indent=2, ensure_ascii=False)
            elif 'html' in content_type or 'text' in content_type:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Извлечь текст из параграфов, заголовков
                text = soup.get_text(separator='\n', strip=True)
                return text
            else:
                return response.text
        except Exception as e:
            return f"Error fetching URL {url}: {str(e)}"

    def _guess_doc_type(self, file_path: Path) -> str:
        name = file_path.stem.lower()
        suffix = file_path.suffix.lower()
        if "policy" in name:
            return "policy"
        if "faq" in name:
            return "faq"
        if "product" in name or "spec" in name:
            return "product_data"
        if "company" in name or "office" in name:
            return "company_info"
        if suffix == ".json":
            return "data"
        if suffix == ".pdf":
            return "document"
        return "general"

    def _chunk_text(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        text = document["content"].replace("\r\n", "\n").strip()
        if len(text) <= self.CHUNK_SIZE:
            return [
                {
                    "text": text,
                    "source": document["source"],
                    "doc_type": document["doc_type"],
                    "metadata": document["metadata"],
                }
            ]

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.CHUNK_SIZE, len(text))
            chunk_text = text[start:end]
            chunks.append(
                {
                    "text": chunk_text,
                    "source": document["source"],
                    "doc_type": document["doc_type"],
                    "metadata": document["metadata"],
                }
            )
            start += self.CHUNK_SIZE - self.CHUNK_OVERLAP
        return chunks

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = self.openai.embeddings.create(
            model=self.EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]

    def _search(self, query: str, doc_type: Optional[str] = None, top_k: int = 3) -> dict:
        if not query:
            return {"answer": "", "sections": [], "sources": [], "confidence": 0.0}

        query_embedding = self._embed_texts([query])[0]
        search_filter = None
        if doc_type:
            search_filter = rest.Filter(
                must=[
                    rest.FieldCondition(
                        key="doc_type",
                        match=rest.MatchValue(value=doc_type),
                    )
                ]
            )

        hits = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_embedding,
            query_filter=search_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        if not hits or not hits.points:
            return {"answer": "No relevant documents found.", "sections": [], "sources": [], "confidence": 0.0}

        sections = []
        sources = []
        scores = []
        for hit in hits.points:
            payload = hit.payload or {}
            payload_text = payload.get("text", "")
            source = payload.get("source", "unknown")
            sections.append(payload_text)
            sources.append(source)
            scores.append(hit.score)

        # Простая оценка confidence: средний score (ограничен диапазоном 0..1)
        confidence = sum(scores) / len(scores) if scores else 0.0
        confidence = max(0.0, min(1.0, confidence))
        answer = " ".join(sections)  # Объединить в один ответ

        return {
            "answer": answer,
            "sections": sections,
            "sources": sources,
            "confidence": confidence
        }

    def search_company_info(self, query: str) -> dict:
        return self._search(query, doc_type="company_info")

    def search_policy(self, query: str) -> dict:
        return self._search(query, doc_type="policy")

    def search_faq(self, query: str) -> dict:
        return self._search(query, doc_type="faq")

    def search_product_data(self, query: str) -> dict:
        return self._search(query, doc_type="product_data")

    def search_docs(self, query: str) -> dict:
        return self._search(query)
