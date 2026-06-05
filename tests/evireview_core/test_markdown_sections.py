from __future__ import annotations

import unittest

from evireview_core.parsing.markdown_sections import chunk_text, classify_section, iter_sections, normalize_ws, tokenize


class MarkdownSectionsTest(unittest.TestCase):
    def test_iter_sections_preserves_nested_path(self) -> None:
        markdown = "# Method\nMain method text.\n## Ablation\nAblation details."

        sections = list(iter_sections(markdown))

        self.assertEqual(sections[0].section_path, "Method")
        self.assertEqual(sections[0].section_type, "method")
        self.assertEqual(sections[1].section_path, "Method > Ablation")
        self.assertEqual(sections[1].section_type, "experiment")

    def test_chunk_text_keeps_short_valid_block(self) -> None:
        text = " ".join(["ablation"] * 80)

        chunks = chunk_text(text, target_tokens=30, overlap_tokens=5, min_tokens=10)

        self.assertGreaterEqual(len(chunks), 3)
        self.assertTrue(all("ablation" in chunk for chunk in chunks))

    def test_normalize_and_tokenize(self) -> None:
        self.assertEqual(normalize_ws("A\n\n  B"), "A B")
        self.assertEqual(tokenize("Ablation-1 improves F1 by 3.5"), ["ablation-1", "improves", "f1", "by", "3.5"])

    def test_classify_section(self) -> None:
        self.assertEqual(classify_section("Experiments > Ablation"), "experiment")
        self.assertEqual(classify_section("Related Work"), "related_work")


if __name__ == "__main__":
    unittest.main()
