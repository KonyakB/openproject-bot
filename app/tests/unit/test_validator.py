from app.db.models import FieldValueMapping, ProjectMapping, ProjectTypeMapping
from app.llm.schemas import ParsedCreateAction
from app.openproject.metadata import MetadataRepository
from app.openproject.validator import CreateActionValidator


def test_validator_resolves_basic_create(db_session) -> None:
    db_session.add(
        ProjectMapping(
            human_name="Space 1",
            openproject_project_id=42,
            openproject_project_identifier="space1",
            aliases_json=["space1", "Space 1"],
            active=True,
        )
    )
    db_session.add(
        ProjectTypeMapping(
            project_id=42,
            openproject_type_id=7,
            name="Task",
            active=True,
        )
    )
    db_session.add(
        FieldValueMapping(
            field_name="Domain",
            field_identifier=9,
            human_value="electronics",
            openproject_value="electronics",
            project_id=None,
            aliases_json=["electronics"],
            active=True,
        )
    )
    db_session.commit()

    parsed = ParsedCreateAction(
        action="create_work_package",
        project_ref="space1",
        type_ref="Task",
        subject="Design PCB",
        custom_fields={"Domain": "electronics"},
        confidence=0.99,
    )

    validator = CreateActionValidator(MetadataRepository(db_session))
    result = validator.validate(parsed, discord_username="alice")

    assert result.ok is True
    assert result.resolved is not None
    assert result.resolved.project_id == 42
    assert result.resolved.type_id == 7
    assert result.resolved.custom_fields["9"] == "electronics"


def test_validator_does_not_force_confirmation_on_confidence_only(db_session) -> None:
    db_session.add(
        ProjectMapping(
            human_name="Demo",
            openproject_project_id=1,
            openproject_project_identifier="demo",
            aliases_json=["demo"],
            active=True,
        )
    )
    db_session.add(ProjectTypeMapping(project_id=1, openproject_type_id=1, name="Task", active=True))
    db_session.commit()

    parsed = ParsedCreateAction(
        action="create_work_package",
        project_ref="demo",
        type_ref="Task",
        subject="Design UMLs",
        confidence=0.4,
        ambiguities=[],
    )

    validator = CreateActionValidator(MetadataRepository(db_session))
    result = validator.validate(parsed, discord_username="alice")

    assert result.ok is True
    assert result.resolved is not None
    assert result.resolved.needs_confirmation is False
