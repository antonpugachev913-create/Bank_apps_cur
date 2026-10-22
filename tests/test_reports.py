import json

import pandas as pd
import pytest

from src.reports import expenditure_by_category


def test_expenditure_by_category(mock_df_transactions) -> None:
    category = "Супермаркеты"
    data = "31.12.2021 16:44:00"
    res_dict = expenditure_by_category(mock_df_transactions, category, data)
    result = json.loads(res_dict)
    assert (result) == {
        "category": "Супермаркеты",
        "total_expenses": 160.89,
        "detailed_info": {
            "operations_count": 1,
            "average_check": 160.89,
            "period_days": 90,
        },
    }
    empty_df = pd.DataFrame(columns=["Дата операции", "Категория", "Сумма операции"])

    empty_res_json = expenditure_by_category(empty_df, category, data)
    empty_result = json.loads(empty_res_json)

    assert empty_result["total_expenses"] == 0.0
    assert empty_result["detailed_info"]["operations_count"] == 0


def test_expenditure_by_category_errors() -> None:
    broken_data_1 = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Тип операции": "Супермаркеты",
            "Сумма операции": -160.89,
        }
    ]
    with pytest.raises(KeyError):
        expenditure_by_category(
            pd.DataFrame(broken_data_1), "Супермаркеты", "31.12.2021 16:44:00"
        )
