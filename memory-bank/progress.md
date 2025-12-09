# Memory Bank: Progress

## Build Status
- Implemented `loki_push.py` CLI (env loading, labels, TLS toggle, verbose/dry-run, requests as required HTTP client).
- Added README instructions with `.env` template (file not created due to ignore; user to supply real `.env`).
- Archived: `memory-bank/archive/archive-loki-demo.md`.
- New task: refactor to use `logging_loki` backend with same CLI semantics. (DONE: transport swapped to `logging_loki.LokiHandler`, CLI/env behavior preserved, TLS verify toggle applied to handler session.)
- Archived: `memory-bank/archive/archive-loki-logging-handler.md`.

## Testing
- E2E: success (HTTP 204) with `.env` credentials after endpoint/username/token normalization. Verbose mode confirmed correct payload/labels.
- For new transport: not re-run with real creds yet; dry-run and code-path validated locally. Fresh e2e pending.

