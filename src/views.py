import datetime
import json
import logging
import os
import time
from json import JSONDecodeError
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

from src.count_data import count_data_from_csv
from src.get_project_roof import get_roof

project_root = get_roof()
loger_path = project_root / "data" / "views.log"

logger = logging.getLogger("views")
file_handler = logging.FileHandler(loger_path, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(level="INFO")

load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_ALPHA = os.getenv("API_KEY_ALPHA_ADVANTAGE")
file_path = project_root / "data/operations.xlsx - Отчет по операциям.csv"
global_transactions = count_data_from_csv(file_path)


def define_part_of_day(date: str) -> tuple:
    """Функция, определяющая текущую часть дня"""
    end_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    hour = end_date.hour
    logger.info("Определяем текущую часть дня")
    if 0 <= hour < 6 or hour == 23:
        greeting = "Доброй ночи"
    elif 6 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    else:
        greeting = "Добрый вечер"
    logger.info(f"Текущая часть дня {greeting}")
    return greeting, end_date


def get_cards_information(
    end_date: datetime, transactions_df: pd.DataFrame | None = None
) -> tuple:
    """Функция, которая возвращает список карт с их номером, суммой трат и cashback"""
    logger.info("Получаем DataFrame для обработки")
    if transactions_df is None:
        transactions_df = pd.DataFrame(global_transactions)

    logger.info("Определяем диапазон дат")
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0)
    cards_list = []

    try:
        logger.info("Преобразуем даты в объект datetime")
        transactions_df["Дата операции"] = pd.to_datetime(
            transactions_df["Дата операции"], dayfirst=True
        )

        logger.info("Фильтруем операции по диапазону")
        filtered_transactions = transactions_df[
            transactions_df["Дата операции"].between(start_date, end_date)
        ]
        expenses_df = filtered_transactions[
            filtered_transactions["Сумма операции"] < 0
        ].copy()

        expenses_uniq_df = (
            expenses_df.groupby("Номер карты")["Сумма операции"].sum().reset_index()
        )
        logger.info("Собираем данные о каждой карте")
        for _, row in expenses_uniq_df.iterrows():
            card = str(row["Номер карты"])
            total_spent = round(abs(row["Сумма операции"]), 2)
            cashback = round(total_spent / 100, 2)
            card_summary = {
                "last_digits": card,
                "total_spent": total_spent,
                "cashback": cashback,
            }
            cards_list.append(card_summary)
        return cards_list, filtered_transactions
    except KeyError as error:
        logger.error(f"Произошла ошибка {error} при обработке DataFrame")
        print(f"Произошла ошибка {error} при обработке DataFrame")
        raise error


def get_top_5_transactions_total_spent(filtered_df: pd.DataFrame) -> list[dict]:
    """Функция, возвращающая топ-5 транзакций по сумме платежа."""
    top_transactions = []
    try:
        df_copy = filtered_df.copy()
        df_copy["Сумма операции по модулю"] = df_copy["Сумма операции"].abs()
        top_5_df = df_copy.sort_values(
            by="Сумма операции по модулю", ascending=False
        ).head(5)
        logger.info("Собираем данные о 5 наибольших по модуля операциях")
        for _, row in top_5_df.iterrows():
            trans = {
                "date": str(row["Дата операции"].strftime("%d.%m.%Y")),
                "amount": round(row["Сумма операции"], 2),
                "category": str(row["Категория"]),
                "description": str(row["Описание"]),
            }
            top_transactions.append(trans)
        return top_transactions
    except KeyError as error:
        logger.error(f"Произошла ошибка {error} при обработке DataFrame")
        print(f"Произошла ошибка {error} при обработке DataFrame")
        raise error


def get_user_settings() -> dict[str, list]:
    "Функция, считывающая настройки пользователя" ""
    try:
        file_settings_path = project_root / "users_settings.json"
        with open(file_settings_path, "r") as file:
            user_settings = json.load(file)
            return user_settings
    except (FileNotFoundError, JSONDecodeError) as error:
        logger.error(
            f"Произошла ошибка {error} при обработке файла users_settings.json"
        )
        print(f"Произошла ошибка {error} при обработке файла users_settings.json")
        raise error


def get_currency_rates(user_settings: dict[str, list]):
    """Функция, возвращающая актуальный курс валют пользователя"""
    currency_rates = []

    logger.info("Получаем необходимые курсы валют")
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/RUB"
    try:
        response = requests.get(url)
        response = response.json()
        currencies = response["conversion_rates"]
    except requests.RequestException as error:
        logger.error(f"Произошла ошибка {error}")
        print(f"Произошла ошибка {error}")
        raise error

    logger.info("Собираем данные о курсе валют")
    for currency in user_settings["user_currencies"]:
        currency_val = {
            "currency": currency,
            "rate": round(1 / currencies[currency], 2),
        }
        currency_rates.append(currency_val)
    return currency_rates


def get_stock_prices(user_settings: dict[str, list]) -> list[dict]:
    """Функция возвращает актуальный курс акций, заданных пользователем"""
    stock_prices = []
    logger.info("Создаём mock список для цен акций")
    stocks_mock = {
        "AAPL": 150.12,
        "AMZN": 3173.18,
        "GOOGL": 2742.39,
        "MSFT": 296.71,
        "TSLA": 1007.08,
    }
    try:
        for stock in user_settings["user_stocks"]:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={API_KEY_ALPHA}"
            try:
                response = requests.get(url, timeout=5)
                response = response.json()
                global_quote = response.get("Global Quote", {})
                if "05. price" in global_quote:
                    price = float(global_quote["05. price"])
                else:
                    price = stocks_mock.get(stock, 0.0)
            except (requests.RequestException, ValueError, KeyError):
                price = stocks_mock.get(stock, 0.0)
            stock_price = {"stock": stock, "price": price}
            stock_prices.append(stock_price)

            time.sleep(1.5)
        return stock_prices
    except requests.RequestException as error:
        logger.error(f"Произошла ошибка {error}")
        print(f"Произошла ошибка {error}")
        raise error


def get_result(
    greeting, cards_list, top_5_transactions, currency_rates, stock_prices
) -> str:
    """Функция собирает итоговый результат"""
    logger.info("Собираем результат")
    result = {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_5_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
    json_res = json.dumps(result, ensure_ascii=False, indent=4)
    return json_res


def main(dates: str, transactions: pd.DataFrame | None = None) -> str:
    greeting, end_date = define_part_of_day(dates)
    cards_list, filtered_transactions = get_cards_information(end_date, transactions)
    top_5_transactions = get_top_5_transactions_total_spent(filtered_transactions)
    user_settings = get_user_settings()
    currency_rates = get_currency_rates(user_settings)
    stock_prices = get_stock_prices(user_settings)
    result = get_result(
        greeting, cards_list, top_5_transactions, currency_rates, stock_prices
    )
    return result


if __name__ == "__main__":
    res = main("2021-12-12 15:00:00")
