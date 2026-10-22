import datetime
import json
import pandas as pd
import requests
import os
from src.count_data import count_data_from_csv
from src.get_project_roof import get_roof
from dotenv import load_dotenv

load_dotenv()

"""
Модуль для генерации JSON-ответа страницы «Главная».

Теги проекта: #json #requests #API #datetime #logging #pytest #pandas

ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ:
1. Принимает на вход:
   - df (pd.DataFrame): Данные транзакций из Excel-файла.
   - date_str (str): Строка даты и времени в формате 'YYYY-MM-DD HH:MM:SS'.

2. Фильтрация данных:
   - Анализируются транзакции с начала месяца входящей даты по саму входящую дату.
   - Пример: '2020-05-20 14:00:00' -> Диапазон: 01.05.2020 00:00:00 - 20.05.2020 14:00:00.

3. Пользовательские настройки (user_settings.json):
   - Список валют: 'user_currencies' (например, ["USD", "EUR"])
   - Список акций: 'user_stocks' (например, ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"])

ВЫХОДНЫЕ ДАННЫЕ (Структура JSON-ответа):
{
    "greeting": str,          # «Доброе утро» (06:00-11:59) / «Добрый день» (12:00-17:59) /
                              # «Добрый вечер» (18:00-23:59) / «Доброй ночи» (00:00-05:59).
    "cards": [                # Расчеты по каждой карте (только расходы):
        {
            "last_digits": str,   # Последние 4 цифры карты.
            "total_spent": float, # Общая сумма расходов.
            "cashback": float     # Кешбэк (1 рубль на каждые 100 рублей расходов).
        }
    ],
    "top_transactions": [     # Топ-5 транзакций, отсортированных по сумме платежа (по убыванию):
        {
            "date": str,          # Дата в формате 'DD.MM.YYYY' (из примера JSON).
            "amount": float,      # Сумма транзакции.
            "category": str,      # Категория операции.
            "description": str    # Описание операции.
        }
    ],
    "currency_rates": [       # Курсы валют из внешнего API относительно рубля:
        {
            "currency": str,      # Название валюты (USD, EUR и т.д.).
            "rate": float         # Стоимость 1 единицы валюты в рублях.
        }
    ],
    "stock_prices": [         # Стоимость акций из S&P500 из внешнего API:
        {
            "stock": str,         # Тикер акции (AAPL, TSLA и т.д.).
            "price": float        # Текущая цена акции.
        }
    ]
}
"""
API_KEY = os.getenv("API_KEY")
project_root = get_roof()
file_path = project_root / "data/operations.xlsx - Отчет по операциям.csv"
global_transactions = count_data_from_csv(file_path)


def main(dates: str, transactions: pd.DataFrame | None = None) -> str:
    end_date = datetime.datetime.strptime(dates, "%d-%m-%Y %H:%M:%S")
    hour = end_date.hour
    if 0 <= hour < 6:
        greeting = "Доброй ночи"
        print("Доброй ночи")
    elif 6 <= hour < 12:
        greeting = "Доброе утро"
        print("Доброе утро")
    elif 12 <= hour < 18:
        greeting = "Добрый день"
        print("Добрый день")
    else:
        print("Добрый вечер")
        greeting = "Добрый вечер"

    if transactions is None:
        transactions = pd.DataFrame(global_transactions)

    start_date = end_date.replace(day=1, hour=0, minute=0, second=0)
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], dayfirst=True
    )
    filtered_transactions = transactions[
        transactions["Дата операции"].between(start_date, end_date)
    ]
    # print(filtered_transactions)

    cards_list = []
    expenses_df = filtered_transactions[
        filtered_transactions["Сумма операции"] < 0
    ].copy()

    expenses_uniq_df = (
        expenses_df.groupby("Номер карты")["Сумма операции"].sum().reset_index()
    )
    for _, row in expenses_uniq_df.iterrows():
        card = str(row["Номер карты"])
        total_spent = round(abs(row["Сумма операции"]), 2)
        cash = round(total_spent / 100, 2)
        expenses_dict = {"last_digits": card, "total_spent": total_spent, "cash": cash}
        cards_list.append(expenses_dict)

    top_transactions = []
    filtered_transactions["Сумма операции по модулю"] = filtered_transactions[
        "Сумма операции"
    ].abs()
    top_5_df = filtered_transactions.nlargest(5, "Сумма операции по модулю")

    for _, row in top_5_df.iterrows():
        trans = {
            "date": str(row["Дата операции"].strftime("%d.%m.%Y")),
            "amount": round(row["Сумма операции"], 2),
            "category": str(row["Категория"]),
            "description": str(row["Описание"]),
        }
        top_transactions.append(trans)

    currency_rates = []
    file_settings_path = project_root / "users_settings.json"
    with open(file_settings_path, "r") as file:
        data = json.load(file)
    print(data)

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/RUB"
    response = requests.get(url)
    response = response.json()
    print(json.dumps(response, ensure_ascii=False, indent=4))

    # "currency_rates": [       # Курсы валют из внешнего API относительно рубля:
    #     {
    #         "currency": str,      # Название валюты (USD, EUR и т.д.).
    #         "rate": float         # Стоимость 1 единицы валюты в рублях.
    #     }

    # json_string = top_5_df.to_json(orient="records", force_ascii=False, indent=4, date_format='iso')
    # with open('viewsi.json', 'w', encoding='utf-8') as file:
    #     file.write(json_string)

    result = {
        "greeting": greeting,
        "cards": cards_list,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": [],
    }
    json_res = json.dumps(result)
    return json_res


main("20-05-2020 23:59:00")
