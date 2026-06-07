from __future__ import annotations

import unittest

from evireview_core.domain.models import Weakness
from evireview_core.providers.base import ProviderGeneration
from evireview_core.retrieval.bm25 import RetrievedEvidence
from evireview_core.verification.structured_judge import StructuredEvidenceVerifier


class StructuredEvidenceVerifierTest(unittest.TestCase):
    def test_maps_provider_judgment_to_constrained_verification_result(self) -> None:
        class FakeProvider:
            def generate_json(self, system: str, user: str, **_kwargs: object) -> ProviderGeneration:
                self.system = system
                self.user = user
                return ProviderGeneration(
                    payload={
                        "label": "Supported",
                        "support_score": 1.7,
                        "evidence_block_ids": ["b1", "not-retrieved"],
                        "rationale": "The evidence explicitly reports the limitation.",
                    },
                    metadata={"provider_name": "minimax"},
                )

        provider = FakeProvider()
        verifier = StructuredEvidenceVerifier(provider, source="minimax_evidence_judge")
        result = verifier(
            Weakness("w1", "p1", "The evaluation uses only one dataset.", "experiment", "major"),
            [RetrievedEvidence("b1", "p1", "Experiments", "experiment", "Only one dataset is used.", 1, 1.0, "bm25")],
        )

        self.assertEqual(result.label, "Supported")
        self.assertEqual(result.support_score, 1.0)
        self.assertEqual(result.evidence_block_ids, ("b1",))
        self.assertEqual(result.verifier, "minimax_evidence_judge")
        self.assertIn("untrusted", provider.system.lower())

    def test_invalid_provider_label_is_rejected(self) -> None:
        class FakeProvider:
            def generate_json(self, *_args: object, **_kwargs: object) -> ProviderGeneration:
                return ProviderGeneration(payload={"label": "Accept", "support_score": 0.9}, metadata={})

        with self.assertRaisesRegex(ValueError, "unsupported verifier label"):
            StructuredEvidenceVerifier(FakeProvider())(
                Weakness("w1", "p1", "Missing evaluation.", "experiment"),
                [RetrievedEvidence("b1", "p1", "Experiments", "experiment", "Evaluation.", 1, 1.0, "bm25")],
            )


if __name__ == "__main__":
    unittest.main()
