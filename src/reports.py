import datetime
import json
from collections.abc import Callable
from functools import wraps
from typing import Any, Optional

import pandas as pd

from src.count_data import count_data_from_csv


def log(filename: str | None = None) -> Callable[..., Any]:
    """Декоратор, который автоматически логирует начало и конец выполнения функции, а также ее результаты или возникшие ошибки."""

    def my_decorator(function: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(function)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            name = function.__name__
            try:
                res = function(*args, **kwargs)
                actual_filename = filename or f"{function.__name__}_default.json"
                log_message = f"{name} ok"
                with open(actual_filename, "w", encoding="utf-8") as file:
                    file.write(str(res))
                return res
            except Exception as e:
                error = e.__class__.__name__
                log_message = f"{name} error: {error}. Inputs: {args}, {kwargs}"
                if filename:
                    with open(filename, "a", encoding="utf-8") as file:
                        file.write(log_message + "\n")
                else:
                    print(log_message)
                raise e

        return wrapped

    return my_decorator


path = "data/operations.xlsx - Отчет по операциям.csv"
list_transactions = count_data_from_csv(path)
df_trans = pd.DataFrame(list_transactions)


@log
def expenditure_by_category(
    df_transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Функция, которая возвращает траты по заданной категории за последние три месяца (от переданной даты)"""
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
    except KeyError:
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
