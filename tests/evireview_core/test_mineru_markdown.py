from __future__ import annotations

import unittest

from evireview_core.parsing.mineru_markdown import normalize_mineru_markdown


class MinerUMarkdownTest(unittest.TestCase):
    def test_removes_frontmatter_and_standalone_images_but_preserves_sections_and_tables(self) -> None:
        raw = """---
source: MinerU
pdf: paper.pdf
---

# Paper Title

![](images/figure.jpg)
Figure 1: Architecture overview.

# Experiments

<table><tr><td>Method</td><td>Score</td></tr></table>
"""

        normalized = normalize_mineru_markdown(raw)

        self.assertNotIn("source: MinerU", normalized)
        self.assertNotIn("images/figure.jpg", normalized)
        self.assertIn("# Experiments", normalized)
        self.assertIn("Figure 1: Architecture overview.", normalized)
        self.assertIn("<table>", normalized)


if __name__ == "__main__":
    unittest.main()
