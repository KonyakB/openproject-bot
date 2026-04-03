from app.llm.parser import CreateRequestParser


class FailingLLMClient:
    def parse_json(self, system_prompt: str, user_prompt: str):
        raise RuntimeError("llm unavailable")


def test_fallback_subject_ignores_boilerplate_and_assignee_clause() -> None:
    parser = CreateRequestParser(llm_client=FailingLLMClient())

    result = parser.parse(
        request="in demo project add a work package to design umls, add bence arek as assignee",
        project_candidates=["demo"],
        type_candidates=["Task"],
        custom_field_candidates={},
    )

    assert result.project_ref == "demo"
    assert result.subject == "Design Umls"
