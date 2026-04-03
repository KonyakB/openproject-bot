from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PendingConfirmation
from app.discord.responses import interaction_update_message
from app.llm.schemas import ValidationResult
from app.openproject.client import OpenProjectClient
from app.openproject.schemas import CreateWorkPackagePayload


class ConfirmationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.op_client = OpenProjectClient()

    def confirm(self, token: str, discord_user_id: str) -> dict:
        row = self._load_pending(token, discord_user_id)
        if row is None:
            return interaction_update_message("Confirmation token is invalid or expired.")

        validation = ValidationResult.model_validate(row.validation_result_json)
        resolved = validation.resolved
        if resolved is None:
            row.status = "expired"
            self.db.commit()
            return interaction_update_message("Confirmation cannot proceed due to invalid state.")

        created = self.op_client.create_work_package(
            CreateWorkPackagePayload(
                project_id=resolved.project_id,
                type_id=resolved.type_id,
                subject=resolved.subject,
                description=resolved.description,
                custom_fields=resolved.custom_fields,
                due_date=resolved.due_date.isoformat() if resolved.due_date else None,
            )
        )
        row.status = "confirmed"
        self.db.commit()
        return interaction_update_message(f"Created work package #{created.id}: {created.link}")

    def cancel(self, token: str, discord_user_id: str) -> dict:
        row = self._load_pending(token, discord_user_id)
        if row is None:
            return interaction_update_message("Confirmation token is invalid or expired.")
        row.status = "cancelled"
        self.db.commit()
        return interaction_update_message("Cancelled.")

    def _load_pending(self, token: str, discord_user_id: str) -> PendingConfirmation | None:
        row = self.db.scalar(
            select(PendingConfirmation).where(
                PendingConfirmation.token == token,
                PendingConfirmation.discord_user_id == discord_user_id,
                PendingConfirmation.status == "pending",
            )
        )
        if row is None:
            return None
        expires_at = row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            row.status = "expired"
            self.db.commit()
            return None
        return row
