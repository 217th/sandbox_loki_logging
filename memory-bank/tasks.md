# Memory Bank: Tasks

## Current Task
- [COMPLETED] Rework the Loki demo script to use `logging_loki` while keeping all existing functionality (env/CLI options, labels, verbose/dry-run, TLS toggle).
- [COMPLETED] Demo Python 3.13 script to push test events to Grafana Cloud Loki.

## Complexity
- Level 2 (Simple Enhancement) — small scope change to swap transport layer to `logging_loki` with existing CLI semantics.

## Plan
- Add dependency `logging_loki` (keep `requests`, `python-dotenv`).
- Refactor `loki_push.py` to use `logging_loki.LokiHandler` (or queue handler) while preserving:
  - Same CLI/env options (endpoint base URL, username/password, labels, verbose, dry-run, insecure TLS toggle, count/message formatting).
  - Endpoint remains base (`https://<stack>.grafana.net`), script appends `/loki/api/v1/push`.
  - Labels default (`app=demo`, `host`, `env=local`) plus overrides/extra labels.
  - Diagnostics: verbose should show URL, labels, verify flag, env sources; warn on bad status.
- Handle handler kwargs compatibility: pass `verify` if supported; otherwise warn and proceed.
- Dry-run: skip sending but show resolved config/payload preview.
- Testing: run local dry-run; if creds available, expect HTTP 204 with real `.env`.
- Archived previous plan: see `memory-bank/archive/archive-loki-demo.md`.

## Build
- Implemented: transport swapped to `logging_loki.LokiHandler`, keeps CLI/env flags, labels defaults/overrides, verbose/dry-run, TLS toggle. Handler session uses verify flag; closes after send.
- Docs: README updated (English) noting `logging_loki`, endpoint base rule; requirements updated.
- Reflection: `memory-bank/reflection/reflection-loki-logging-handler.md`.
- Archive: `memory-bank/archive/archive-loki-logging-handler.md`.

## Reflection
- Completed for current task: `memory-bank/reflection/reflection-loki-logging-handler.md`.
- Completed for previous task: `memory-bank/reflection/reflection-loki-demo.md`.

