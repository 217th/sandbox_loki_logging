# Grafana Loki Demo Push Script

Python 3.13 CLI to send test log events to Grafana Cloud Loki.

## Quick start
1) Install dependencies (Python 3.13):
   ```bash
   pip install -r requirements.txt
   ```

2) Create `.env` next to this file (note: `LOKI_ENDPOINT` must be the base URL only; do **not** include `/loki/api/v1/push` because the script appends it automatically):
   ```
   LOKI_ENDPOINT=https://<stack>.grafana.net
   LOKI_USERNAME=<tenant-id>
   LOKI_PASSWORD=<api-token-with-logs-write>
   LOKI_LABELS=app=demo,env=local
   LOKI_INSECURE=0
   LOKI_VERBOSE=0
   ```

3) Send test logs (transport uses `logging_loki` under the hood):
   ```bash
   python loki_push.py --count 3 --message "hello from demo"
   ```

4) Check result:
   - Expected HTTP status: `204`.
   - On issues, enable `--verbose` and/or temporarily `--insecure` (trusted env only).

## CLI options
- `--endpoint`, `--username`, `--password`: override env.
- `--label key=value`: repeatable; overrides defaults (`app=demo`, `host=<hostname>`).
- `--count N`, `--interval seconds`, `--message "text"`.
- `--insecure`: disable TLS verification (testing only).
- `--verbose`: print request/response details.
- `--dry-run`: print payload without sending.

Requires `python-dotenv`, `requests`, and `python-logging-loki` (installed via `requirements.txt`). Expected success status: 204.