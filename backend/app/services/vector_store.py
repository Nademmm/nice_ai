import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from typing import List, Dict, Optional
import json
import hashlib


class VectorStoreService:
    def __init__(self):
        # Try to load embedding model with fallback for network issues
        try:
            print(f"[VectorStore] Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                trust_remote_code=True
            )
            print("[VectorStore] Embedding model loaded successfully")
        except Exception as e:
            print(f"[VectorStore] Warning: Failed to load embedding model: {str(e)}")
            print("[VectorStore] Falling back to local model or cached version...")
            try:
                # Try with cache_folder to use local cache
                cache_folder = "./model_cache"
                os.makedirs(cache_folder, exist_ok=True)
                self.embedding_model = SentenceTransformer(
                    settings.EMBEDDING_MODEL,
                    cache_folder=cache_folder,
                    trust_remote_code=True
                )
                print("[VectorStore] Embedding model loaded from cache")
            except Exception as e2:
                print(f"[VectorStore] Error: Still failed to load model: {str(e2)}")
                raise
        
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="niscahya_knowledge",
            metadata={"description": "Niscahya Indonesia knowledge base"}
        )

    def get_embedding(self, text: str) -> List[float]:
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def add_document(self, text: str, metadata: Dict = None, document_id: str = None):
        if document_id is None:
            document_id = f"doc_{self.collection.count()}"

        embedding = self.get_embedding(text)

        self.collection.add(
            ids=[document_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}]
        )
        return document_id

    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        query_embedding = self.get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        documents = []
        if results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    "content": doc,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0
                })
        return documents

    def delete_document(self, document_id: str):
        self.collection.delete(ids=[document_id])

    def get_all_documents(self) -> List[Dict]:
        all_data = self.collection.get()
        documents = []
        for i, doc_id in enumerate(all_data['ids']):
            documents.append({
                "id": doc_id,
                "content": all_data['documents'][i],
                "metadata": all_data['metadatas'][i]
            })
        return documents

    def count_documents(self) -> int:
        return self.collection.count()


vector_store = VectorStoreService()
