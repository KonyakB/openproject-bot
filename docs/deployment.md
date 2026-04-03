# Deployment

1. Configure `.env` in production with secure values.
2. Build and start services:

```bash
docker compose up -d --build
```

3. Pull the Ollama model used by the parser:

```bash
docker compose exec ollama ollama pull llama3.2:1b
```

4. Run migrations:

```bash
docker compose exec bot alembic upgrade head
```

5. Register Discord commands:

```bash
docker compose exec bot python scripts/register_discord_commands.py
```

6. Sync metadata:

```bash
docker compose exec bot python scripts/sync_openproject_metadata.py
```

7. Set Discord Interactions Endpoint URL to:

```text
https://<your-bot-domain>/discord/interactions
```
