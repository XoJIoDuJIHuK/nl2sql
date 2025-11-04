# NL2SQL

Диссертация на тему "Естественноязыковый интерфейс для генерации запросов к базе данных по доступным техническим методам использования производственных отходов"

## Порядок запуска

1. Установить [`uv`](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2)
2. В корне проекта выполнить `uv sync`: это установит нужную версию Python и зависимости проекта
3. Создать базу данных PostgreSQL и заполнить её скриптом `script.sql`
4. Создать файл `.env` с нужными значениями
5. Запустить при помощи `uv run main.py`

## TODO:

- Add support for RPC calls via tools
- Enrich system prompt with domain-specific information
