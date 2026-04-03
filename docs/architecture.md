# Architecture

The service receives Discord interactions at `POST /discord/interactions`, verifies signatures, routes `/pm create`, parses user text with an LLM, validates against locally synced OpenProject metadata, and creates work packages through the OpenProject REST API.

Core flow:

1. Discord interaction arrives.
2. Signature verified using Ed25519 public key.
3. Command routed to create service.
4. LLM parser returns structured JSON.
5. Validator resolves project/type/custom fields using DB metadata.
6. OpenProject client creates work package.
7. Audit log row stored.
8. Discord response returned.
