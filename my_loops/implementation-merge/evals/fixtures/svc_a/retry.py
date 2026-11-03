"""Retry with exponential backoff (from svc_a)."""
import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryError(Exception):
    """Raised when every attempt failed; wraps the last error."""


def backoff_delays(base: float, cap: float, attempts: int) -> list[float]:
    """Full-jitter delays: uniform in [0, min(cap, base * 2**n)]."""
    return [random.uniform(0, min(cap, base * 2**n)) for n in range(attempts - 1)]


def retry(fn: Callable[[], T], attempts: int = 5, base: float = 0.1, cap: float = 5.0,
          retry_on: tuple[type[BaseException], ...] = (ConnectionError, TimeoutError)) -> T:
    last: BaseException | None = None
    for delay in [0.0, *backoff_delays(base, cap, attempts)]:
        time.sleep(delay)
        try:
            return fn()
        except retry_on as exc:
            last = exc
    raise RetryError(f"gave up after {attempts} attempts") from last
