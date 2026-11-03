"""Weather plugin: polls a forecast API and announces changes."""
import requests

from core import bus
from core.host import _registry


class Weather:
    def __init__(self) -> None:
        self.calendar = _registry.get("calendar")  # reach into another plugin directly

    def poll(self) -> None:
        data = requests.get("https://api.example.com/forecast").json()
        bus.publish("weather.changed", {"temp": data["temp"]})
        if self.calendar is not None:
            self.calendar.events.append({"title": "rain", "at": data["time"]})


def setup() -> Weather:
    return Weather()
