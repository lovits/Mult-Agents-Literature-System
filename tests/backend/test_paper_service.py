from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from app.repositories.sqlite_run_repository import SQLiteRunRepository


class PaperServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        from app.services.paper_service import PaperService

        self.temp_dir = tempfile.TemporaryDirectory()
        self.repository = SQLiteRunRepository(Path(self.temp_dir.name) / "backend.sqlite3")
        self.repository.initialize()
        self.service = PaperService(self.repository)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_import_persists_ordered_sections_and_deterministic_blocks(self) -> None:
        markdown = "# Abstract\nShort claim.\n\n# Experiments\nWe compare three retrieval baselines."

        first = self.service.import_markdown("paper-1", "Agent RAG", markdown)
        first_blocks = self.service.get_evidence_blocks("paper-1")
        second = self.service.import_markdown("paper-1", "Agent RAG", markdown)
        second_blocks = self.service.get_evidence_blocks("paper-1")

        self.assertEqual(first["section_count"], 2)
        self.assertEqual(first["evidence_block_count"], 2)
        self.assertEqual(second["paper_id"], "paper-1")
        self.assertEqual([item["section_type"] for item in self.service.get_sections("paper-1")], ["abstract", "experiment"])
        self.assertEqual([item["block_id"] for item in first_blocks], [item["block_id"] for item in second_blocks])
        self.assertEqual(first_blocks[0]["text"], "Short claim.")

    def test_reimport_replaces_derived_assets_atomically(self) -> None:
        self.service.import_markdown("paper-1", "Old", "# Abstract\nOld text.")

        imported = self.service.import_markdown("paper-1", "New", "# Method\nNew method text.")

        self.assertEqual(imported["title"], "New")
        self.assertEqual(len(self.service.get_sections("paper-1")), 1)
        self.assertEqual(self.service.get_sections("paper-1")[0]["section_type"], "method")
        self.assertNotIn("Old text", str(self.service.get_evidence_blocks("paper-1")))

    def test_missing_paper_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            self.service.get_paper("missing")


if __name__ == "__main__":
    unittest.main()
