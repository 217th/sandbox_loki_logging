#!/usr/bin/env python3
"""
CLI для отправки тестовых логов в Grafana Cloud Loki.

Кратко (рус):
- Грузит переменные из `.env` через python-dotenv (обязательно).
- Аутентификация Basic: username/token + password/API token.
- Лейблы из ENV/CLI, дефолтно app=demo, host=<hostname>.
- Режимы verbose/dry-run, опция отключения проверки TLS.
- Требует библиотеку requests (обязательно).
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    import requests  # type: ignore
except Exception:
    print("[error] requests not installed. Please install with `pip install requests`.", file=sys.stderr)
    sys.exit(1)

try:
    import dotenv  # type: ignore
except Exception:
    # Без python-dotenv не сможем загрузить .env. Завершаем работу с подсказкой.
    print("[error] python-dotenv not installed. Please install with `pip install python-dotenv`.", file=sys.stderr)
    sys.exit(1)


def load_env_file(path: str = ".env") -> None:
    """
    Загрузить переменные окружения из .env, если файл есть.
    override=True — значения из .env перекрывают то, что могло остаться в окружении.
    """
    if os.path.exists(path):
        dotenv.load_dotenv(path, override=True)


def parse_env_bool(value: Optional[str]) -> bool:
    """Интерпретировать строку ENV как bool (1/true/yes/on)."""
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_labels(env_labels: Optional[str], cli_labels: Optional[List[str]]) -> Dict[str, str]:
    """
    Собирает лейблы:
    - базовые app=demo, host=<hostname>
    - потом ENV (LOKI_LABELS="k=v,foo=bar")
    - потом CLI (--label k=v), CLI перекрывает ENV.
    """
    labels: Dict[str, str] = {
        "app": "demo",
        "host": socket.gethostname(),
    }

    def apply(kv: str) -> None:
        if "=" not in kv:
            return
        k, v = kv.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k:
            labels[k] = v

    if env_labels:
        for item in env_labels.split(","):
            apply(item)
    if cli_labels:
        for item in cli_labels:
            apply(item)
    return labels


def build_payload(labels: Dict[str, str], messages: List[str]) -> Dict[str, object]:
    """
    Формирует тело push-запроса Loki:
    streams: [{stream: labels, values: [[timestamp_ns, message], ...]}]
    Loki требует timestamp в наносекундах строкой.
    """
    now_ns = time.time_ns()
    values = []
    for idx, message in enumerate(messages, start=1):
        ts_ns = now_ns + idx  # гарантируем монотонный рост, даже если time_ns вернет одинаковое значение
        values.append([str(ts_ns), message])
    return {"streams": [{"stream": labels, "values": values}]}


def format_message(base: str, idx: int) -> str:
    """Добавляет к базовому сообщению порядковый номер и ISO-время (UTC) для удобного чтения."""
    iso_ts = datetime.now(timezone.utc).isoformat()
    return f"{base} | idx={idx} | ts={iso_ts}"


def send_with_requests(
    url: str,
    payload: Dict[str, object],
    username: str,
    password: str,
    verify: bool,
    verbose: bool,
) -> int:
    """Отправка через requests. Возвращает HTTP статус или -1 при ошибке."""
    try:
        resp = requests.post(
            url,
            json=payload,
            auth=(username, password),
            headers={"Content-Type": "application/json"},
            timeout=10,
            verify=verify,
        )
        body = resp.text
        if verbose:
            print(f"[requests] status={resp.status_code} body={body}")
        if resp.status_code != 204:
            print(f"[warn] HTTP {resp.status_code} from Loki at {url}", file=sys.stderr)
            if body:
                print(f"[warn] Response body: {body}", file=sys.stderr)
            print(
                "[hint] 404/401 часто означают неверный endpoint или креды. "
                "Проверьте базовый URL (должен заканчиваться на stack). "
                "Скрипт добавляет /loki/api/v1/push автоматически; "
                "убедитесь, что схема https:// и правильный поддомен/stack id.",
                file=sys.stderr,
            )
        return resp.status_code
    except Exception as exc:
        print(f"[error] requests failed: {exc}", file=sys.stderr)
        return -1


def main(argv: Optional[List[str]] = None) -> int:
    # 1) Подхватываем переменные из .env (не трогаем уже заданные в окружении).
    load_env_file(".env")

    # 2) Разбор аргументов CLI.
    parser = argparse.ArgumentParser(description="Send demo logs to Grafana Cloud Loki")
    parser.add_argument("--endpoint", help="Base URL, e.g. https://<stack>.grafana.net")
    parser.add_argument("--username", help="Loki username / tenant ID")
    parser.add_argument("--password", help="Loki password or API token")
    parser.add_argument("--label", action="append", help="Label key=value (can repeat)")
    parser.add_argument("--message", default="hello from loki demo", help="Base message text")
    parser.add_argument("--count", type=int, default=5, help="Number of messages to send")
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds between messages")
    parser.add_argument("--insecure", action="store_true", help="Disable TLS verification")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without sending")

    args = parser.parse_args(argv)

    # 3) Креды и настройки берём из CLI или ENV (CLI приоритетнее).
    def env_clean(name: str) -> Optional[str]:
        """
        Чистим значение ENV:
        - убираем префикс 'export ' если прописали в .env
        - стрип пробелы/кавычки по краям
        """
        val = os.getenv(name)
        if val is None:
            return None
        cleaned = val.strip()
        if cleaned.lower().startswith("export "):
            cleaned = cleaned[7:].strip()
        # убираем обрамляющие кавычки, если есть
        if (cleaned.startswith('"') and cleaned.endswith('"')) or (cleaned.startswith("'") and cleaned.endswith("'")):
            cleaned = cleaned[1:-1].strip()
        return cleaned

    endpoint = (args.endpoint or env_clean("LOKI_ENDPOINT")) or None
    username = (args.username or env_clean("LOKI_USERNAME")) or None
    password = (args.password or env_clean("LOKI_PASSWORD")) or None
    env_labels = env_clean("LOKI_LABELS")
    insecure = args.insecure or parse_env_bool(env_clean("LOKI_INSECURE"))
    verbose = args.verbose or parse_env_bool(env_clean("LOKI_VERBOSE"))

    # 4) Проверяем, что обязательные параметры заданы.
    if not endpoint or not username or not password:
        print("[error] Missing required credentials. Provide --endpoint/--username/--password or set LOKI_ENDPOINT/LOKI_USERNAME/LOKI_PASSWORD.", file=sys.stderr)
        return 1

    # 5) Собираем итоговый URL и лейблы.
    push_url = endpoint.rstrip("/") + "/loki/api/v1/push"
    labels = parse_labels(env_labels, args.label)

    # 6) Формируем сообщения и payload для одного запроса.
    messages = [format_message(args.message, i) for i in range(1, args.count + 1)]
    payload = build_payload(labels, messages)

    # 7) Dry-run: просто печатаем JSON.
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    # 8) Отладочная печать.
    if verbose:
        print(f"[info] sending to {push_url}")
        print(f"[info] labels={labels}")
        print(f"[info] verify_tls={not insecure}")
        user_preview = (username[:4] + "…" + username[-2:]) if username and len(username) > 6 else username
        pw_preview = ""
        if password:
            pw_preview = f"{password[:4]}…{password[-4:]}" if len(password) > 8 else "***"
        def warn_if_contains(ctrl: str, name: str, val: Optional[str]) -> None:
            if val and any(c in val for c in ctrl):
                print(f"[warn] {name} contains control/whitespace chars", file=sys.stderr)
        warn_if_contains("\r\n\t ", "password", password)
        warn_if_contains("\r\n\t ", "username", username)
        print(
            "[debug] endpoint_env={ep} username_env={un} password_env={pw} "
            "username_preview={up} username_len={ul} password_len={pl} password_preview={pp}".format(
                ep=bool(env_clean("LOKI_ENDPOINT")),
                un=bool(env_clean("LOKI_USERNAME")),
                pw="***" if env_clean("LOKI_PASSWORD") else "",
                up=user_preview or "",
                ul=len(username or ""),
                pl=len(password or ""),
                pp=pw_preview,
            )
        )

    # 9) Отправляем, выбирая доступный HTTP клиент.
    status = send_with_requests(push_url, payload, username, password, verify=not insecure, verbose=verbose)

    # 10) Проверяем результат.
    if status == 204:
        print("[ok] Loki accepted payload (204).")
        return 0

    print(f"[warn] Unexpected status {status}. Check credentials, endpoint, or TLS settings.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

