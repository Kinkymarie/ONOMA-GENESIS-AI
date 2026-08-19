from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)


class MemoryCreate(BaseModel):
    project_id: int | None = None
    kind: Literal["session", "project", "document", "research", "workflow", "preference"] = "project"
    content: str = Field(min_length=1, max_length=10000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    project_id: int | None = None
    mode: Literal["auto", "research", "code", "design", "security", "business"] = "auto"


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    project_id: int | None = None
    limit: int = Field(default=10, ge=1, le=50)
