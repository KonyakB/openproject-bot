import re

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
            subject = self._derive_subject(request)
            return ParsedCreateAction(
                action="create_work_package",
                project_ref=self._extract_project_ref(request),
                type_ref=self._extract_type_ref(request),
                subject=subject,
                confidence=0.76,
            )

    @staticmethod
    def _extract_project_ref(request: str) -> str | None:
        lower = request.lower()
        match = re.search(r"\bin\s+([a-z0-9_-]+)\s+project\b", lower)
        if match:
            return match.group(1)
        match = re.search(r"\bproject\s+([a-z0-9_-]+)\b", lower)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def _extract_type_ref(request: str) -> str | None:
        lower = request.lower()
        if "bug" in lower:
            return "Bug"
        if "feature" in lower:
            return "Feature"
        if "story" in lower:
            return "Story"
        return "Task"

    @staticmethod
    def _derive_subject(request: str) -> str | None:
        cleaned = " ".join(request.split()).strip(" ,.")
        if not cleaned:
            return None

        if "," in cleaned:
            tail = cleaned.split(",")[-1].strip()
            if len(tail) >= 3:
                return tail[:100].title()

        for prefix in [
            "create a new issue",
            "create issue",
            "create task",
            "create",
            "add",
        ]:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip(" ,")
                break

        words = cleaned.split()
        subject = " ".join(words[:10]).strip()
        return subject[:100].title() if subject else None
