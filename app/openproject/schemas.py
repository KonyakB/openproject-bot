from typing import Any

from pydantic import BaseModel, Field


class OpenProjectProject(BaseModel):
    id: int
    name: str
    identifier: str | None = None


class OpenProjectType(BaseModel):
    id: int
    name: str


class OpenProjectWorkPackageResult(BaseModel):
    id: int
    subject: str
    project_name: str | None = None
    link: str | None = None


class CreateWorkPackagePayload(BaseModel):
    project_id: int
    type_id: int
    subject: str
    description: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    priority_id: int | None = None
    assignee_id: int | None = None
    due_date: str | None = None
