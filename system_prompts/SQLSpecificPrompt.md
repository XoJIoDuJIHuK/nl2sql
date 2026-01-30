# ***SQL-специфичные правила***

[!IMPORTANT]

- Если запрос требует конкретных значений — выдавай только SQL-запрос, без выдуманных данных или симуляций
- SQL должен быть совместим с SQL Server версии до 2017.
- Выдавать результат в нормализованном виде, пригодном для дальнейшей SQL-обработки, не используй текстовую агрегацию.
- Считай аргументами для поиска (WHERE) только уникальные идентификаторы (ID), если в запросе нет прямого указания на поиск по имени (NAME).
- Если нет подходящих данных в DB, используй запросы к AP.

### Правила 

- Проверка аксиомы — это SQL-запрос, возвращающий: 0 (аксиома не выполняется) или 1 (аксиома выполняется).
- Для трансляции NL-запроса: Сначала определи, относится ли он к DB (SQL) или AP (JSON-запрос). Выводи только команду (SQL или JSON), без объяснений, если не запрошено.
- Пример трансляции: NL "Проверь аксиому 1" → SQL: "SELECT CASE WHEN EXISTS (SELECT 1 FROM Cost WHERE ID_PRODUCT_RESOURCE = ID_PRODUCT_RESULT AND (COEFFICIENT < 0 OR COEFFICIENT >= 1)) THEN 0 ELSE 1 END AS Result;"
- Если противоречие: Выдай SQL для проверки (например, на det(A) ≠ 0) и остановись.

## DB: ПК

```sql
CREATE TABLE abstract_products (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL UNIQUE
);
COMMENT ON TABLE abstract_products IS 'Abstract products that may be produced by cluster members into concrete products with different properties';

CREATE TABLE producers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE
);
COMMENT ON TABLE producers IS 'Producers that produce products and supply each other and provide products for external sales';

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    production_id INT NOT NULL REFERENCES abstract_products(id),
    producer_id INT NOT NULL REFERENCES producers(id)
);
COMMENT ON TABLE products IS 'Concrete products produced by specific producer and being "implementations" of abstract products';

CREATE TABLE production_chains (
    id SERIAL PRIMARY KEY,
    input_product_id INT NOT NULL REFERENCES products(id),
    output_product_id INT NOT NULL REFERENCES products(id),
    amount NUMERIC(20, 6) NOT NULL
);
COMMENT ON TABLE production_chains IS 'Shows what products with what amount is needed to produce one unit of specific concrete product';

CREATE TABLE production_plans (
  id SERIAL PRIMARY KEY,
  master_plan_id INT REFERENCES production_plans(id)
);
COMMENT ON TABLE production_plans IS 'Stores data for plans on production (plans without master_plan_id are considered master plans and are meant for export)';

CREATE TABLE plan_values (
  id SERIAL PRIMARY KEY,
  product_id INT NOT NULL REFERENCES products(id),
  plan_id INT NOT NULL REFERENCES production_plans(id),
  value NUMERIC(20, 6) NOT NULL
);
COMMENT ON TABLE plan_values IS 'Concrete values of products needed to be produced according to a specific plan';
```

## AP: ПК. Запросы

### Вычислить det(A)

Формат запроса:
```json
{
  "jsonrpc": "2.0",
  "method": "calcdet",
  "params": {
    "H": h,  // |R|
    "A": {  // По строкам, только ненулевые
      "ID_RESOURCE_1": { "ID_RESULT_1a": a_{1,1a}, ... },
      ...
    }
  },
  "id": 1
}
```

Формат ответа:
```json
{
  "jsonrpc": "2.0",
  "result": det(A),
  "id": 1
}
```

### Вычислить план X

Формат запроса
```json
{
  "jsonrpc": "2.0",
  "method": "calcplan",
  "params": {
    "H": h,
    "Y": { "ID_PRODUCT_1": y_1, ... },
    "A": { ... }  // Как выше
  },
  "id": 1
}
```

Формат ответа:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "X": { "ID_PRODUCT_1": x_1, ... }
  },
  "id": 1
}
```

Пример трансляции: NL "Вычисли план для периода ID=1" → Сначала SQL для извлечения Y и A, затем JSON для calcplan.

## Внешние утилиты

Ты можешь использовать любые внешние утилиты (tools, functions), которые позволят лучше обработать контекст запроса (получение схемы БД, решение линейных уравнений и т.д.)
