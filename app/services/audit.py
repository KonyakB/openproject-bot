from sqlalchemy.orm import Session

from app.db.models import CommandAuditLog
from app.llm.schemas import ParsedCreateAction, ValidationResult


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def log(
        self,
        *,
        interaction_id: str,
        discord_user_id: str,
        discord_username: str,
        raw_command: str,
        parsed: ParsedCreateAction,
        validation: ValidationResult,
        status: str,
        work_package_id: int | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        row = CommandAuditLog(
            discord_interaction_id=interaction_id,
            discord_user_id=discord_user_id,
            discord_username=discord_username,
            raw_command=raw_command,
            parsed_action_json=parsed.model_dump(mode="json"),
            validation_result_json=validation.model_dump(mode="json"),
            execution_status=status,
            openproject_work_package_id=work_package_id,
            error_code=error_code,
            error_message=error_message,
        )
        self.db.add(row)
        self.db.commit()
