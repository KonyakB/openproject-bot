# OpenProject + Discord LLM Assistant — Implementation Plan

## 1. Objective

Build a production-deployable assistant that:

- accepts commands from Discord via slash commands,
- interprets natural language requests using an LLM,
- validates the requested action against known OpenProject metadata,
- executes write operations against the OpenProject REST API,
- optionally uses OpenProject MCP only for read/search assistance,
- is developed locally on a personal machine,
- and is deployed to the existing VPS where OpenProject is already hosted.

The first production goal is this workflow:

`/pm create a new issue in the space1 project for electronics, design pcb`

Expected behavior:

- identify the intended action as `create_work_package`,
- resolve `space1` to an OpenProject project,
- resolve `electronics` to a configured field value,
- derive a clean subject such as `Design PCB`,
- create the work package through the OpenProject API,
- return the created work package reference and link in Discord.

---

## 2. Scope and Non-Goals

### In scope for v1

- Discord slash commands
- natural-language parsing with an LLM
- OpenProject work package creation
- metadata resolution and validation
- confirmation flow for ambiguous requests
- local development environment
- Dockerized deployment to VPS
- observability, audit logging, secret handling
- optional read-only OpenProject MCP integration for search/summarization

### Out of scope for v1

- direct arbitrary natural-language execution without validation
- destructive operations like delete
- full conversational memory
- direct bot-side user impersonation in OpenProject
- multi-tenant support
- browser UI beyond health/docs endpoints

---

## 3. Key Product Decisions

### 3.1 Use REST API for writes

