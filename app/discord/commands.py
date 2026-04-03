from pydantic import BaseModel


class ParsedCommand(BaseModel):
    group: str
    subcommand: str
    request_text: str | None = None


def parse_application_command(payload: dict) -> ParsedCommand:
    data = payload.get("data", {})
    group = data.get("name", "")
    options = data.get("options", [])
    if not options:
        return ParsedCommand(group=group, subcommand="", request_text=None)

    sub = options[0]
    subcommand = sub.get("name", "")
    sub_opts = sub.get("options", [])
    request_text = None
    for opt in sub_opts:
        if opt.get("name") == "request":
            request_text = opt.get("value")
            break

    return ParsedCommand(group=group, subcommand=subcommand, request_text=request_text)
