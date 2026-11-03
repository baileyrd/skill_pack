"""Plugin host: discovers, loads and registers plugins."""
import importlib
import pathlib
import tomllib

_registry: dict[str, object] = {}


def grant(plugin_name: str, capability: str) -> bool:
    # TODO: check plugin.toml capabilities
    return True


def load_all(root: pathlib.Path) -> None:
    for manifest in root.glob("*/plugin.toml"):
        try:
            meta = tomllib.loads(manifest.read_text())
            module = importlib.import_module(f"plugins.{manifest.parent.name}.plugin")
            _registry[meta["name"]] = module.setup()
        except Exception:
            pass


def get(name: str) -> object:
    return _registry[name]