Use the OpenProject REST API for all create/update/comment operations. OpenProject’s API documentation for work packages emphasizes schema/form-driven creation and notes that available fields vary by plugins and custom fields. MCP should not be the write path. The OpenProject MCP server is currently experimental and read-only. ([openproject.org](https://www.openproject.org/docs/api/endpoints/work-packages/?utm_source=chatgpt.com))

### 3.2 Treat the LLM as a parser, not the source of truth

The LLM must only:

- classify intent,
- extract candidate fields,
- generate a draft subject/description,
- identify ambiguities.

The backend is authoritative for:

- project existence,
- allowed types,
- valid custom field values,
- user mapping,
- permissions,
- final payload construction.

### 3.3 Introduce one canonical “domain/tag” field in OpenProject

Do not leave “tag or something” ambiguous. Pick a single OpenProject representation for concepts like `electronics`, `firmware`, `mechanical`.

Recommended choice:

- create one custom field such as `Domain`, `Discipline`, or `Area`
- predefine allowed values
- let the bot map natural language to this field

This avoids the model having to guess whether `electronics` means a category, tag, label, type, or project.

### 3.4 Require confirmation when confidence is low

The bot should create immediately only when all required fields are resolved with high confidence. Otherwise it should post a parsed preview and require explicit confirmation.

---

## 4. Recommended Architecture

```text
Discord Slash Command
   -> Bot Webhook Endpoint (FastAPI)
      -> Command Router
         -> LLM Parser
         -> Metadata Resolver / Validator
         -> OpenProject Service (REST API)
         -> Audit Logger
      -> Discord Response

Optional Read Path:
LLM Router -> OpenProject MCP Client -> summarized result
```

### 4.1 Components

#### A. Discord interaction layer
Receives slash command payloads and component interactions (buttons for confirm/cancel).

#### B. Application service layer
Owns command orchestration, validation, permissions, and API integration.

#### C. LLM parsing layer
Converts raw text to strict structured JSON.

#### D. Metadata cache layer
Caches projects, types, statuses, priorities, custom field values, and optional user mappings.

#### E. OpenProject integration layer
Handles:

- auth,
- metadata fetch,
- work package form/schema lookup,
- create/update/comment requests,
- retry behavior,
- error normalization.

#### F. Persistence layer
Stores:

- command logs,
- parsed payloads,
- validation outcomes,
- confirmation tokens,
- execution results,
- optional Discord ↔ OpenProject user mappings.

#### G. Deployment/runtime layer
Docker container running on the VPS behind Nginx/Caddy/Traefik or an existing reverse proxy.

---

## 5. Tech Stack Recommendation

### Primary recommendation

- **Language:** Python 3.12+
- **API framework:** FastAPI
- **Validation:** Pydantic v2
- **HTTP client:** httpx
- **Database:** PostgreSQL
- **Caching:** Redis optional, otherwise DB + in-memory cache
- **Discord integration:** direct interactions endpoint or discord.py for command registration support
- **Containerization:** Docker + Docker Compose
- **Process runtime:** uvicorn or gunicorn+uvicorn workers
- **Reverse proxy:** existing VPS Nginx/Caddy
- **Secrets:** `.env` locally, VPS environment or Docker secrets in deployment

### Why this stack

FastAPI is a good fit for webhook-style services and supports deployment behind a reverse proxy. The official docs include deployment guidance for Docker, HTTPS, and proxy-aware routing. ([fastapi.tiangolo.com](https://fastapi.tiangolo.com/advanced/behind-a-proxy/?utm_source=chatgpt.com))

---

## 6. Repository Layout

```text
openproject-discord-assistant/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ api/
│  │  ├─ discord.py
│  │  ├─ health.py
│  │  └─ admin.py
│  ├─ core/
│  │  ├─ logging.py
│  │  ├─ security.py
│  │  ├─ exceptions.py
│  │  └─ metrics.py
│  ├─ llm/
│  │  ├─ client.py
│  │  ├─ schemas.py
│  │  ├─ prompts.py
│  │  └─ parser.py
│  ├─ discord/
│  │  ├─ verify.py
│  │  ├─ responses.py
│  │  ├─ commands.py
│  │  └─ components.py
│  ├─ openproject/
│  │  ├─ client.py
│  │  ├─ schemas.py
│  │  ├─ metadata.py
│  │  ├─ mapper.py
│  │  ├─ validator.py
│  │  └─ mcp_client.py
│  ├─ services/
│  │  ├─ command_router.py
│  │  ├─ create_issue.py
│  │  ├─ confirm_action.py
│  │  ├─ sync_metadata.py
│  │  └─ audit.py
│  ├─ db/
│  │  ├─ base.py
│  │  ├─ models.py
│  │  ├─ session.py
│  │  └─ migrations/
│  └─ tests/
│     ├─ unit/
│     ├─ integration/
│     └─ fixtures/
├─ scripts/
│  ├─ register_discord_commands.py
│  ├─ sync_openproject_metadata.py
│  └─ smoke_test.py
├─ docker/
│  ├─ Dockerfile
│  └─ docker-compose.yml
├─ .env.example
├─ pyproject.toml
├─ README.md
└─ docs/
   ├─ architecture.md
   ├─ deployment.md
   └─ runbooks.md
```

---

## 7. Data Model

### 7.1 Core database tables

#### `command_audit_log`
Fields:

- id
- discord_interaction_id
- discord_user_id
- discord_username
- raw_command
- parsed_action_json
- validation_result_json
- execution_status
- openproject_work_package_id nullable
- error_code nullable
- error_message nullable
- created_at

#### `pending_confirmations`
Fields:

- id
- token
- discord_user_id
- expires_at
- parsed_action_json
- validation_result_json
- status (`pending`, `confirmed`, `cancelled`, `expired`)
- created_at

#### `project_mappings`
Fields:

- id
- human_name
- openproject_project_id
- openproject_project_identifier
- aliases_json
- active
- updated_at

#### `field_value_mappings`
Fields:

- id
- field_name
- human_value
- openproject_value
- aliases_json
- active
- updated_at

#### `discord_openproject_user_mappings` (optional v1.1)
Fields:

- id
- discord_user_id
- discord_username
- openproject_user_id
- openproject_login
- active
- updated_at

#### `metadata_sync_state`
Fields:

- id
- metadata_kind
- last_synced_at
- checksum nullable
- status

---

## 8. Command Surface

### 8.1 v1 slash commands

#### `/pm create`
Arguments:

- `request` (string, required)

Examples:

- `/pm create request:"create a new issue in the space1 project for electronics, design pcb"`
- `/pm create request:"space1 bug electronics pcb trace width issue on rev b"`

#### `/pm help`
Returns supported formats and examples.

#### `/pm projects`
Returns visible project list or key project aliases.

### 8.2 v1.1 commands

- `/pm comment`
- `/pm update`
- `/pm search`
- `/pm summarize`

### 8.3 Discord buttons

- `Confirm`
- `Cancel`

Discord’s official interactions and application command docs cover slash commands and interaction payload handling. ([docs.discord.com](https://docs.discord.com/developers/platform/interactions?utm_source=chatgpt.com))

---

## 9. LLM Contract

### 9.1 Model responsibilities

Input:

- raw user request
- command type
- allowed projects and aliases
- allowed work package types
- allowed custom field names and candidate values
- optional example outputs

Output:

Strict JSON only.

### 9.2 Output schema for v1

```json
{
  "action": "create_work_package",
  "project_ref": "space1",
  "type_ref": "Task",
  "subject": "Design PCB",
  "description": "Create PCB design task for electronics workstream.",
  "custom_fields": {
    "Domain": "electronics"
  },
  "priority_ref": null,
  "assignee_ref": null,
  "due_date": null,
  "confidence": 0.91,
  "ambiguities": []
}
```

### 9.3 System prompt principles

The system prompt should instruct the model to:

- never invent IDs,
- only use names from the provided candidates where possible,
- leave unresolved values null,
- surface ambiguities explicitly,
- keep subjects short and action-oriented,
- use the raw request as grounding.

### 9.4 Confidence policy

Use a backend threshold, not only model-provided confidence.

Suggested policy:

- auto-execute if all required fields resolve and no ambiguities remain,
- require confirmation if any required field is guessed or multiple matches exist,
- reject if no valid project or no valid subject can be derived.

---

## 10. OpenProject Integration Design

### 10.1 Authentication

Use a dedicated bot account or service token.

Recommended pattern:

- create a dedicated OpenProject user such as `discord-bot`
- generate a personal access token for that user
- restrict the account to the projects and permissions needed

### 10.2 Metadata synchronization

Sync these regularly from OpenProject:

- projects
- project identifiers
- enabled work package types per project
- priorities
n- statuses if needed later
- custom field definitions
- allowed custom field values
- optional list of assignable users per project

OpenProject’s work package API notes that plugins and custom fields can change the available schema and that clients should consult schema information. Project settings also determine which work package types are enabled in each project. ([openproject.org](https://www.openproject.org/docs/api/endpoints/work-packages/?utm_source=chatgpt.com))

### 10.3 Work package creation flow

Preferred robust flow:

1. Resolve project.
2. Resolve type.
3. Load create form/schema for that project/type.
4. Build payload only with allowed fields.
5. Submit create request.
6. Parse created work package response.
7. Store audit log.

The official API examples emphasize the create form workflow and `Content-Type: application/json` for state-changing requests. ([openproject.org](https://www.openproject.org/docs/api/example/?utm_source=chatgpt.com))

### 10.4 Error handling

Normalize OpenProject failures into app-level errors:

- `PROJECT_NOT_FOUND`
- `TYPE_NOT_ALLOWED`
- `INVALID_CUSTOM_FIELD_VALUE`
- `AUTH_FAILED`
- `RATE_LIMITED`
- `VALIDATION_FAILED`
- `OPENPROJECT_UNAVAILABLE`

### 10.5 MCP integration

Treat MCP as optional and read-only:

- use for issue search,
- project summarization,
- duplicate detection assistance,
- context enrichment before create.

Do not use MCP for writes because OpenProject documents the current MCP feature as experimental and read-only. ([openproject.org](https://www.openproject.org/docs/system-admin-guide/integrations/mcp-server/?utm_source=chatgpt.com))

---

## 11. Validation and Resolution Strategy

### 11.1 Entity resolution

When the LLM returns references such as `space1` and `electronics`, the backend should resolve them using:

1. exact alias match,
2. case-insensitive exact match,
3. normalized slug match,
4. fuzzy match above a strict threshold,
5. otherwise mark ambiguous/unresolved.

### 11.2 Subject generation policy

If the subject is missing or poor:

- derive it from the request using deterministic cleanup,
- keep the original request in the description,
- optionally append `Requested via Discord by <username>`.

### 11.3 Project-scoped validation

A field can be valid globally but invalid for a project. Validation must therefore occur against the target project’s allowed types and schema.

### 11.4 Idempotency / duplicate risk

To avoid accidental duplicate issues:

- store the last successful create hash per user for a short time window,
- optionally search recent similar work packages before create,
- show a warning if a very similar issue already exists.

---

## 12. Discord Interaction Flow

### 12.1 Immediate acknowledgement

Discord interactions should be acknowledged quickly. Use deferred responses when processing takes longer than a very short interval.

### 12.2 Success response

Return:

- work package ID/reference,
- subject,
- project,
- direct URL,
- any normalized fields.

Example:

```text
Created work package #1234
Project: space1
Type: Task
Domain: electronics
Subject: Design PCB
Link: https://openproject.example.com/work_packages/1234
```

### 12.3 Confirmation response

Example:

```text
I parsed your request as:
- Action: Create work package
- Project: space1
- Type: Task
- Domain: electronics
- Subject: Design PCB

Confirm?
```

Buttons:

- Confirm
- Cancel

### 12.4 Error response

Make errors operationally useful.

Example:

```text
I could not create the work package because `electronics` is not a valid Domain value in project `space1`.
Allowed values: electronics-hw, electronics-fw, mechanical
```

---

## 13. Security Plan

### 13.1 Secret handling

Secrets required:

- Discord public key for request verification
- Discord bot/application credentials
- OpenProject API token
- LLM API key
- database credentials

Rules:

- never hardcode secrets,
- use `.env` only locally,
- use VPS environment injection or Docker secrets in deployment,
- rotate tokens periodically.

### 13.2 Request verification

Verify Discord request signatures on every interaction request.

### 13.3 Network design

Recommended deployment topology:

- Discord sends HTTPS requests to your VPS domain
- reverse proxy terminates TLS
- bot app runs on private localhost Docker network
- bot app talks to OpenProject via internal VPS network or public domain with TLS

### 13.4 Authorization policy

For v1, simplest policy:

- only allow the bot in specific Discord servers/channels/roles,
- optionally map allowed Discord roles to allowed OpenProject projects.

### 13.5 OpenProject permissions

Use least privilege:

- create work packages only where needed,
- no delete permissions,
- no admin permissions,
- no global project management.

---

## 14. Local Development Plan

### 14.1 Development environment

The code is developed on the personal machine while OpenProject is hosted on the VPS.

Recommended local setup:

- run the bot app locally in Docker or a Python virtualenv,
- point the app to the VPS OpenProject base URL,
- use a development OpenProject bot token,
- expose the local webhook endpoint to Discord via a tunnel during local development.

Options for temporary public ingress during local development:

- Cloudflare Tunnel
- ngrok
- Tailscale Funnel

### 14.2 Local environment variables

Example `.env.local`:

```env
APP_ENV=development
APP_BASE_URL=https://your-dev-tunnel.example
DISCORD_PUBLIC_KEY=...
DISCORD_APPLICATION_ID=...
DISCORD_BOT_TOKEN=...
OPENPROJECT_BASE_URL=https://openproject.yourdomain.com
OPENPROJECT_API_TOKEN=...
LLM_API_KEY=...
DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/opbot
LOG_LEVEL=DEBUG
```

### 14.3 Local run modes

Mode A: no Discord, direct local tests
- call the internal service functions with fixtures

Mode B: Discord end-to-end
- register dev guild commands
- expose webhook through a tunnel
- use Discord test server only

### 14.4 Local development tasks

- register slash commands for a dev guild
- sync metadata from OpenProject VPS
- test create flow against a sandbox project
- test ambiguous parsing and confirmation buttons
- test error handling for invalid values

---

## 15. VPS Deployment Plan

### 15.1 Deployment target assumptions

- OpenProject already runs on the VPS
- domain and TLS are already available or can be added
- Docker is acceptable for the new bot service

### 15.2 Recommended deployment topology

```text
Internet
  -> Reverse Proxy (Nginx/Caddy/Traefik)
      -> /discord/interactions -> Bot Container
      -> /health -> Bot Container
      -> OpenProject continues on its existing route/domain

Bot Container
  -> PostgreSQL Container or existing Postgres
  -> optional Redis Container
  -> OpenProject API over HTTPS or internal network
```

### 15.3 DNS / routing options

#### Option A: separate subdomain
- `bot.example.com` -> bot service
- `openproject.example.com` -> OpenProject

Recommended for clarity.

#### Option B: same domain, separate path
- `example.com/openproject`
- `example.com/discord-bot`

Works, but is more fragile operationally.

### 15.4 Docker Compose services

Recommended services:

- `op-discord-bot`
- `op-discord-bot-db`
- `op-discord-bot-redis` optional

### 15.5 Production environment variables

```env
APP_ENV=production
APP_BASE_URL=https://bot.example.com
DISCORD_PUBLIC_KEY=...
DISCORD_APPLICATION_ID=...
DISCORD_BOT_TOKEN=...
OPENPROJECT_BASE_URL=https://openproject.example.com
OPENPROJECT_API_TOKEN=...
LLM_API_KEY=...
DATABASE_URL=postgresql+psycopg://...
REDIS_URL=redis://...
LOG_LEVEL=INFO
```

### 15.6 Deployment sequence

1. Provision bot database.
2. Build image.
3. Configure secrets.
4. Start app behind reverse proxy.
5. Run database migrations.
6. Register production Discord commands.
7. Run metadata sync.
8. Perform smoke test.
9. Restrict Discord command visibility if desired.

---

## 16. Operational Concerns

### 16.1 Logging

Structured JSON logs with fields:

- request_id
- discord_interaction_id
- discord_user_id
- command_name
- execution_stage
- openproject_project_id
- openproject_work_package_id
- latency_ms
- error_code

### 16.2 Metrics

Expose a `/metrics` endpoint if Prometheus is available.

Key metrics:

- request count
- create success rate
- confirmation rate
- validation failure rate
- OpenProject API latency
- LLM latency
- metadata sync age

### 16.3 Health checks

- `/health/live`
- `/health/ready`

Readiness should verify:

- DB connectivity
- OpenProject reachability
- optionally LLM provider reachability

### 16.4 Runbooks

Include runbooks for:

- Discord signature verification failures
- OpenProject auth failures
- metadata sync failures
- LLM provider downtime
- database migration failures

---

## 17. Testing Strategy

### 17.1 Unit tests

Test:

- request parsing
- entity normalization
- alias matching
- confidence policy
- payload construction
- error normalization

### 17.2 Integration tests

Use mocked Discord payloads and either:

- a test OpenProject project on the VPS,
- or mocked OpenProject endpoints for non-destructive tests.

### 17.3 End-to-end tests

In a dev Discord server:

- `/pm create request:"create task in space1 for electronics, design pcb"`
- verify work package created
- verify confirmation flow
- verify invalid value handling

### 17.4 Regression fixtures

Create a corpus of real or representative commands:

- obvious create requests
- messy shorthand
- ambiguous project names
- invalid field values
- duplicate-like requests
- multilingual or shorthand variations if relevant

---

## 18. Suggested Development Phases for Codex

### Phase 0 — Foundation
Deliverables:

- repo scaffold
- config management
- Dockerfile + docker-compose
- FastAPI app skeleton
- health endpoints
- PostgreSQL models and migrations
- structured logging

Acceptance criteria:

- app starts locally
- health endpoints respond
- DB migrations run

### Phase 1 — Discord webhook integration
Deliverables:

- Discord signature verification
- interaction endpoint
- slash command registration script
- simple `/pm help`

Acceptance criteria:

- local dev guild command works
- signature verification passes
- help response visible in Discord

### Phase 2 — OpenProject client and metadata sync
Deliverables:

- OpenProject client
- project/type/custom field metadata sync
- local persistence of mappings
- admin/debug endpoint to inspect synced metadata

Acceptance criteria:

- metadata sync completes against VPS OpenProject
- synced projects and field values are queryable locally

### Phase 3 — LLM parser and validation pipeline
Deliverables:

- LLM client wrapper
- strict output schema
- parser service
- resolution and validation service
- unit tests for representative commands

Acceptance criteria:

- raw commands parse to valid JSON
- unresolved fields are surfaced explicitly
- invalid values are rejected before API calls

### Phase 4 — Create work package command
Deliverables:

- `/pm create`
- confirmation flow for ambiguity
- OpenProject work package creation
- audit log persistence
- success/error responses

Acceptance criteria:

- known-good command creates a work package
- ambiguous command produces confirmation prompt
- invalid command fails gracefully

### Phase 5 — Production deployment to VPS
Deliverables:

- production Docker Compose
- reverse proxy config sample
- environment variable docs
- migration and deployment scripts
- smoke test procedure

Acceptance criteria:

- bot reachable from Discord over HTTPS on VPS
- creates work package in production OpenProject
- logs and health checks function

### Phase 6 — Optional MCP read-path integration
Deliverables:

- feature-flagged MCP client
- `/pm search`
- `/pm summarize`
- duplicate-detection helper before create

Acceptance criteria:

- read-only searches work when MCP is enabled
- write path remains fully REST-based

---

## 19. Codex Task Breakdown

Provide Codex with these concrete work items in order.

### Task 1: Scaffold project
Build the repository structure, config system, Docker setup, and FastAPI app with health endpoints.

### Task 2: Implement database layer
Create SQLAlchemy models, Alembic migrations, and DB session handling for audit logs, confirmations, and metadata mappings.

### Task 3: Implement Discord request verification and routing
Add the `/discord/interactions` endpoint, verify signatures, parse interaction payloads, and support deferred responses.

### Task 4: Implement OpenProject API client
Add authenticated HTTP client methods for:

- listing projects,
- fetching project-specific types,
- fetching create form/schema,
- creating work packages,
- normalizing API errors.

### Task 5: Implement metadata sync
Create scheduled/manual sync code to cache OpenProject projects, aliases, types, and configured custom field values in the DB.

### Task 6: Implement LLM parser
Define strict Pydantic schemas, prompts, and a parser service that maps natural language into candidate action JSON.

### Task 7: Implement resolver/validator
Resolve project/type/custom field references against synced metadata and produce either:

- executable payload,
- confirmation payload,
- or validation error.

### Task 8: Implement `/pm create`
Wire the full create flow from Discord command to OpenProject work package creation and response formatting.

### Task 9: Implement confirmation buttons
Add button interaction handlers for confirm/cancel using persisted pending confirmation tokens.

### Task 10: Add tests
Add unit, integration, and smoke tests for the create path.

### Task 11: Add production deployment assets
Create production-ready Docker Compose, sample reverse proxy config, and deployment documentation.

### Task 12: Optional MCP integration
Add a feature-flagged read-only MCP client and commands for search/summarize.

---

## 20. Prompt Pack for Codex

### System-level instruction for Codex

Implement a production-ready Python FastAPI service that integrates Discord slash commands with OpenProject. Use the OpenProject REST API for write operations. Treat OpenProject MCP as optional and read-only only. The service must run locally for development and be deployable via Docker Compose to a VPS. Emphasize maintainability, strict validation, typed models, tests, and security.

### Additional constraints for Codex

- Use Python 3.12+
- Use FastAPI, Pydantic v2, SQLAlchemy, Alembic, and httpx
- Prefer pure HTTP interactions over heavy Discord bot gateway dependencies unless required
- Verify Discord signatures on incoming requests
- Use a service-oriented module layout
- All LLM outputs must be validated with Pydantic before use
- Do not let the LLM generate direct API payloads without backend validation
- Add structured logging and health endpoints
- Provide Docker and Docker Compose files
- Write tests for parsing, validation, and create flow

### Codex implementation instruction for the create command

Implement `/pm create` where the user supplies a free-text request. The system should parse the request into structured fields, resolve those fields against cached OpenProject metadata, validate the result against the target project schema, and create the work package only if validation succeeds. If the request is ambiguous, return a Discord confirmation prompt with Confirm and Cancel buttons.

---

## 21. Example Internal Schemas

### Parsed action schema

```python
class ParsedCreateAction(BaseModel):
    action: Literal["create_work_package"]
    project_ref: str | None = None
    type_ref: str | None = None
    subject: str | None = None
    description: str | None = None
    custom_fields: dict[str, str | int | bool | None] = Field(default_factory=dict)
    priority_ref: str | None = None
    assignee_ref: str | None = None
    due_date: date | None = None
    confidence: float = 0.0
    ambiguities: list[str] = Field(default_factory=list)
```

### Resolved action schema

```python
class ResolvedCreateAction(BaseModel):
    project_id: int
    type_id: int
    subject: str
    description: str | None = None
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    priority_id: int | None = None
    assignee_id: int | None = None
    due_date: date | None = None
    needs_confirmation: bool = False
    confirmation_reasons: list[str] = Field(default_factory=list)
```

---

## 22. Example API Flow

### Request from Discord

```text
/pm create request:"create a new issue in the space1 project for electronics, design pcb"
```

### Parsed by LLM

```json
{
  "action": "create_work_package",
  "project_ref": "space1",
  "type_ref": "Task",
  "subject": "Design PCB",
  "description": "Create a PCB design task for the electronics area.",
  "custom_fields": {
    "Domain": "electronics"
  },
  "confidence": 0.92,
  "ambiguities": []
}
```

### Resolved by backend

```json
{
  "project_id": 42,
  "type_id": 7,
  "subject": "Design PCB",
  "description": "Create a PCB design task for the electronics area.\n\nRequested via Discord by alice.",
  "custom_fields": {
    "Domain": "electronics"
  },
  "needs_confirmation": false,
  "confirmation_reasons": []
}
```

### Create result returned to Discord

```text
Created work package #1234 in space1
Subject: Design PCB
Domain: electronics
https://openproject.example.com/work_packages/1234
```

---

## 23. Risks and Mitigations

### Risk: model invents invalid values
Mitigation:
- strict candidate lists
- backend validation
- no direct API execution from model output

### Risk: OpenProject custom fields differ from assumptions
Mitigation:
- metadata sync
- form/schema lookup before create

### Risk: Discord webhook endpoint exposed publicly
Mitigation:
- signature verification
- reverse proxy hardening
- rate limiting

### Risk: duplicate issues from repeated commands
Mitigation:
- short-window idempotency hash
- optional duplicate search warning

### Risk: production drift between local and VPS
Mitigation:
- Dockerized local environment
- environment-specific config files
- migration-based schema management

### Risk: MCP instability
Mitigation:
- feature flag
- never use for writes
- keep core flows REST-based

---

## 24. Recommended Implementation Order

1. Scaffold app and infrastructure
2. Add Discord interaction endpoint
3. Add OpenProject client
4. Sync metadata
5. Add parser and validation pipeline
6. Add create issue flow
7. Add confirmation buttons
8. Add audit logging and tests
9. Deploy to VPS
10. Add optional read/search features and MCP later

---

## 25. Final Recommendation

The most robust production design is:

- **Discord slash commands** as the user interface,
- **FastAPI service** as the orchestration layer,
- **OpenProject REST API** for all writes,
- **LLM only for structured parsing and summarization**,
- **OpenProject MCP only as an optional read-only helper**,
- **Docker Compose deployment on the VPS** with separate bot service, database, and reverse proxy routing.

This design fits local development on a personal machine, works cleanly with an OpenProject instance already running on a VPS, and keeps the system dependable as the natural-language interface becomes more flexible.

