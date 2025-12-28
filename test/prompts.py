PROMPTS_TO_TEST = [
    # --- Category: Basic SQL / Entity Retrieval ---
    {
        "id": "SQL_01",
        "category": "Basic SQL",
        "text": "Выведи список всех производителей (producers) в кластере."
    },
    {
        "id": "SQL_02",
        "category": "Basic SQL",
        "text": "Покажи все записи из таблицы products."
    },

    # --- Category: Mathematical Definitions (Set Theory) ---
    {
        "id": "MATH_01",
        "category": "Set Definitions",
        "text": "Найди все продукты, которые принадлежат множеству R, но не принадлежат множеству R-черта (продукты только для внутреннего потребления)."
    },
    {
        "id": "MATH_02",
        "category": "Set Definitions",
        "text": "Выведи список промежуточных продуктов ПК (r_i, которые не входят в R-черта и участвуют в цепочках)."
    },

    # --- Category: Axiom Verification ---
    {
        "id": "AXIOM_01",
        "category": "Axiom Checks",
        "text": "Проверь Аксиому 1 для текущей модели (0 <= a_{i,i} < 1)."
    },
    {
        "id": "AXIOM_02",
        "category": "Axiom Checks",
        "text": "Проверь, выполняется ли аксиома о том, что для продуктов внутреннего потребления внешний спрос (y_i) равен 0."
    },

    # --- Category: Complex SQL / Joins ---
    {
        "id": "CPLX_01",
        "category": "Complex SQL",
        "text": "Покажи технологические цепочки: для каждого конечного продукта выведи список необходимых ресурсов и их количество."
    },

    # --- Category: API / Computational Tools ---
    # These require the LLM to call `make_graphql_request` or `call_local_http_server`
    # based on the definitions in the prompt for 'calcdet' and 'calcplan'.
    {
        "id": "API_01",
        "category": "API/Calc",
        "text": "Вычисли определитель матрицы затрат A (det(A))."
    },
    {
        "id": "API_02",
        "category": "API/Calc",
        "text": "Рассчитай плановый вектор X для текущих значений внешнего спроса Y."
    },

    # --- Category: Contradictions / Error Handling ---
    {
        "id": "ERR_01",
        "category": "Robustness",
        "text": "Проверь систему на противоречивость: есть ли в матрице A отрицательные значения?"
    },
    {
        "id": "ERR_02",
        "category": "Robustness",
        "text": "В базе данных есть производитель с именем 'NonExistentFactory'. Найди его продукты." 
        # (Should handle empty result gracefully)
    }
]
