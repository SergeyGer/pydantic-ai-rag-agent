from qdrant_client import QdrantClient

class VectorStore:
    def __init__(self):
        self.client = QdrantClient(":memory:") # Для демо храним в памяти

    def search_docs(self, query: str):
        # В реальном проекте тут поиск эмбеддингов
        # Для демо вернем заглушку, имитирующую найденный текст
        return "Smartclip office is located in Berlin. They have a 4-day work week option."
