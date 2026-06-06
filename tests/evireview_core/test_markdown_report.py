from __future__ import annotations

import unittest


class MarkdownReportTest(unittest.TestCase):
    def test_renders_public_audit_summary_without_internal_error(self) -> None:
        from evireview_core.reporting.markdown_report import render_review_audit_markdown

        markdown = render_review_audit_markdown(
            {
                "run_id": "run-1",
                "paper_id": "paper-1",
                "status": "succeeded",
                "error": "sensitive provider error",
                "result": {
                    "metric_boundary": "silver diagnostic",
                    "weakness_count": 1,
                    "evidence_block_count": 2,
                    "ranked_findings": [
                        {
                            "rank": 1,
                            "weakness_id": "w-1",
                            "label": "Partially Supported",
                            "rank_score": 0.73,
                        }
                    ],
                    "verification": {
                        "w-1": {
                            "support_score": 0.61,
                            "evidence_block_ids": ["block-1"],
                            "rationale": "Evidence partially addresses the concern.",
                        }
                    },
                },
            },
            [
                {"event_type": "queued"},
                {"event_type": "running"},
                {"event_type": "succeeded"},
            ],
        )

        self.assertIn("# Review Audit Report: paper-1", markdown)
        self.assertIn("silver diagnostic", markdown)
        self.assertIn("w-1", markdown)
        self.assertIn("Partially Supported", markdown)
        self.assertIn("block-1", markdown)
        self.assertIn("queued -> running -> succeeded", markdown)
        self.assertNotIn("sensitive provider error", markdown)


if __name__ == "__main__":
    unittest.main()
