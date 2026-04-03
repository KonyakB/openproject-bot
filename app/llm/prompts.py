SYSTEM_PROMPT = """You are a strict parser for OpenProject work package creation.
Output JSON only, no markdown.
Rules:
- action must be create_work_package
- never invent IDs
- use null for unresolved fields
- keep subject concise and action-oriented
- include ambiguities when uncertain
"""


def build_user_prompt(
    request: str,
    project_candidates: list[str],
    type_candidates: list[str],
    custom_field_candidates: dict[str, list[str]],
) -> str:
    return (
        "Parse the following request into the schema.\n"
        f"Request: {request}\n"
        f"Projects: {project_candidates}\n"
        f"Types: {type_candidates}\n"
        f"CustomFields: {custom_field_candidates}\n"
    )
