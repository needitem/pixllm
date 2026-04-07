from typing import Optional

from pydantic import BaseModel, Field


class IssueSessionTokenRequest(BaseModel):
    label: str = ""
    ttl_sec: Optional[int] = Field(default=None, ge=60)
    permanent: bool = False


class RevokeSessionTokenRequest(BaseModel):
    token_id: str = Field(..., min_length=1)
