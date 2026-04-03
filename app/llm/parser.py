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

        lowered = cleaned.lower()
        lowered = re.sub(r"\bin\s+[a-z0-9_-]+\s+project\b", "", lowered)
        lowered = re.sub(r"\bproject\s+[a-z0-9_-]+\b", "", lowered)

        for prefix in [
            "create a new issue",
            "create issue",
            "create a work package",
            "create work package",
            "create task",
            "create",
            "add",
        ]:
            if lowered.startswith(prefix):
                lowered = lowered[len(prefix) :].strip(" ,")
                break

        lowered = re.sub(r"\b(a|an)\s+work\s+package\b", "", lowered)
        lowered = re.sub(r"\bwork\s+package\b", "", lowered)
        lowered = re.sub(r"\b(a|an)\s+issue\b", "", lowered)
        lowered = re.sub(r"\bissue\b", "", lowered)
        lowered = re.sub(r"\btask\b", "", lowered)

        if " to " in lowered:
            lowered = lowered.split(" to ", maxsplit=1)[1]

        parts = [p.strip() for p in re.split(r",|\band\b", lowered) if p.strip()]
        informative = []
        for part in parts:
            if any(token in part for token in ["assignee", "assign", "priority", "due date", "project"]):
                continue
            informative.append(part)

        if informative:
            lowered = informative[0]
        elif parts:
            lowered = parts[0]

        lowered = re.sub(r"[^a-z0-9\s-]", "", lowered).strip()
        words = lowered.split()
        subject = " ".join(words[:10]).strip()
        return subject[:100].title() if subject else None
