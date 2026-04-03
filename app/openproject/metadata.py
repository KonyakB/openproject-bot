from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FieldValueMapping, ProjectMapping, ProjectTypeMapping


@dataclass
class ProjectMeta:
    id: int
    name: str
    identifier: str
    aliases: list[str]


@dataclass
class TypeMeta:
    project_id: int
    type_id: int
    name: str


@dataclass
class FieldValueMeta:
    field_id: int
    field_name: str
    value: str
    openproject_value: str
    aliases: list[str]
    project_id: int | None


class MetadataRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def load_projects(self) -> list[ProjectMeta]:
        rows = self.db.scalars(select(ProjectMapping).where(ProjectMapping.active.is_(True))).all()
        return [
            ProjectMeta(
                id=r.openproject_project_id,
                name=r.human_name,
                identifier=r.openproject_project_identifier,
                aliases=r.aliases_json,
            )
            for r in rows
        ]

    def load_types(self) -> list[TypeMeta]:
        rows = self.db.scalars(select(ProjectTypeMapping).where(ProjectTypeMapping.active.is_(True))).all()
        return [TypeMeta(project_id=r.project_id, type_id=r.openproject_type_id, name=r.name) for r in rows]

    def load_field_values(self) -> list[FieldValueMeta]:
        rows = self.db.scalars(select(FieldValueMapping).where(FieldValueMapping.active.is_(True))).all()
        return [
            FieldValueMeta(
                field_id=r.field_identifier,
                field_name=r.field_name,
                value=r.human_value,
                openproject_value=r.openproject_value,
                aliases=r.aliases_json,
                project_id=r.project_id,
            )
            for r in rows
        ]
