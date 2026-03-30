from typing import Optional

from pydantic import BaseModel, Field


class StartEmbedDocsRequest(BaseModel):
    docs_dir: str
    qdrant_url: str = "http://localhost:6333"
    batch_size: int = Field(default=32, ge=1, le=256)
    model: str = "BAAI/bge-m3"
    force_reindex: bool = False


class StartVerifyEmbeddingsRequest(BaseModel):
    qdrant_url: str = "http://localhost:6333"
    model: str = "BAAI/bge-m3"
    query: Optional[str] = None
    collection: Optional[str] = None
    top_k: int = Field(default=3, ge=1, le=20)


class StartResetRagRequest(BaseModel):
    skip_minio: bool = False
    keep_documents_only: bool = True

