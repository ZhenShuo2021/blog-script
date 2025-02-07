import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_date() -> str:
    return datetime.now().strftime("%Y%m%d")


def generate_hash(data: Any) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def read_file(filepath: Path) -> Any | None:
    if filepath.exists():
        with filepath.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None


def write_file(data: Any, filepath: Path) -> None:
    with filepath.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_data(url: str, timeout: int = 10) -> Any:
    response = requests.get(url, timeout=timeout)
    response.encoding = "utf-8"
    return response.json()
