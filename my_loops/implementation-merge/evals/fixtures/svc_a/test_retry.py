import unittest
from unittest import mock

from retry import RetryError, backoff_delays, retry


class RetryTest(unittest.TestCase):
    def test_delays_capped(self) -> None:
        self.assertTrue(all(d <= 1.0 for d in backoff_delays(0.5, 1.0, 6)))

    @mock.patch("time.sleep")
    def test_gives_up(self, _sleep: mock.Mock) -> None:
        def boom() -> None:
            raise ConnectionError("down")
        with self.assertRaises(RetryError):
            retry(boom, attempts=3)

    @mock.patch("time.sleep")
    def test_does_not_retry_value_error(self, _sleep: mock.Mock) -> None:
        calls = []
        def bad() -> None:
            calls.append(1)
            raise ValueError("bad input")
        with self.assertRaises(ValueError):
            retry(bad)
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
