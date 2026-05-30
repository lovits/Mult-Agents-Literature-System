# CLAIMCHECK Paper-grounded Weakness Benchmark

This experiment checks the stronger benchmark route: reviewer weaknesses grounded to paper claims.

## Dataset

- Source repository: https://github.com/JHU-CLSP/CLAIMCHECK
- Paper: https://aclanthology.org/2025.findings-emnlp.1185/
- License note: no upstream LICENSE file was detected; raw and row-level text files are intentionally not committed.
- Gold definition: A weakness is Grounded when CLAIMCHECK annotators linked it to at least one target claim.
- Pilot: 5 paper-review pairs, 13 weaknesses.
- Main: 55 paper-review pairs, 155 weaknesses.
- Main grounding labels: `Grounded: 108, Ungrounded: 47`

## Grounded / Ungrounded Baselines

| Baseline | Main Accuracy | Main Macro-F1 | Prediction Counts |
| --- | ---: | ---: | --- |
| `majority_pilot_label` | 0.6968 | 0.4106 | `Grounded: 155` |
| `weakness_claim_lexical_threshold_v0` | 0.6968 | 0.4106 | `Grounded: 155` |

## Claim Association Ranking

- Grounded weaknesses: 108
- Mapped targets: 72
- Unmapped targets: 36
- Hit@1: 0.1944
- Hit@3: 0.3194
- Hit@5: 0.4306
- MRR: 0.3106

## Interpretation

- CLAIMCHECK is closer to the thesis target than SubstanReview because weaknesses are linked to claims from the reviewed paper.
- The simple lexical classifier collapses to the pilot-majority behavior because the pilot split is tiny and highly skewed.
- Lexical ranking still recovers some target claims on the main split, but Hit@3 remains low, showing that paper-claim grounding needs a semantic retriever/verifier rather than keyword overlap.
- This benchmark should be the next target for an LLM or embedding-based verifier, while SubstanReview remains useful for review-internal substantiation.
