# PeerReview Bench Ready-label Baseline

This experiment uses an external dataset with existing expert annotations, so no new manual labels are required.

- Dataset: https://huggingface.co/datasets/prometheus-eval/peerreview-bench
- License: CC-BY-4.0
- Local rows used: 300

| Task | Train | Test | Majority Macro-F1 | NB Macro-F1 | NB Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| correctness | 240 | 60 | 0.4643 | 0.4643 | 0.8667 |
| significance | 214 | 54 | 0.2622 | 0.4935 | 0.7593 |
| evidence | 199 | 50 | 0.4898 | 0.4898 | 0.96 |

## Interpretation

- This is a direct no-manual-label verifier/ranker-quality baseline aligned with the thesis modules.
- `correctness`, `significance`, and `evidence` map to verifier correctness, ranker priority, and evidence-grounding dimensions.
- The current baseline is intentionally transparent; stronger LLM or embedding models can be added after this floor is stable.
