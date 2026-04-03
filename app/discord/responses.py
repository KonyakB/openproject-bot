def interaction_pong() -> dict:
    return {"type": 1}


def interaction_message(content: str, ephemeral: bool = True) -> dict:
    flags = 64 if ephemeral else 0
    return {"type": 4, "data": {"content": content, "flags": flags}}


def interaction_with_confirmation(content: str, token: str) -> dict:
    return {
        "type": 4,
        "data": {
            "content": content,
            "flags": 64,
            "components": [
                {
                    "type": 1,
                    "components": [
                        {"type": 2, "style": 3, "label": "Confirm", "custom_id": f"confirm:{token}"},
                        {"type": 2, "style": 4, "label": "Cancel", "custom_id": f"cancel:{token}"},
                    ],
                }
            ],
        },
    }


def interaction_update_message(content: str) -> dict:
    return {"type": 7, "data": {"content": content, "components": []}}
