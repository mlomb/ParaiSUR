from pathlib import Path
import json

CACHE_PATH = Path("../data-cache")


def get_cache(key: str):
    try:
        with open(CACHE_PATH / key) as f:
            return json.loads(f.read())
    except FileNotFoundError:
        return None


def set_cache(key: str, value):
    with open(CACHE_PATH / key, "w") as f:
        f.write(json.dumps(value))
