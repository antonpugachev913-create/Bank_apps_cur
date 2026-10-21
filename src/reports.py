import json

import pandas as pd
import datetime
from src.count_data import count_data_from_csv
from typing import Optional

"""
БИЗНЕС-ЛОГИКА ФУНКЦИИ (ТЗ):
Функция фильтрует транзакции по заданной категории и рассчитывает сумму трат 
за последние 3 месяца от указанной даты (включительно).

Входные параметры:
- df (pd.DataFrame): Датафрейм с транзакциями.
- category (str): Название категории для фильтрации.
- target_date (str | datetime, optional): Опциональная опорная дата. 
  Если не передана, используется текущая дата.

Выходные параметры:
- JSON-строка (или dict) с суммой трат и детальной информацией.

СТЕК ДЛЯ МОДУЛЯ:
- pandas (работа с датафреймом и фильтрация по датам)
- datetime (расчет временного интервала в 3 месяца)
- json (форматирование итогового ответа)
- logging (логирование процесса расчета)
- pytest (тестирование краевых случаев и фильтрации)
"""

path = "data/operations.xlsx - Отчет по операциям.csv"
list_transactions = count_data_from_csv(path)
df_trans = pd.DataFrame(list_transactions)


def expenditure_by_category(
    df_transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    try:
        filtered_df = df_transactions[
            df_transactions["Категория"].str.lower() == category.lower()
        ].copy()
        if date:
            end_date = datetime.datetime.strptime(date, "%d.%m.%Y %H:%M:%S")
        else:
            end_date = datetime.datetime.today()
        start_date = end_date - pd.DateOffset(months=3)
        filtered_df["Дата операции"] = pd.to_datetime(
            filtered_df["Дата операции"], dayfirst=True
        )
        end_df = filtered_df[filtered_df["Дата операции"].between(start_date, end_date)]
        total_expenses = abs(end_df["Сумма операции"].sum())
        operations_count = len(end_df)
        if operations_count > 0:
            average_check = abs(end_df["Сумма операции"].mean())
        else:
            average_check = 0.0
        result_dict = {
            "category": category,
            "total_expenses": total_expenses,
            "detailed_info": {
                "operations_count": operations_count,
                "average_check": average_check,
                "period_days": 90,
            },
        }
        res = json.dumps(result_dict, ensure_ascii=False, indent=4)
        # print(res)
        return res
    except KeyError as k:
        raise KeyError


# expenditure_by_category(df_trans, "Супермаркеты", "31.12.2021 16:44:00")
# data = [
#     {
#         "Дата операции": "31.12.2021 16:44:00",
#         "Категория": "Супермаркеты",
#         "Сумма операции": -160.89,
#     },
#     {
#         "Дата операции": "30.12.2021 12:00:00",
#         "Категория": "Каршеринг",
#         "Сумма операции": -500.00,
#     },
#     {
#         "Дата операции": "01.05.2021 10:00:00",
#         "Категория": "Супермаркеты",
#         "Сумма операции": -1000.00,
#     },
# ]
# expenditure_by_category(pd.DataFrame(data), "Супермаркеты", "31.12.2021 16:44:00")
