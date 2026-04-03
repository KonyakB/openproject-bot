import httpx


def edit_original_interaction_response(
    application_id: str,
    interaction_token: str,
    content: str,
    components: list[dict] | None = None,
) -> None:
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{interaction_token}/messages/@original"
    payload: dict = {"content": content}
    if components is not None:
        payload["components"] = components
    with httpx.Client(timeout=20.0) as client:
        response = client.patch(url, json=payload)
        response.raise_for_status()
