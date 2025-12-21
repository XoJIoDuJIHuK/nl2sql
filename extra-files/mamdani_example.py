import numpy as np


# Функция для треугольной функции принадлежности
def triangular_mf(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)


# Определение нечетких множеств
# Service: poor (0,0,5), average (0,5,10), good (5,10,10)
def service_poor(x):
    return triangular_mf(x, 0, 0, 5)


def service_average(x):
    return triangular_mf(x, 0, 5, 10)


def service_good(x):
    return triangular_mf(x, 5, 10, 10)


# Food: rancid (0,0,8), delicious (2,10,10)
def food_rancid(x):
    return triangular_mf(x, 0, 0, 8)


def food_delicious(x):
    return triangular_mf(x, 2, 10, 10)


# Tip: low (0,0,13), medium (0,13,25), high (13,25,25)
def tip_low(y):
    return triangular_mf(y, 0, 0, 13)


def tip_medium(y):
    return triangular_mf(y, 0, 13, 25)


def tip_high(y):
    return triangular_mf(y, 13, 25, 25)


def calculate_tip(service: float, food: float) -> float:
    # Шаг 2: Фаззификация
    mu_service_poor = service_poor(service)
    mu_service_average = service_average(service)
    mu_service_good = service_good(service)

    mu_food_rancid = food_rancid(food)
    mu_food_delicious = food_delicious(food)

    print(
        f"Service: poor={mu_service_poor:.2f}, average={mu_service_average:.2f}, good={mu_service_good:.2f}"
    )
    print(f"Food: rancid={mu_food_rancid:.2f}, delicious={mu_food_delicious:.2f}")

    # Шаг 3: Правила (используем min для AND)
    # Rule 1: IF service poor AND food rancid THEN tip low
    alpha1 = min(mu_service_poor, mu_food_rancid)

    # Rule 2: IF service average AND food delicious THEN tip medium
    alpha2 = min(mu_service_average, mu_food_delicious)

    # Rule 3: IF service good AND food delicious THEN tip high
    alpha3 = min(mu_service_good, mu_food_delicious)

    # Rule 4: IF service good AND food rancid THEN tip medium
    alpha4 = min(mu_service_good, mu_food_rancid)

    # Шаг 4: Агрегация - дискретизируем выход от 0 до 25
    y = np.linspace(0, 25, 1000)  # Для точности
    mu_tip = np.zeros_like(y)

    # Усечение и max для агрегации
    for i, val in enumerate(y):
        mu_low_clipped = min(tip_low(val), alpha1)
        mu_medium_clipped1 = min(tip_medium(val), alpha2)
        mu_medium_clipped2 = min(tip_medium(val), alpha4)
        mu_high_clipped = min(tip_high(val), alpha3)

        # Агрегация: max из всех clipped
        mu_tip[i] = max(
            mu_low_clipped, mu_medium_clipped1, mu_medium_clipped2, mu_high_clipped
        )

    # Шаг 5: Дефаззификация - центр тяжести
    if np.sum(mu_tip) > 0:
        tip_crisp = np.sum(y * mu_tip) / np.sum(mu_tip)
        print(f"Calculated tip: {tip_crisp:.2f}%")
        return tip_crisp
    else:
        print("No rules fired, tip: 0%")
        return 0.0
