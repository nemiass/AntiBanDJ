from configs.config import ROOT_PATH
import json
import requests
import re


# FUNCIONES DE AYUDA


def read_prefixes() -> dict[str, dict]:
    with open(f"{ROOT_PATH}/configs/prefixes.json") as f:
        return json.load(f)


def save_prefixes(prefixes: dict[str, dict]) -> None:
    with open(f"{ROOT_PATH}/configs/prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)


def url_by_name(song_target: tuple[str]) -> str:
    target_url = "https://www.youtube.com/results"
    search = "+".join(song_target)
    params = {"search_query": search}
    response = requests.get(target_url, params=params)
    reg = r"watch\?v=(\S{11})"
    urls = re.findall(reg, response.text)
    return f"https://www.youtube.com/watch?v={urls[0]}"


def is_url(song_target: tuple[str]) -> bool:
    return len(song_target) == 1 and song_target[0].startswith("https://")
