"""In-process event bus."""
import asyncio
from collections import defaultdict
from typing import Any, Callable

_subscribers: dict[str, list[Callable[[dict[str, Any]], Any]]] = defaultdict(list)


def subscribe(topic: str, handler: Callable[[dict[str, Any]], Any]) -> None:
    _subscribers[topic].append(handler)


def publish(topic: str, message: dict[str, Any]) -> None:
    for handler in _subscribers[topic]:
        result = handler(message)
        if asyncio.iscoroutine(result):
            asyncio.get_event_loop().run_until_complete(result)
