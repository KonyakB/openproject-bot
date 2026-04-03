from app.llm.client import LLMClient
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.llm.schemas import ParsedCreateAction


class CreateRequestParser:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def parse(
        self,
        request: str,
        project_candidates: list[str],
        type_candidates: list[str],
        custom_field_candidates: dict[str, list[str]],
    ) -> ParsedCreateAction:
        try:
            raw = self.llm_client.parse_json(
                system_prompt=SYSTEM_PROMPT,
                user_prompt=build_user_prompt(
                    request=request,
                    project_candidates=project_candidates,
                    type_candidates=type_candidates,
                    custom_field_candidates=custom_field_candidates,
                ),
            )
            return ParsedCreateAction.model_validate(raw)
        except Exception:
            subject = request.strip().capitalize()[:100] if request.strip() else None
            return ParsedCreateAction(
                action="create_work_package",
                subject=subject,
                confidence=0.2,
                ambiguities=["LLM parsing fallback used"],
            )
