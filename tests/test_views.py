import json
import pandas as pd
import pytest
import requests
from unittest.mock import patch, MagicMock
from src.views import main


@patch("requests.get")
def test_main(mock_response) -> None:
    mock_res = MagicMock()

    mock_res.json.return_value = {
        "conversion_rates": {"USD": 1 / 73.21, "EUR": 1 / 87.08}
    }

    mock_response.return_value = mock_res
    date = "2021-12-12 15:00:00"

    mock_transactions = pd.DataFrame(
        [
            {
                "Дата операции": "10.12.2021 00:00:00",
                "Номер карты": "5814",
                "Сумма операции": -1262.00,
                "Категория": "Переводы",
                "Описание": "Перевод Кредитная карта. ТП 10.2 RUR",
            },
            {
                "Дата операции": "05.12.2021 00:00:00",
                "Номер карты": "7512",
                "Сумма операции": -7.94,
                "Категория": "Супермаркеты",
                "Описание": "Лента",
            },
            {
                "Дата операции": "04.12.2021 00:00:00",
                "Номер карты": "5814",
                "Сумма операции": 421.00,
                "Категория": "Различные товары",
                "Описание": "Ozon.ru",
            },
            {
                "Дата операции": "03.12.2021 00:00:00",
                "Номер карты": "5814",
                "Сумма операции": 1198.23,
                "Категория": "ЖКХ",
                "Описание": "ЖКУ Квартира",
            },
            {
                "Дата операции": "02.12.2021 00:00:00",
                "Номер карты": "5814",
                "Сумма операции": 453.00,
                "Категория": "Бонусы",
                "Описание": "Кешбэк за обычные покупки",
            },
        ]
    )

    data = {
        "greeting": "Добрый день",
        "cards": [
            {"last_digits": "5814", "total_spent": 1262.00, "cashback": 12.62},
            {"last_digits": "7512", "total_spent": 7.94, "cashback": 0.08},
        ],
          "top_transactions": [
            {
                "date": "03.12.2021",
                "amount": 1198.23,
                "category": "ЖКХ",
                "description": "ЖКУ Квартира",
            },
            {
                "date": "02.12.2021",
                "amount": 453.00,
                "category": "Бонусы",
                "description": "Кешбэк за обычные покупки",
            },
            {
                "date": "04.12.2021",
                "amount": 421.00,
                "category": "Различные товары",
                "description": "Ozon.ru",
            },
            {
                "date": "05.12.2021",
                "amount": -7.94,
                "category": "Супермаркеты",
                "description": "Лента",
            },
            {
                "date": "10.12.2021",
                "amount": -1262.00,
                "category": "Переводы",
                "description": "Перевод Кредитная карта. ТП 10.2 RUR",
            },
        ],
        "currency_rates": [
            {"currency": "USD", "rate": 73.21},
            {"currency": "EUR", "rate": 87.08},
        ],
        "stock_prices": [
            {"stock": "AAPL", "price": 150.12},
            {"stock": "AMZN", "price": 3173.18},
            {"stock": "GOOGL", "price": 2742.39},
            {"stock": "MSFT", "price": 296.71},
            {"stock": "TSLA", "price": 1007.08},
        ],
    }
    res = json.loads(main(date, transactions=mock_transactions))

    assert res["greeting"] == data["greeting"]

    assert len(res["cards"]) == len(data["cards"])
    for card in data["cards"]:
        assert card in res["cards"]

    assert len(res["top_transactions"]) == len(data["top_transactions"])
    assert res["top_transactions"] == data["top_transactions"]

    assert len(res["currency_rates"]) == len(data["currency_rates"])
    for rate in data["currency_rates"]:
        assert rate in res["currency_rates"]

    assert len(res["stock_prices"]) == len(data["stock_prices"])
    for stock in data["stock_prices"]:
        assert stock in res["stock_prices"]


@patch("requests.get")
def test_main_empty_df(mock_response) -> None:
    mock_res = MagicMock()

    mock_res.json.return_value = {
        "conversion_rates": {"USD": 1 / 73.21, "EUR": 1 / 87.08}
    }

    mock_response.return_value = mock_res
    date = "2021-12-12 15:00:00"

    mock_transactions = pd.DataFrame(
        {
            "Дата операции": pd.Series(dtype="datetime64[ns]"),
            "Номер карты": pd.Series(dtype="str"),
            "Сумма операции": pd.Series(dtype="float"),
            "Категория": pd.Series(dtype="str"),
            "Описание": pd.Series(dtype="str"),
        }
    )

    res = json.loads(main(date, transactions=mock_transactions))

    assert res["greeting"] == "Добрый день"

    assert res["cards"] == []

    assert res["top_transactions"] == []

    assert len(res["currency_rates"]) == 2


@patch("requests.get")
def test_main_api_error(mock_response) -> None:
    mock_response.side_effect = requests.RequestException
    date = "2021-12-12 15:00:00"

    with pytest.raises(requests.RequestException):
        main(date)
