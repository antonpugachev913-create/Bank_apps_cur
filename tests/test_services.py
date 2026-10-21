import pytest
from src.services import simple_search


def test_simple_search(transactions_data) -> None:
    assert simple_search("Пополнения", transactions_data) == [
        {
            "Дата операции": "30.12.2021 17:50:30",
            "Дата платежа": "30.12.2021",
            "Номер карты": "*4556",
            "Статус": "OK",
            "Сумма операции": 5046.0,
            "Валюта операции": "RUB",
            "Сумма платежа": 5046.0,
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Пополнения",
            "MCC": "",
            "Описание": "Пополнение через Газпромбанк",
            "Бонусы (включая кэшбэк)": 0.0,
            "Округление на инвесткопилку": 0.0,
            "Сумма операции с округлением": 5046.0,
        }
    ]
    assert simple_search("Пополнения", []) == []


def test_simple_search_error(bad_transactions_data) -> None:
    with pytest.raises(KeyError):
        simple_search("Пополнения", bad_transactions_data)
