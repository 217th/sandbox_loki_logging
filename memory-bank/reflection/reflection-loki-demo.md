# Reflection — Loki demo push script

## Summary
- Level 2 enhancement: Python CLI to push test events to Grafana Cloud Loki.
- Implemented `loki_push.py` with required `requests` and `python-dotenv`; docs in `README.md`.

## What went well
- Простая CLI-обвязка: аргументы + ENV с приоритетом CLI.
- Чёткое формирование payload Loki (наносекундные метки, понятные сообщения с idx + ISO-время).
- Подробные русские комментарии для удобства чтения и сопровождения.

## Challenges
- Отказались от fallback на stdlib/urllib, чтобы упростить код — потребовалось обновить план и README.
- Проблемы аутентификации из-за оставшихся в окружении старых/неочищенных значений и возможных пробелов/кавычек в .env; потребовались override=True и доп. диагностика в verbose.

## Lessons learned
- Лучше сразу выбирать единственный HTTP клиент (requests) ради простоты и читаемости.
- Делать `dotenv` обязательным упрощает загрузку настроек и избавляет от самописного парсера.
- Для Loki полезно нормализовывать креды (strip/кавычки/пробелы) и показывать превью в verbose, чтобы быстрее находить ошибки 401.

## Next steps
- При желании: задействовать `--interval` как реальную задержку между событиями (сейчас отправка одним батчем).

