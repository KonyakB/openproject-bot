from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import FieldValueMapping, ProjectMapping, ProjectTypeMapping
from app.db.session import get_db
from app.openproject.client import OpenProjectClient
from app.services.sync_metadata import MetadataSyncService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/sync-metadata")
def sync_metadata(db: Session = Depends(get_db)) -> dict[str, int]:
    return MetadataSyncService(db, OpenProjectClient()).run()


@router.get("/metadata")
def metadata(db: Session = Depends(get_db)) -> dict:
    projects = db.scalars(select(ProjectMapping).where(ProjectMapping.active.is_(True))).all()
    types = db.scalars(select(ProjectTypeMapping).where(ProjectTypeMapping.active.is_(True))).all()
    fields = db.scalars(select(FieldValueMapping).where(FieldValueMapping.active.is_(True))).all()
    return {
        "projects": [
            {
                "project_id": p.openproject_project_id,
                "identifier": p.openproject_project_identifier,
                "name": p.human_name,
                "aliases": p.aliases_json,
            }
            for p in projects
        ],
        "types": [
            {"project_id": t.project_id, "type_id": t.openproject_type_id, "name": t.name}
            for t in types
        ],
        "field_values": [
            {
                "field_id": f.field_identifier,
                "field_name": f.field_name,
                "value": f.human_value,
                "openproject_value": f.openproject_value,
            }
            for f in fields
        ],
    }
