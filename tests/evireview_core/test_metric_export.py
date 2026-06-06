from __future__ import annotations

import json
import unittest

from evireview_core.evaluation.export import render_metrics_csv, render_metrics_markdown
from evireview_core.evaluation.metrics import MetricRecord, metric_records_json


class MetricExportTest(unittest.TestCase):
    def test_record_rejects_unknown_metric_boundary(self) -> None:
        with self.assertRaisesRegex(ValueError, "metric boundary"):
            MetricRecord("PeerQA-XT", "retrieval", "paper_rag", "bm25", "hit_at_3", 0.5, "unknown", "metrics.json")

    def test_exporters_preserve_boundary_and_source_with_stable_order(self) -> None:
        records = [
            MetricRecord("PeerQA-XT", "retrieval", "paper_rag", "section-aware", "hit_at_3", 0.606, "proxy", "peerqa.json"),
            MetricRecord("CLAIMCHECK", "ranker", "evidence_ranker", "bm25", "map", 0.7771, "diagnostic", "claimcheck.json"),
        ]

        payload = json.loads(metric_records_json(records))
        csv_text = render_metrics_csv(records)
        markdown = render_metrics_markdown(records)

        self.assertEqual(payload[0]["dataset"], "CLAIMCHECK")
        self.assertEqual(payload[1]["metric_boundary"], "proxy")
        self.assertIn("source_artifact", csv_text.splitlines()[0])
        self.assertIn("| CLAIMCHECK | ranker | evidence_ranker | bm25 | map | 0.7771 | diagnostic | claimcheck.json |", markdown)


if __name__ == "__main__":
    unittest.main()
