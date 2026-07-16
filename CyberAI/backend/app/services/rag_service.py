import os
import uuid
from typing import List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from app.config import settings

class RAGService:
    def __init__(self):
        os.makedirs(settings.chroma_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=settings.chroma_dir,
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        try:
            self.ef = embedding_functions.DefaultEmbeddingFunction()
            test_emb = self.ef(["test"])
            self.use_embeddings = True
        except Exception:
            self.use_embeddings = False
            self.ef = None

        self.collection = self.client.get_or_create_collection(
            name="cyberai_documents",
            metadata={"hnsw:space": "cosine"}
        )

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        return chunks

    def index_document(self, doc_id: str, filename: str, text: str) -> int:
        chunks = self._chunk_text(text)
        metadatas = [{"doc_id": doc_id, "filename": filename, "chunk": i} for i in range(len(chunks))]
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

        if self.use_embeddings:
            embeddings = self.ef(chunks)
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
        else:
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
        return len(chunks)

    def search(self, query: str, n_results: int = 5) -> tuple[List[str], List[str]]:
        if self.use_embeddings:
            query_embedding = self.ef([query])
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        sources = list(set(m.get("filename", "Desconocido") for m in metadatas if m))

        return documents, sources

    def delete_document(self, doc_id: str):
        self.collection.delete(where={"doc_id": doc_id})

    def list_documents(self) -> List[dict]:
        all_metadatas = self.collection.get()["metadatas"]
        seen = {}
        for m in all_metadatas:
            if m and m["doc_id"] not in seen:
                seen[m["doc_id"]] = {"id": m["doc_id"], "filename": m["filename"]}
        return list(seen.values())
