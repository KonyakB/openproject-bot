from pydantic import BaseModel


class ComponentAction(BaseModel):
    action: str
    token: str


def parse_component_custom_id(custom_id: str) -> ComponentAction | None:
    if ":" not in custom_id:
        return None
    action, token = custom_id.split(":", maxsplit=1)
    if action not in {"confirm", "cancel"}:
        return None
    return ComponentAction(action=action, token=token)
