import httpx

from app.config import get_settings


def main() -> None:
    settings = get_settings()
    url = f"https://discord.com/api/v10/applications/{settings.discord_application_id}/commands"
    headers = {
        "Authorization": f"Bot {settings.discord_bot_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": "pm",
        "description": "OpenProject assistant",
        "options": [
            {
                "type": 1,
                "name": "create",
                "description": "Create work package from natural language",
                "options": [
                    {
                        "type": 3,
                        "name": "request",
                        "description": "Natural language request",
                        "required": True,
                    }
                ],
            },
            {
                "type": 1,
                "name": "help",
                "description": "Show usage",
            },
            {
                "type": 1,
                "name": "projects",
                "description": "List synced OpenProject projects",
            },
        ],
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
    print("Registered /pm command")


if __name__ == "__main__":
    main()
