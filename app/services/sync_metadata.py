from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FieldValueMapping, MetadataSyncState, ProjectMapping, ProjectTypeMapping
from app.openproject.client import OpenProjectClient


class MetadataSyncService:
    def __init__(self, db: Session, op_client: OpenProjectClient) -> None:
        self.db = db
        self.op_client = op_client

    def run(self) -> dict[str, int]:
        projects = self.op_client.list_projects()
        project_count = 0
        type_count = 0
        field_count = 0

        for project in projects:
            row = self.db.scalar(
                select(ProjectMapping).where(ProjectMapping.openproject_project_id == project.id)
            )
            if row is None:
                row = ProjectMapping(
                    human_name=project.name,
                    openproject_project_id=project.id,
                    openproject_project_identifier=project.identifier or project.name.lower().replace(" ", "-"),
                    aliases_json=[project.name, project.identifier or ""],
                    active=True,
                )
                self.db.add(row)
            else:
                row.human_name = project.name
                row.openproject_project_identifier = project.identifier or row.openproject_project_identifier
                row.aliases_json = list({project.name, project.identifier or "", *row.aliases_json})
                row.active = True
                row.updated_at = datetime.now(UTC)
            project_count += 1

            types = self.op_client.list_project_types(project.id)
            for t in types:
                trow = self.db.scalar(
                    select(ProjectTypeMapping).where(
                        ProjectTypeMapping.project_id == project.id,
                        ProjectTypeMapping.openproject_type_id == t.id,
                    )
                )
                if trow is None:
                    trow = ProjectTypeMapping(
                        project_id=project.id,
                        openproject_type_id=t.id,
                        name=t.name,
                        active=True,
                    )
                    self.db.add(trow)
                else:
                    trow.name = t.name
                    trow.active = True
                    trow.updated_at = datetime.now(UTC)
                type_count += 1

        custom_fields = self.op_client.fetch_custom_fields()
        for cf in custom_fields:
            field_name = cf.get("name")
            field_id = cf.get("id")
            if not field_name or field_id is None:
                continue
            values = cf.get("_embedded", {}).get("allowedValues", [])
            for value in values:
                v = value.get("value")
                if v is None:
                    continue
                frow = self.db.scalar(
                    select(FieldValueMapping).where(
                        FieldValueMapping.field_name == field_name,
                        FieldValueMapping.human_value == str(v),
                        FieldValueMapping.project_id.is_(None),
                    )
                )
                if frow is None:
                    frow = FieldValueMapping(
                        field_name=field_name,
                        field_identifier=int(field_id),
                        human_value=str(v),
                        openproject_value=str(v),
                        project_id=None,
                        aliases_json=[str(v)],
                        active=True,
                    )
                    self.db.add(frow)
                else:
                    frow.openproject_value = str(v)
                    frow.field_identifier = int(field_id)
                    frow.aliases_json = list({*frow.aliases_json, str(v)})
                    frow.active = True
                    frow.updated_at = datetime.now(UTC)
                field_count += 1

        state = self.db.scalar(select(MetadataSyncState).where(MetadataSyncState.metadata_kind == "all"))
        if state is None:
            state = MetadataSyncState(metadata_kind="all", status="ok", last_synced_at=datetime.now(UTC))
            self.db.add(state)
        else:
            state.status = "ok"
            state.last_synced_at = datetime.now(UTC)

        self.db.commit()
        return {"projects": project_count, "types": type_count, "field_values": field_count}
