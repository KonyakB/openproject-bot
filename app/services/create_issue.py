import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.db.models import PendingConfirmation
from app.discord.responses import interaction_message, interaction_with_confirmation
from app.llm.parser import CreateRequestParser
from app.openproject.mapper import normalize_ref
from app.openproject.client import OpenProjectClient
from app.openproject.metadata import MetadataRepository
from app.openproject.schemas import CreateWorkPackagePayload
from app.openproject.validator import CreateActionValidator
from app.services.audit import AuditService


class CreateIssueService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.parser = CreateRequestParser()
        self.op_client = OpenProjectClient()
        self.metadata_repo = MetadataRepository(db)
        self.validator = CreateActionValidator(self.metadata_repo)
        self.audit = AuditService(db)

    def run(self, *, interaction_id: str, discord_user_id: str, discord_username: str, request_text: str) -> dict:
        projects = self.metadata_repo.load_projects()
        types = self.metadata_repo.load_types()
        field_values = self.metadata_repo.load_field_values()

        parsed = self.parser.parse(
            request=request_text,
            project_candidates=[p.identifier for p in projects] + [p.name for p in projects],
            type_candidates=list({t.name for t in types}),
            custom_field_candidates=self._field_candidates(field_values),
        )

        if not parsed.project_ref:
            inferred_project = self._infer_project_from_text(request_text, projects)
            if inferred_project:
                parsed.project_ref = inferred_project
                parsed.ambiguities.append("Project inferred from request text")

        validation = self.validator.validate(parsed, discord_username=discord_username)
        if not validation.ok or validation.resolved is None:
            msg = f"Could not create work package: {', '.join(validation.errors)}"
            self.audit.log(
                interaction_id=interaction_id,
                discord_user_id=discord_user_id,
                discord_username=discord_username,
                raw_command=request_text,
                parsed=parsed,
                validation=validation,
                status="validation_failed",
                error_code="VALIDATION_FAILED",
                error_message=msg,
            )
            return interaction_message(msg)

        resolved = validation.resolved
        if resolved.needs_confirmation:
            token = secrets.token_urlsafe(18)
            row = PendingConfirmation(
                token=token,
                discord_user_id=discord_user_id,
                expires_at=datetime.now(UTC) + timedelta(minutes=10),
                parsed_action_json=parsed.model_dump(mode="json"),
                validation_result_json=validation.model_dump(mode="json"),
                status="pending",
            )
            self.db.add(row)
            self.db.commit()

            reasons = "\n".join(f"- {r}" for r in resolved.confirmation_reasons)
            content = (
                "I parsed your request and need confirmation before creating the work package.\n"
                f"Project ID: {resolved.project_id}\n"
                f"Type ID: {resolved.type_id}\n"
                f"Subject: {resolved.subject}\n"
                f"Reasons:\n{reasons}"
            )
            self.audit.log(
                interaction_id=interaction_id,
                discord_user_id=discord_user_id,
                discord_username=discord_username,
                raw_command=request_text,
                parsed=parsed,
                validation=validation,
                status="pending_confirmation",
            )
            return interaction_with_confirmation(content, token=token)

        created = self.op_client.create_work_package(
            CreateWorkPackagePayload(
                project_id=resolved.project_id,
                type_id=resolved.type_id,
                subject=resolved.subject,
                description=resolved.description,
                custom_fields=resolved.custom_fields,
                due_date=resolved.due_date.isoformat() if resolved.due_date else None,
                priority_id=resolved.priority_id,
                assignee_id=resolved.assignee_id,
            )
        )
        self.audit.log(
            interaction_id=interaction_id,
            discord_user_id=discord_user_id,
            discord_username=discord_username,
            raw_command=request_text,
            parsed=parsed,
            validation=validation,
            status="created",
            work_package_id=created.id,
        )
        message = (
            f"Created work package #{created.id}\n"
            f"Subject: {created.subject}\n"
            f"Link: {created.link}"
        )
        return interaction_message(message)

    @staticmethod
    def _field_candidates(field_values: list) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for field in field_values:
            result.setdefault(field.field_name, []).append(field.value)
        return result

    @staticmethod
    def _infer_project_from_text(request_text: str, projects: list) -> str | None:
        normalized_request = normalize_ref(request_text)
        matches: list[str] = []
        for project in projects:
            candidates = [project.identifier, project.name, *project.aliases]
            for candidate in candidates:
                if not candidate:
                    continue
                if normalize_ref(candidate) and normalize_ref(candidate) in normalized_request:
                    matches.append(project.identifier)
                    break
        if len(matches) == 1:
            return matches[0]
        return None
