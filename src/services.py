import re
import json
import logging
import pathlib
from src.count_data import count_data_from_csv

loger_script = pathlib.Path(__file__).resolve()
project_root = next(p for p in loger_script.parents if p.name == 'Bank_app_curs')
loger_path = project_root / 'data' / 'simple_search.log'

logger = logging.getLogger('simple_search')
file_handler = logging.FileHandler(loger_path, encoding='utf-8')
file_formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
logger.setLevel(level='INFO')
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

path = "data/operations.xlsx - Отчет по операциям.csv"
transactions = count_data_from_csv(path)


def simple_search(user_string: str) -> str:
    global transactions
    logger.info('Начинаем фильтрацию операций')
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
    logger.info('Выводим готовый результат')
    return filtered_transactions


filtered_res = simple_search("Пополнения")
# print(filtered_res)

# with open("check.json", "w", encoding="utf-8") as file:
#     file.write(filtered_res)
