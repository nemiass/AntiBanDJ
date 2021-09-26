from configs.config import ROOT_PATH
import json

# FUNCIONES DE AYUDA


def read_prefixes() -> dict[str, dict]:
    with open(f"{ROOT_PATH}/configs/prefixes.json") as f:
        return json.load(f)


def save_prefixes(prefixes: dict[str, dict]) -> None:
    with open(f"{ROOT_PATH}/configs/prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)
