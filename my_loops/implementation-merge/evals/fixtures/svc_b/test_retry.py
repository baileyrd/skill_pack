import unittest
from unittest import mock

from retry import RetryAfter, retry


class RetryTest(unittest.TestCase):
    @mock.patch("time.sleep")
    def test_retry_after_is_honoured(self, sleep: mock.Mock) -> None:
        results = iter([RetryAfter(7.0), "ok"])
        def fn() -> str:
            r = next(results)
            if isinstance(r, Exception):
                raise r
            return r
        self.assertEqual(retry(fn), "ok")
        sleep.assert_called_once_with(7.0)

    @mock.patch("time.sleep")
    def test_on_retry_reports_attempts(self, _sleep: mock.Mock) -> None:
        seen = []
        def boom() -> None:
            raise ConnectionError("down")
        self.assertIsNone(retry(boom, attempts=3, on_retry=lambda n, e: seen.append(n)))
        self.assertEqual(seen, [1, 2, 3])


if __name__ == "__main__":
    unittest.main()
