# OpenProject Discord Assistant (Phase 1)

Production-oriented FastAPI backend for Discord slash commands that create OpenProject work packages via REST.

## What is implemented

- FastAPI app with `POST /discord/interactions`
- Discord Ed25519 signature verification
- `/pm create` and `/pm help` handling
- LLM parser interface + strict Pydantic output schema
- Metadata sync service (projects, types, custom field values)
- Resolver/validator against local metadata cache
- OpenProject REST client for metadata and work package creation
- Confirmation buttons (`Confirm` / `Cancel`) with persisted tokens
- SQLAlchemy models + Alembic initial migration
- Dockerfile and Docker Compose (`bot` + `postgres` + `ollama`)
- Basic unit tests

## Project layout

```text
app/
  api/
  core/
  llm/
  discord/
  openproject/
  services/
  db/
```

## Environment variables

Required:

- `DISCORD_PUBLIC_KEY`
- `DISCORD_APPLICATION_ID`
- `DISCORD_BOT_TOKEN`
- `DISCORD_GUILD_ID` (recommended for instant command updates in a dev server)
- `OPENPROJECT_BASE_URL`
- `OPENPROJECT_API_TOKEN`
- `LLM_API_KEY` (use a placeholder like `dummy` when using local Ollama without auth)
- `DATABASE_URL`

Optional:

- `APP_ENV` (default `development`)
- `APP_NAME`
- `APP_BASE_URL`
- `LOG_LEVEL`
- `LLM_BASE_URL`
- `LLM_MODEL`

Copy and edit:

```bash
cp .env.example .env
```

## Local development

1. Install dependencies:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Start PostgreSQL and app:

```bash
docker compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload
```

If you use the local Ollama service in Docker Compose, pull the model once:

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull llama3.2:1b
```

3. Sync OpenProject metadata:

```bash
python scripts/sync_openproject_metadata.py
```

4. Register Discord commands:

```bash
python scripts/register_discord_commands.py
```

Tip: set `DISCORD_GUILD_ID` in `.env` for immediate command propagation in that guild.
Global command updates can take up to about an hour.

5. Expose local endpoint for Discord with tunnel (ngrok/Cloudflare/Tailscale).

## API endpoints

- `POST /discord/interactions`
- `GET /health/live`
- `GET /health/ready`
- `POST /admin/sync-metadata`

## Tests

```bash
pytest
```

## VPS deployment

1. Copy project and `.env` to VPS.
2. Start services:

```bash
docker compose up -d --build
```

3. Pull and warm the Ollama model:

```bash
docker compose exec ollama ollama pull llama3.2:1b
```

4. Run migrations:

```bash
docker compose exec bot alembic upgrade head
```

5. Register commands and sync metadata from container.
6. Route HTTPS `POST /discord/interactions` to bot container using reverse proxy.

## Reverse proxy example (Nginx)

```nginx
server {
    listen 443 ssl;
    server_name bot.example.com;

    location /discord/interactions {
        proxy_pass http://127.0.0.1:8000/discord/interactions;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health/ {
        proxy_pass http://127.0.0.1:8000/health/;
    }
}
```

## Notes

- OpenProject writes are REST-only.
- MCP is stubbed and read-only placeholder.
- LLM output is always validated before API execution.
