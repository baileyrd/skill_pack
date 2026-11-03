"""A tiny file-backed key-value store."""
import json
import pathlib


class Store:
    def __init__(self, path: pathlib.Path) -> None:
        self.path = path
        self.data: dict[str, str] = json.loads(path.read_text()) if path.exists() else {}

    def get(self, key: str) -> str:
        return self.data[key]

    def set(self, key: str, value: str) -> None:
        self.data[key] = value
        self.path.write_text(json.dumps(self.data))

    def delete(self, key: str) -> None:
        del self.data[key]
