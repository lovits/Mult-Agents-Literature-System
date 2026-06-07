from __future__ import annotations

import unittest

from evireview_core.classification.auxiliary import classify_auxiliary_decision
from evireview_core.domain.models import VerificationResult, Weakness


class AuxiliaryDecisionClassifierTest(unittest.TestCase):
    def test_supported_major_finding_produces_reject_tendency_with_diagnostic_boundary(self) -> None:
        weakness = Weakness("w1", "p1", "The evaluation lacks critical baselines.", "experiment", "major")
        verification = {
            "w1": VerificationResult("w1", "Supported", 0.9, ("b1",), "Evidence supports the issue.", "test")
        }

        signal = classify_auxiliary_decision([weakness], verification)

        self.assertEqual(signal.label, "Reject")
        self.assertGreaterEqual(signal.reject_score, 0.5)
        self.assertEqual(signal.metric_boundary, "auxiliary diagnostic")
        self.assertTrue(signal.not_for_decision)

    def test_unsupported_finding_does_not_create_reject_tendency(self) -> None:
        weakness = Weakness("w1", "p1", "The evaluation lacks critical baselines.", "experiment", "major")
        verification = {
            "w1": VerificationResult("w1", "Unsupported", 0.1, (), "No evidence.", "test")
        }

        signal = classify_auxiliary_decision([weakness], verification)

        self.assertEqual(signal.label, "Accept")
        self.assertLess(signal.reject_score, 0.5)


if __name__ == "__main__":
    unittest.main()
