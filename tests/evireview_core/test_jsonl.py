from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from evireview_core.io.jsonl import read_jsonl, write_jsonl


class JsonlTest(unittest.TestCase):
    def test_write_and_read_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            rows = [{"id": "a", "value": 1}, {"id": "b", "value": 2}]

            write_jsonl(path, rows)

            self.assertEqual(read_jsonl(path), rows)


if __name__ == "__main__":
    unittest.main()
