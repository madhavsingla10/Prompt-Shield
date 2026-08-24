import os
import math
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from config import settings
from schemas import RAGRecord, RAGContext
from agents.base_agent import BaseAgent

class InMemoryVectorStore:
    """Lightweight in-memory vector index fallback when ChromaDB is not installed."""
    def __init__(self):
        self.documents: Dict[str, Dict[str, Any]] = {}

    def add(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        for i, doc_id in enumerate(ids):
            self.documents[doc_id] = {
                "id": doc_id,
                "document": documents[i],
                "metadata": metadatas[i] if i < len(metadatas) else {}
            }

    def query(self, query_texts: List[str], n_results: int = 3) -> Dict[str, Any]:
        query = query_texts[0].lower() if query_texts else ""
        query_words = set(query.split())
        scored = []
        for doc_id, data in self.documents.items():
            doc_text = data["document"].lower()
            doc_words = set(doc_text.split())
            overlap = len(query_words.intersection(doc_words))
            score = overlap / (math.sqrt(len(query_words) * len(doc_words)) + 1e-5)
            scored.append((score, data))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:n_results]

        return {
            "ids": [[item[1]["id"] for item in top]],
            "documents": [[item[1]["document"] for item in top]],
            "metadatas": [[item[1]["metadata"] for item in top]],
            "distances": [[1.0 - item[0] for item in top]]
        }

class VectorStoreManager(BaseAgent):
    """
    ChromaDB Vector Store Manager with resilient in-memory fallback.
    Manages vector embeddings, persistent knowledge collections,
    semantic search retrieval, and indirect injection document indexing.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        super().__init__(name="VectorStoreAgent")
        self.persist_dir = persist_dir or settings.VECTOR_DB_DIR
        self._client = None
        self._is_in_memory_fallback = False
        self._fallback_stores: Dict[str, InMemoryVectorStore] = {}

    def _get_client(self):
        if self._client is None:
            try:
                import chromadb
                os.makedirs(self.persist_dir, exist_ok=True)
                self._client = chromadb.PersistentClient(path=self.persist_dir)
                self.log(f"Initialized ChromaDB persistent client at '{self.persist_dir}'.")
            except ImportError:
                self.log("ChromaDB library not installed; using optimized in-memory vector index.")
                self._is_in_memory_fallback = True
            except Exception as e:
                self.log(f"Warning: Persistent ChromaDB client failed ({e}). Falling back to ephemeral in-memory index.")
                self._is_in_memory_fallback = True
        return self._client

    def index_rag_context(self, context: RAGContext, collection_name: str = "rag_knowledge") -> str:
        """Indexes all documents and honeypot records from a RAGContext into vector store."""
        self._get_client()

        ids = [r.id for r in context.records]
        documents = [f"{r.title}\n{r.content}" for r in context.records]
        metadatas = [
            {
                "title": r.title,
                "is_sensitive": r.is_sensitive,
                "is_poisoned": r.is_poisoned,
                "domain": context.domain_description
            }
            for r in context.records
        ]

        if self._is_in_memory_fallback or self._client is None:
            store = InMemoryVectorStore()
            if ids:
                store.add(ids=ids, documents=documents, metadatas=metadatas)
            self._fallback_stores[collection_name] = store
            self.log(f"Indexed {len(ids)} knowledge chunks into in-memory collection '{collection_name}'.")
            return collection_name

        try:
            try:
                self._client.delete_collection(name=collection_name)
            except Exception:
                pass

            collection = self._client.get_or_create_collection(name=collection_name)
            if ids:
                collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
            self.log(f"Successfully indexed {len(ids)} knowledge chunks into ChromaDB collection '{collection_name}'.")
            return collection_name
        except Exception as e:
            self.log(f"Error indexing documents into ChromaDB ({e}); falling back to in-memory store.")
            store = InMemoryVectorStore()
            if ids:
                store.add(ids=ids, documents=documents, metadatas=metadatas)
            self._fallback_stores[collection_name] = store
            return collection_name

    def query_similar(self, query: str, collection_name: str = "rag_knowledge", top_k: int = 3) -> List[Dict[str, Any]]:
        """Queries the vector store for top_k relevant documents."""
        self._get_client()

        if self._is_in_memory_fallback or self._client is None or collection_name in self._fallback_stores:
            store = self._fallback_stores.get(collection_name, InMemoryVectorStore())
            results = store.query(query_texts=[query], n_results=top_k)
        else:
            try:
                collection = self._client.get_collection(name=collection_name)
                results = collection.query(
                    query_texts=[query],
                    n_results=top_k
                )
            except Exception as e:
                self.log(f"Error querying vector collection '{collection_name}': {e}")
                return []

        hits = []
        if results and "documents" in results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                doc_id = results["ids"][0][i] if "ids" in results else str(i)
                meta = results["metadatas"][0][i] if "metadatas" in results and results["metadatas"] else {}
                dist = results["distances"][0][i] if "distances" in results and results["distances"] else 0.0
                hits.append({
                    "id": doc_id,
                    "document": doc,
                    "metadata": meta,
                    "distance": dist
                })
        return hits

vector_store_manager = VectorStoreManager()

