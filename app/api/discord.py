import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db
from app.discord.commands import parse_application_command
from app.discord.components import parse_component_custom_id
from app.discord.responses import interaction_message, interaction_pong
from app.discord.verify import verify_discord_signature
from app.services.command_router import CommandRouterService
from app.services.confirm_action import ConfirmationService

router = APIRouter(prefix="/discord", tags=["discord"])


@router.post("/interactions")
async def discord_interactions(
    request: Request,
    x_signature_ed25519: str = Header(default=""),
    x_signature_timestamp: str = Header(default=""),
    db: Session = Depends(get_db),
) -> dict:
    settings = get_settings()
    body = await request.body()
    if not verify_discord_signature(
        public_key_hex=settings.discord_public_key,
        signature_hex=x_signature_ed25519,
        timestamp=x_signature_timestamp,
        body=body,
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid request signature")

    payload = json.loads(body.decode("utf-8"))
    interaction_type = payload.get("type")

    if interaction_type == 1:
        return interaction_pong()

    if interaction_type == 2:
        command = parse_application_command(payload)
        member = payload.get("member", {}).get("user", {})
        discord_user_id = member.get("id", "unknown")
        discord_username = member.get("username", "unknown")
        if command.group != "pm":
            return interaction_message("Unsupported command group.")
        return CommandRouterService(db).route_pm_subcommand(
            interaction_id=payload.get("id", "unknown"),
            subcommand=command.subcommand,
            request_text=command.request_text,
            discord_user_id=discord_user_id,
            discord_username=discord_username,
        )

    if interaction_type == 3:
        custom_id = payload.get("data", {}).get("custom_id", "")
        action = parse_component_custom_id(custom_id)
        member = payload.get("member", {}).get("user", {})
        discord_user_id = member.get("id", "unknown")
        if action is None:
            return interaction_message("Invalid action token.")
        service = ConfirmationService(db)
        if action.action == "confirm":
            return service.confirm(action.token, discord_user_id)
        return service.cancel(action.token, discord_user_id)

    return interaction_message("Unsupported Discord interaction type.")
