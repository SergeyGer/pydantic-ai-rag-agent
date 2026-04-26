import sys
sys.path.append("src")
from qdrant_client import QdrantClient
print([m for m in dir(QdrantClient) if "search" in m.lower()])
