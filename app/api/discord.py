import json

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import SessionLocal
from app.db.session import get_db
from app.discord.commands import parse_application_command
from app.discord.components import parse_component_custom_id
from app.discord.responses import (
    interaction_deferred_channel_message,
    interaction_deferred_update_message,
    interaction_message,
    interaction_pong,
)
from app.discord.verify import verify_discord_signature
from app.discord.webhook import edit_original_interaction_response
from app.services.command_router import CommandRouterService
from app.services.confirm_action import ConfirmationService

router = APIRouter(prefix="/discord", tags=["discord"])


@router.post("/interactions")
async def discord_interactions(
    request: Request,
    background_tasks: BackgroundTasks,
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
        if command.subcommand == "create":
            background_tasks.add_task(
                _process_create_interaction,
                payload.get("id", "unknown"),
                command.request_text,
                discord_user_id,
                discord_username,
                settings.discord_application_id,
                payload.get("token", ""),
            )
            return interaction_deferred_channel_message(ephemeral=True)

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
        background_tasks.add_task(
            _process_component_interaction,
            action.action,
            action.token,
            discord_user_id,
            settings.discord_application_id,
            payload.get("token", ""),
        )
        return interaction_deferred_update_message()

    return interaction_message("Unsupported Discord interaction type.")


def _process_create_interaction(
    interaction_id: str,
    request_text: str | None,
    discord_user_id: str,
    discord_username: str,
    application_id: str,
    interaction_token: str,
) -> None:
    db = SessionLocal()
    try:
        response = CommandRouterService(db).route_pm_subcommand(
            interaction_id=interaction_id,
            subcommand="create",
            request_text=request_text,
            discord_user_id=discord_user_id,
            discord_username=discord_username,
        )
        data = response.get("data", {})
        edit_original_interaction_response(
            application_id=application_id,
            interaction_token=interaction_token,
            content=data.get("content", "Done."),
            components=data.get("components", []),
        )
    except Exception:
        edit_original_interaction_response(
            application_id=application_id,
            interaction_token=interaction_token,
            content="I could not process the request due to an internal error.",
            components=[],
        )
    finally:
        db.close()


def _process_component_interaction(
    action: str,
    confirmation_token: str,
    discord_user_id: str,
    application_id: str,
    interaction_token: str,
) -> None:
    db = SessionLocal()
    try:
        service = ConfirmationService(db)
        if action == "confirm":
            response = service.confirm(confirmation_token, discord_user_id)
        else:
            response = service.cancel(confirmation_token, discord_user_id)
        data = response.get("data", {})
        edit_original_interaction_response(
            application_id=application_id,
            interaction_token=interaction_token,
            content=data.get("content", "Done."),
            components=data.get("components", []),
        )
    except Exception:
        edit_original_interaction_response(
            application_id=application_id,
            interaction_token=interaction_token,
            content="I could not process that action due to an internal error.",
            components=[],
        )
    finally:
        db.close()
