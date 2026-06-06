from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[2] / "code" / "experiments" / "evireview_a" / "src"
sys.path.insert(0, str(SRC_DIR))

from metric_adapter_registry import collect_historical_metrics


class MetricAdapterRegistryTest(unittest.TestCase):
    def test_collects_method_metrics_with_explicit_proxy_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "peerqa_xt_retrieval_metrics.json").write_text(
                json.dumps({"methods": {"bm25_question": {"answer_support_hit_at_3": 0.598}}}),
                encoding="utf-8",
            )

            records = collect_historical_metrics(root)

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].dataset, "PeerQA-XT")
        self.assertEqual(records[0].method, "bm25_question")
        self.assertEqual(records[0].metric, "answer_support_hit_at_3")
        self.assertEqual(records[0].metric_boundary, "proxy")

    def test_collects_provider_coverage_without_treating_threshold_as_metric_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "minimax_reviewer_coverage_metrics.json").write_text(
                json.dumps(
                    {
                        "generic_rate": 0.0667,
                        "coverage_by_threshold": [
                            {"threshold": 0.18, "evaluated_human_weakness_count": 151, "human_weakness_recall": 0.5232}
                        ],
                    }
                ),
                encoding="utf-8",
            )

            records = collect_historical_metrics(root)

        metrics = {item.metric: item.value for item in records}
        self.assertEqual(metrics["generic_rate"], 0.0667)
        self.assertEqual(metrics["human_weakness_recall_at_0.18"], 0.5232)
        self.assertNotIn("threshold", metrics)
        self.assertTrue(all(item.metric_boundary == "diagnostic" for item in records))


if __name__ == "__main__":
    unittest.main()
