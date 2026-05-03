import csv
import json
import uuid
from pathlib import Path
from typing import Dict, List

from openai import OpenAI
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest


class VectorStore:
    COLLECTION_NAME = "documents"
    EMBEDDING_MODEL = "text-embedding-3-large"
    VECTOR_SIZE = 3072
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 100

    def __init__(self, data_dir: str = "data"):
        self.client = QdrantClient(":memory:")  # Для демо храним в памяти
        self.openai = OpenAI()
        self._ensure_collection()
        self.load_documents(data_dir)

    def _ensure_collection(self):
        try:
            # Check if collection exists
            self.client.get_collection(self.COLLECTION_NAME)
        except Exception:
            # Create collection if it doesn't exist
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config={
                    "size": self.VECTOR_SIZE,
                    "distance": rest.Distance.COSINE,
                },
            )

    def load_documents(self, data_dir: str = "data"):
        # Check if documents are already loaded
        try:
            collection_info = self.client.get_collection(self.COLLECTION_NAME)
            if collection_info.points_count > 0:
                return  # Documents already loaded
        except Exception:
            pass  # Collection might not exist yet

        path = Path(data_dir)
        if not path.exists():
            return

        documents = []
        for file_path in sorted(path.rglob("*")):
            if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md", ".csv", ".pdf", ".json"}:
                text = self._read_file(file_path)
                if not text:
                    continue

                documents.append(
                    {
                        "source": str(file_path.name),
                        "content": text,
                        "doc_type": self._guess_doc_type(file_path),
                        "metadata": {
                            "file_path": str(file_path),
                            "modified_time": file_path.stat().st_mtime,
                        }
                    }
                )

        chunks = []
        for document in documents:
            chunks.extend(self._chunk_text(document))

        if not chunks:
            return

        embeddings = self._embed_texts([chunk["text"] for chunk in chunks])
        points = []
        for chunk, embedding in zip(chunks, embeddings):
            points.append(
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
            )

        self.client.upsert(collection_name=self.COLLECTION_NAME, points=points)

    def _read_file(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            return self._read_csv(file_path)
        elif suffix == ".pdf":
            return self._read_pdf(file_path)
        elif suffix == ".json":
            return self._read_json(file_path)
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

    def _chunk_text(self, document: Dict[str, any]) -> List[Dict[str, any]]:
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

    def _search(self, query: str, doc_type: str = None, top_k: int = 3) -> str:
        if not query:
            return ""

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
            return "No relevant documents found."

        results = []
        for hit in hits.points:
            payload = hit.payload or {}
            payload_text = payload.get("text", "")
            source = payload.get("source", "unknown")
            results.append(f"Source: {source}\n{payload_text}")

        return "\n\n".join(results)

    def search_company_info(self, query: str) -> str:
        return self._search(query, doc_type="company_info")

    def search_policy(self, query: str) -> str:
        return self._search(query, doc_type="policy")

    def search_faq(self, query: str) -> str:
        return self._search(query, doc_type="faq")

    def search_product_data(self, query: str) -> str:
        return self._search(query, doc_type="product_data")

    def search_docs(self, query: str) -> str:
        return self._search(query)
