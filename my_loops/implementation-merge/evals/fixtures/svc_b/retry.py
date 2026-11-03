"""Retry helper (from svc_b). Honours Retry-After and reports attempts."""
import time
from typing import Callable, Optional, TypeVar

T = TypeVar("T")


class RetryAfter(Exception):
    """Raise from fn to ask for a specific wait, e.g. from an HTTP 429 Retry-After header."""

    def __init__(self, seconds: float) -> None:
        super().__init__(f"retry after {seconds}s")
        self.seconds = seconds


def retry(fn: Callable[[], T], attempts: int = 4, delay: float = 0.2,
          on_retry: Optional[Callable[[int, BaseException], None]] = None) -> Optional[T]:
    """Call fn until it succeeds; return None if every attempt failed."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except RetryAfter as exc:
            wait = exc.seconds
            err: BaseException = exc
        except Exception as exc:  # retries everything
            wait = delay * 2 ** (attempt - 1)
            err = exc
        if on_retry is not None:
            on_retry(attempt, err)
        if attempt < attempts:
            time.sleep(wait)
    return None
