from __future__ import annotations

import os
from typing import Any

from langchain_classic.indexes import SQLRecordManager, index
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter


import time

class SafeGeminiEmbeddings:
    def __init__(self, model: str, delay: float = 0.6) -> None:
        self._base = GoogleGenerativeAIEmbeddings(model=model)
        self._delay = delay  # seconds between individual embed_query calls to stay under 100 req/min

    def embed_query(self, text: str) -> list[float]:
        return self._base.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            vectors.append(self._base.embed_query(text))
            time.sleep(self._delay)
        return vectors


class IngestionVectorStore:
    def __init__(
        self,
        chroma_dir: str,
        collection_name: str,
        embedding_model: str,
        record_manager_db_url: str,
        record_manager_namespace: str,
    ) -> None:
        self._collection_name = collection_name
        self._chroma_dir = chroma_dir
        self._embedder = SafeGeminiEmbeddings(model=embedding_model)
        self._vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self._embedder,
            persist_directory=chroma_dir,
        )
        self._record_manager = SQLRecordManager(
            namespace=record_manager_namespace,
            db_url=record_manager_db_url,
        )
        self._record_manager.create_schema()

    def reset_collection(self) -> None:
        self._vector_store.delete_collection()
        self._vector_store = Chroma(
            collection_name=self._collection_name,
            embedding_function=self._embedder,
            persist_directory=self._chroma_dir,
        )
        # Wipe existing record-manager entries for this namespace.
        while True:
            keys = self._record_manager.list_keys(limit=1000)
            if not keys:
                break
            self._record_manager.delete_keys(keys)

    def index_documents(
        self,
        documents: list[Document],
        batch_size: int,
        cleanup: str | None,
        source_id_key: str | None,
        cleanup_batch_size: int,
        force_update: bool,
        key_encoder: str,
    ) -> dict[str, int]:
        if batch_size <= 0:
            raise ValueError("batch_size must be > 0")
        if cleanup not in {None, "incremental", "full", "scoped_full"}:
            raise ValueError("cleanup must be one of: None, incremental, full, scoped_full")
        safe_documents = [doc for doc in documents if doc.page_content and doc.page_content.strip()]
        if not safe_documents:
            return {
                "num_added": 0,
                "num_deleted": 0,
                "num_skipped": 0,
                "num_updated": 0,
            }

        return self._index_with_retry(
            documents=safe_documents,
            batch_size=batch_size,
            cleanup=cleanup,
            source_id_key=source_id_key,
            cleanup_batch_size=cleanup_batch_size,
            force_update=force_update,
            key_encoder=key_encoder,
        )

    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=1, max=10),
        reraise=True,
    )
    def _index_with_retry(
        self,
        documents: list[Document],
        batch_size: int,
        cleanup: str | None,
        source_id_key: str | None,
        cleanup_batch_size: int,
        force_update: bool,
        key_encoder: str,
    ) -> dict[str, int]:
        return index(
            docs_source=documents,
            record_manager=self._record_manager,
            vector_store=self._vector_store,
            batch_size=batch_size,
            cleanup=cleanup,
            source_id_key=source_id_key,
            cleanup_batch_size=cleanup_batch_size,
            force_update=force_update,
            key_encoder=key_encoder,
        )

    def smoke_query(self, query: str, top_k: int) -> tuple[list[dict[str, Any]], list[float]]:
        docs_and_scores = self._vector_store.similarity_search_with_score(query=query, k=top_k)
        metadatas: list[dict[str, Any]] = []
        distances: list[float] = []
        for doc, score in docs_and_scores:
            metadatas.append(doc.metadata)
            distances.append(float(score))
        return metadatas, distances


def validate_environment(chroma_dir: str | None) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY. Add it to backend/.env or environment.")

    persist_directory = chroma_dir or os.getenv("CHROMA_PERSIST_DIRECTORY")
    if not persist_directory:
        raise RuntimeError(
            "Missing CHROMA_PERSIST_DIRECTORY. Set it in backend/.env or pass --chroma-dir."
        )
    return persist_directory
