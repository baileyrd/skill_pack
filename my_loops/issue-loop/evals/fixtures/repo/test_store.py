import pathlib
import tempfile
import unittest

from kvstore import Store


class StoreTest(unittest.TestCase):
    def test_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            s = Store(pathlib.Path(d) / "db.json")
            s.set("a", "1")
            self.assertEqual(Store(pathlib.Path(d) / "db.json").get("a"), "1")


if __name__ == "__main__":
    unittest.main()
