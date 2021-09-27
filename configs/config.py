from os import path, sep

DEFAULT_PREFIX = "?"
ROOT_PATH = path.dirname(path.abspath(__file__)).rsplit(sep, 1)[0]

with open(f'{ROOT_PATH}/token.txt', 'r', encoding="utf-8") as f:
    TOKEN = f.read()
