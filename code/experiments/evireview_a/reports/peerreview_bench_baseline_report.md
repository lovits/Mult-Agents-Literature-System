# PeerReview Bench Ready-label Baseline

This experiment uses an external dataset with existing expert annotations, so no new manual labels are required.

- Dataset: https://huggingface.co/datasets/prometheus-eval/peerreview-bench
- License: CC-BY-4.0
- Local rows used: 3881

| Task | Train | Test | Majority Macro-F1 | Review-item NB Macro-F1 | Context NB Macro-F1 | Context NB Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| correctness | 3079 | 802 | 0.4646 | 0.4901 | 0.5601 | 0.818 |
| significance | 2720 | 696 | 0.2486 | 0.3723 | 0.3241 | 0.5833 |
| evidence | 2266 | 602 | 0.4819 | 0.4819 | 0.5153 | 0.9169 |

Split rule: grouped by `paper_id` with a deterministic 80/20 paper-level split, so rows from the same paper do not appear in both train and test.

## Context NB Per-label Recall

| Task | Label | Support | Recall | F1 |
| --- | --- | ---: | ---: | ---: |
| correctness | Correct | 696 | 0.9124 | 0.8969 |
| correctness | Not Correct | 106 | 0.1981 | 0.2234 |
| significance | Marginally Significant | 188 | 0.1809 | 0.2274 |
| significance | Not Significant | 94 | 0.0 | 0.0 |
| significance | Significant | 414 | 0.8986 | 0.7447 |
| evidence | Requires More | 42 | 0.0476 | 0.0741 |
| evidence | Sufficient | 560 | 0.9821 | 0.9565 |

## Interpretation

- This is a direct no-manual-label verifier/ranker-quality baseline aligned with the thesis modules.
- `correctness`, `significance`, and `evidence` map to verifier correctness, ranker priority, and evidence-grounding dimensions.
- The grouped split is stricter than row-level random/modulo splitting because it blocks same-paper leakage.
- Context NB concatenates paper title, short paper excerpt, review item, and annotator comments. It is still a simple lexical floor, not a final verifier.
- The current baseline is intentionally transparent; stronger LLM or embedding models can be added after this floor is stable.
