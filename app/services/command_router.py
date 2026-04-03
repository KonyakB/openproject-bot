from sqlalchemy.orm import Session

from app.discord.responses import interaction_message
from app.services.create_issue import CreateIssueService


class CommandRouterService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def route_pm_subcommand(
        self,
        *,
        interaction_id: str,
        subcommand: str,
        request_text: str | None,
        discord_user_id: str,
        discord_username: str,
    ) -> dict:
        if subcommand == "help":
            return interaction_message(
                "Supported commands:\n"
                "/pm create request:\"create issue in space1 for electronics, design pcb\""
            )

        if subcommand == "create":
            if not request_text:
                return interaction_message("Missing request text. Usage: /pm create request:\"...\"")
            return CreateIssueService(self.db).run(
                interaction_id=interaction_id,
                discord_user_id=discord_user_id,
                discord_username=discord_username,
                request_text=request_text,
            )

        return interaction_message("Unsupported /pm subcommand.")
