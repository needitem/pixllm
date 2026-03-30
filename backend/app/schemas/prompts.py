from typing import List, Optional
from pydantic import BaseModel


class PromptCreate(BaseModel):
    title: str
    content: str
    variables: List[str] = []
    tags: List[str] = []


class PromptUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[List[str]] = None
    tags: Optional[List[str]] = None
