import pathlib
import json
import pandas as pd


def count_data_from_csv(way: str | None) -> list[dict]:
    script_path = pathlib.Path(__file__).resolve()
    project_root = next(p for p in script_path.parents if p.name == "Bank_app_curs")
    file_path = project_root / way
    data = pd.read_csv(file_path, decimal=",")
    data = data.fillna("")
    return data.to_dict(orient="records")


path = "data/operations.xlsx - Отчет по операциям.csv"
res = count_data_from_csv(path)

beautiful_res = json.dumps(res, indent=4, ensure_ascii=False)
print(beautiful_res)

with open("count.json", "w", encoding="utf-8") as file:
    file.write(beautiful_res)
