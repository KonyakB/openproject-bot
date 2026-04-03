from app.db.models import FieldValueMapping, ProjectMapping, ProjectTypeMapping
from app.openproject.schemas import OpenProjectWorkPackageResult
from app.services.create_issue import CreateIssueService


class StubParser:
    def parse(self, **kwargs):
        from app.llm.schemas import ParsedCreateAction

        return ParsedCreateAction(
            action="create_work_package",
            project_ref="space1",
            type_ref="Task",
            subject="Design PCB",
            description="Create PCB",
            custom_fields={"Domain": "electronics"},
            confidence=0.99,
        )


class StubOpenProjectClient:
    def create_work_package(self, payload):
        return OpenProjectWorkPackageResult(
            id=1234,
            subject=payload.subject,
            project_name="space1",
            link="https://openproject.example.com/work_packages/1234",
        )


def test_create_issue_service_success(db_session) -> None:
    db_session.add(
        ProjectMapping(
            human_name="Space 1",
            openproject_project_id=42,
            openproject_project_identifier="space1",
            aliases_json=["space1"],
            active=True,
        )
    )
    db_session.add(ProjectTypeMapping(project_id=42, openproject_type_id=7, name="Task", active=True))
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

    service = CreateIssueService(db_session)
    service.parser = StubParser()
    service.op_client = StubOpenProjectClient()

    response = service.run(
        interaction_id="abc",
        discord_user_id="u1",
        discord_username="alice",
        request_text="create issue in space1 for electronics, design pcb",
    )

    assert response["type"] == 4
    assert "Created work package #1234" in response["data"]["content"]
