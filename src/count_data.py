import pathlib
import pandas as pd
def count_data_from_csv(way: str | None) -> str:
    file_path = pathlib.Path(__file__).parent.parent / way
    data = pd.read_csv(file_path)
    return data.to_json(orient='records')

path = 'data/operations.xlsx - Отчет по операциям.csv'
res = count_data_from_csv(path)
print(res)