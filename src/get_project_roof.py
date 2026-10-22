import pathlib


def get_roof():
    loger_script = pathlib.Path(__file__).resolve()
    project_root = next(p for p in loger_script.parents if p.name == "Bank_app_curs")
    return project_root
