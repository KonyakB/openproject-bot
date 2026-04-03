# Runbooks

## Discord signature failures

- Check `DISCORD_PUBLIC_KEY` value and webhook URL configuration.
- Confirm reverse proxy is passing raw body unchanged.

## OpenProject auth failures

- Verify `OPENPROJECT_API_TOKEN` and account permissions.
- Call `GET /api/v3/projects` with the same token.

## Metadata sync failures

- Execute `python scripts/sync_openproject_metadata.py` and inspect logs.
- Verify OpenProject `custom_fields` endpoint availability.

## LLM provider downtime

- Parser falls back to low-confidence mode and confirmation path.
- Check `LLM_BASE_URL`, `LLM_API_KEY`, and provider status.
