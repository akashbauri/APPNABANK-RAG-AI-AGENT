import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class MultilingualEmbedder:
    def __init__(self):
        # Using local multilingual E5 base model supporting multi-language embedding
        self.model = SentenceTransformer('intfloat/multilingual-e5-base')

    def _format_texts(self, texts: List[str], is_query: bool) -> List[str]:
        # E5 model design patterns require prefixing queries and documents
        prefix = "query: " if is_query else "passage: "
        return [f"{prefix}{text}" for text in texts]

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        formatted = self._format_texts(documents, is_query=False)
        embeddings = self.model.encode(formatted, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        formatted = self._format_texts([query], is_query=True)
        embedding = self.model.encode(formatted, normalize_embeddings=True)
        return embedding[0].tolist()

embedder = MultilingualEmbedder()
