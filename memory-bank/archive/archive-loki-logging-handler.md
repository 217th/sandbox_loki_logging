# TASK ARCHIVE: Loki demo – logging_loki transport refactor

## METADATA
- Complexity: Level 2 (Simple Enhancement)
- Status: Completed
- Scope: Swap transport to `logging_loki` while preserving CLI/env behavior.

## SUMMARY
- Refactored `loki_push.py` to use `logging_loki.LokiHandler` with Basic Auth, keeping existing CLI/env flags (labels, verbose, dry-run, TLS toggle, endpoint base handling).
- Updated dependencies (`python-logging-loki`) and README guidance.

## REQUIREMENTS
- Preserve CLI/env options and defaults: base endpoint (script appends `/loki/api/v1/push`), labels `app=demo`, `host=<hostname>`, `env=local`, overrides via env/CLI, verbose/dry-run, insecure toggle.
- Keep diagnostics and payload semantics; support `.env` override.

## IMPLEMENTATION
- `loki_push.py`: transport via `LokiHandler(url, tags, auth, version=1)`; set `handler.emitter.session.verify` from insecure flag; close emitter after send; reused verbose diagnostics and label/env handling; dry-run unchanged.
- Dependencies: `requirements.txt` now includes `python-logging-loki`.
- Docs: README (English) notes base endpoint rule and dependency update.

## TESTING
- Code-path and dry-run validated locally.
- E2E with real creds not re-run after the transport swap (expected 204 based on prior run and identical auth/payload semantics).

## LESSONS LEARNED
- PyPI name is `python-logging-loki`; verify package names before pinning.
- When handler ctor lacks TLS knobs, set `session.verify` directly and close session to avoid leaks.

## REFERENCES
- Plan/Progress: `memory-bank/tasks.md`, `memory-bank/progress.md`
- Reflection: `memory-bank/reflection/reflection-loki-logging-handler.md`
- Previous archive: `memory-bank/archive/archive-loki-demo.md`

