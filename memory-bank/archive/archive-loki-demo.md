# TASK ARCHIVE: Loki demo push script

## METADATA
- Complexity: Level 2 (Simple Enhancement)
- Files: `loki_push.py`, `README.md`, `requirements.txt`
- Archive path: `memory-bank/archive/archive-loki-demo.md`

## SUMMARY
Python 3.13 CLI (`loki_push.py`) для отправки тестовых логов в Grafana Cloud Loki через Basic Auth, с загрузкой настроек из `.env`, поддержкой лейблов, verbose/dry-run, опцией отключения TLS и обязательным `requests`/`python-dotenv`.

## REQUIREMENTS
- Пушить тестовые события напрямую в Grafana Cloud Loki.
- Поддержать конфиг из `.env`, CLI аргументы, Basic Auth.
- Предоставить шаблон запуска и зависимости.

## IMPLEMENTATION
- `loki_push.py`: загрузка `.env` (override=True), нормализация значений (strip/кавычки/export), формирование payload Loki (наносекундные метки), отправка через requests, диагностика в verbose (превью creds, предупреждения о пробелах/кавычках), флаги `--verbose`, `--dry-run`, `--insecure`, лейблы по умолчанию `app=demo`, `host=<hostname>` + override через ENV/CLI.
- `README.md`: детальный quick start, пример `.env`, инструкция установки `requirements.txt`.
- `requirements.txt`: `requests`, `python-dotenv`.

## TESTING
- E2E с реальными Loki кредами из `.env`: HTTP 204 (успешно). verbose подтвердил корректный endpoint/username/token и отправку payload.

## LESSONS LEARNED
- Использовать единый HTTP клиент (requests) для упрощения.
- Делать `dotenv` обязательным и очищать значения (strip/кавычки/export) снижает риск 401.
- Диагностическое превью в verbose ускоряет поиск ошибок аутентификации.

## REFERENCES
- Reflection: `memory-bank/reflection/reflection-loki-demo.md`
- Tasks: `memory-bank/tasks.md` (archived)
- Progress: `memory-bank/progress.md`

