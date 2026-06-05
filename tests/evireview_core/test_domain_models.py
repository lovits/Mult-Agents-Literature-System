from __future__ import annotations

import unittest

from evireview_core.domain.models import EvidenceBlock, VerificationResult, Weakness
from evireview_core.verification.labels import VerifierLabel, is_supported_or_better


class DomainModelTest(unittest.TestCase):
    def test_package_exposes_version(self) -> None:
        import evireview_core

        self.assertEqual(evireview_core.__version__, "0.1.0")

    def test_weakness_round_trip_dict(self) -> None:
        weakness = Weakness(
            weakness_id="w1",
            paper_id="p1",
            weakness_text="The experiment lacks ablation studies.",
            category="experiment",
            severity="major",
            source="human_review",
        )

        self.assertEqual(Weakness.from_dict(weakness.to_dict()), weakness)

    def test_evidence_block_round_trip_dict(self) -> None:
        block = EvidenceBlock(
            block_id="b1",
            paper_id="p1",
            section_path="Experiments > Ablations",
            section_type="experiment",
            text="We compare the model without the reranker.",
        )

        self.assertEqual(EvidenceBlock.from_dict(block.to_dict()), block)

    def test_verification_result_round_trip_dict(self) -> None:
        result = VerificationResult(
            weakness_id="w1",
            label=VerifierLabel.PARTIALLY_SUPPORTED.value,
            support_score=0.7,
            evidence_block_ids=("b1", "b2"),
            rationale="The paper mentions ablations but not all claimed settings.",
            verifier="heuristic_v1",
        )

        self.assertEqual(VerificationResult.from_dict(result.to_dict()), result)

    def test_supported_or_better(self) -> None:
        self.assertTrue(is_supported_or_better(VerifierLabel.SUPPORTED.value))
        self.assertTrue(is_supported_or_better(VerifierLabel.PARTIALLY_SUPPORTED.value))
        self.assertFalse(is_supported_or_better(VerifierLabel.UNSUPPORTED.value))


if __name__ == "__main__":
    unittest.main()
