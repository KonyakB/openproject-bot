from app.config import get_settings
from app.llm.schemas import ParsedCreateAction, ResolvedCreateAction, ValidationResult
from app.openproject.mapper import match_value
from app.openproject.metadata import MetadataRepository


class CreateActionValidator:
    def __init__(self, metadata_repo: MetadataRepository) -> None:
        self.metadata_repo = metadata_repo
        self.settings = get_settings()

    def validate(self, parsed: ParsedCreateAction, discord_username: str) -> ValidationResult:
        errors: list[str] = []
        confirmation_reasons: list[str] = []

        projects = self.metadata_repo.load_projects()
        if not projects:
            return ValidationResult(ok=False, errors=["PROJECT_NOT_FOUND:No projects synced"])

        selected_project = None
        project_was_fuzzy = False

        if not parsed.project_ref and len(projects) == 1:
            selected_project = projects[0]
            confirmation_reasons.append("Project omitted; defaulted to only available project")

        project_refs = [p.identifier for p in projects] + [p.name for p in projects]
        if selected_project is None:
            project_match, project_was_fuzzy = match_value(parsed.project_ref or "", project_refs)
            if not project_match:
                available = ", ".join(sorted({p.identifier for p in projects}))
                errors.append(f"PROJECT_NOT_FOUND:Available projects are {available}")
                return ValidationResult(ok=False, errors=errors)
            if project_was_fuzzy:
                confirmation_reasons.append("Project resolution used fuzzy match")

            project_meta = next(
                p
                for p in projects
                if project_match in {p.identifier, p.name} or project_match in p.aliases
            )
        else:
            project_meta = selected_project

        types = [t for t in self.metadata_repo.load_types() if t.project_id == project_meta.id]
        if not types:
            errors.append("TYPE_NOT_ALLOWED")
            return ValidationResult(ok=False, errors=errors)

        type_names = [t.name for t in types]
        type_ref = parsed.type_ref or "Task"
        type_match, type_was_fuzzy = match_value(type_ref, type_names)
        if not type_match:
            errors.append("TYPE_NOT_ALLOWED")
            return ValidationResult(ok=False, errors=errors)
        if type_was_fuzzy:
            confirmation_reasons.append("Type resolution used fuzzy match")
        type_meta = next(t for t in types if t.name == type_match)

        if not parsed.subject or len(parsed.subject.strip()) < 3:
            errors.append("SUBJECT_REQUIRED")
            return ValidationResult(ok=False, errors=errors)

        resolved_custom_fields: dict[str, str] = {}
        all_field_values = self.metadata_repo.load_field_values()
        for field_name, candidate in parsed.custom_fields.items():
            field_options = [
                f
                for f in all_field_values
                if f.field_name.lower() == field_name.lower() and (f.project_id is None or f.project_id == project_meta.id)
            ]
            allowed = [f.value for f in field_options]
            match, was_fuzzy = match_value(str(candidate), allowed)
            if not match:
                errors.append(f"INVALID_CUSTOM_FIELD_VALUE:{field_name}")
                continue
            if was_fuzzy:
                confirmation_reasons.append(f"Custom field {field_name} resolved with fuzzy match")
            option = next(f for f in field_options if f.value == match)
            resolved_custom_fields[str(option.field_id)] = option.openproject_value

        if errors:
            return ValidationResult(ok=False, errors=errors)

        description = parsed.description
        if description:
            description = f"{description}\n\nRequested via Discord by {discord_username}."

        should_gate_on_confidence = bool(parsed.ambiguities)
        if parsed.confidence < self.settings.auto_create_confidence_threshold and should_gate_on_confidence:
            confirmation_reasons.append("Parser confidence below auto-create threshold")

        needs_confirmation = bool(parsed.ambiguities) or bool(confirmation_reasons)
        confirmation_reasons.extend(parsed.ambiguities)

        return ValidationResult(
            ok=True,
            resolved=ResolvedCreateAction(
                project_id=project_meta.id,
                type_id=type_meta.type_id,
                subject=parsed.subject.strip(),
                description=description,
                custom_fields=resolved_custom_fields,
                due_date=parsed.due_date,
                needs_confirmation=needs_confirmation,
                confirmation_reasons=confirmation_reasons,
            ),
        )
