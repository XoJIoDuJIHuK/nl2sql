# NL2SQL

Диссертация на тему "Естественноязыковый интерфейс для генерации запросов к базе данных по доступным техническим методам использования производственных отходов"

## Порядок запуска

1. Установить [`uv`](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2)
2. В корне проекта выполнить `uv sync`: это установит нужную версию Python и зависимости проекта
3. Создать базу данных PostgreSQL и заполнить её скриптом `script.sql`
4. Создать файл `.env` с нужными значениями
5. Запустить при помощи `uv run main.py`

## TODO:

- Enrich system prompt with domain-specific information
- Make system prompt as formal as possible
- Collaborative work of 2+ people
- Later numerous constraints on production will be added
- The end task is to create a system that will solve task with those constraints
- Add roles so when one's constraints change, others are notified
- Make LLM a coordinator that makes all plans sum up
- Create architectural diagram

- Products may be produced in advance and stored in storage for later

- Каждый участник может задавать свой план в виде функции желательности (треугольной, игрек от 0 до 1, есть L, T и U)
- **Нужно найти, какая вообще функция будет для иксов** (X-AX=Y, X - это (вроде) план по каждому продукту для каждого производителя)
- Для каждого продукта, выходящего за пределы кластера, задаётся своя функция желательности
- Нужно свести задачу к тому, может ли наш участник кластера выполнить план в данных пределах или нет
- В феврале будут взрослые конференции, на неё сформилируем доклад по этой "нечёткой" теме

- OData. Сделать модель, скормить Имитатору Интеллекта, посмотреть на результаты. Вставим в диссертацию как разные методы
- Отличия вероятности от нечёткости - при нечёткости нет бинарности (20% того, что вода чистая, значит, что вода на 20% чистая и на 80% отравленная), а в случае вероятности строго 20% бутылок будут чистыми, а 80% отравленными
