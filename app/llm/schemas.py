from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


class ParsedCreateAction(BaseModel):
    action: Literal["create_work_package"]
    project_ref: str | None = None
    type_ref: str | None = None
    subject: str | None = None
    description: str | None = None
    custom_fields: dict[str, str | int | bool | None] = Field(default_factory=dict)
    priority_ref: str | None = None
    assignee_ref: str | None = None
    due_date: date | None = None
    confidence: float = 0.0
    ambiguities: list[str] = Field(default_factory=list)


class ResolvedCreateAction(BaseModel):
    project_id: int
    type_id: int
    subject: str
    description: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    priority_id: int | None = None
    assignee_id: int | None = None
    due_date: date | None = None
    needs_confirmation: bool = False
    confirmation_reasons: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    ok: bool
    errors: list[str] = Field(default_factory=list)
    resolved: ResolvedCreateAction | None = None
