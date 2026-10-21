import re
import json

"""
БИЗНЕС-ЛОГИКА ФУНКЦИИ (ТЗ):
Пользователь передает строку для поиска. 
Функция возвращает JSON-ответ со всеми транзакциями, 
которые содержат этот запрос в описании или категории.

СТЕК ДЛЯ МОДУЛЯ:
- json (форматирование ответа)
- logging (логирование процесса поиска)
- pytest (тестирование логики фильтрации)
"""
from src.count_data import count_data_from_csv

path = "data/operations.xlsx - Отчет по операциям.csv"
transactions = count_data_from_csv(path)


def simple_search(user_string: str) -> str:
    global transactions
    pattern = re.compile(user_string, re.IGNORECASE)
    filtered_transactions = []
    for transaction in transactions:
        description = transaction["Описание"]
        category = transaction["Категория"]
        if pattern.search(description) or pattern.search(category):
            filtered_transactions.append(transaction)
    filtered_transactions = json.dumps(
        filtered_transactions, ensure_ascii=False, indent=4
    )
    return filtered_transactions


# filtered_res = simple_search("Пополнения")
# print(filtered_res)
#
# with open("check.json", "w", encoding="utf-8") as file:
#     file.write(filtered_res)
