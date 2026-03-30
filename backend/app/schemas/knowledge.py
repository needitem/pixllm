from typing import List, Optional
from pydantic import BaseModel


class KnowledgeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    file_ids: List[str] = []


class KnowledgeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    file_ids: Optional[List[str]] = None
