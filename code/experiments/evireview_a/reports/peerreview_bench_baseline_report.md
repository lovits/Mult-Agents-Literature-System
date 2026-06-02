# PeerReview Bench Ready-label Baseline

This experiment uses an external dataset with existing expert annotations, so no new manual labels are required.

- Dataset: https://huggingface.co/datasets/prometheus-eval/peerreview-bench
- License: CC-BY-4.0
- Local rows used: 3881

| Task | Train | Test | Majority Macro-F1 | Review NB Macro-F1 | Balanced Review NB Macro-F1 | Context NB Macro-F1 | Balanced Context NB Macro-F1 | Evidence-aware Feature Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| correctness | 3079 | 802 | 0.4646 | 0.4901 | 0.4846 | 0.5601 | 0.5686 | - |
| significance | 2720 | 696 | 0.2486 | 0.3723 | 0.4207 | 0.3241 | 0.3205 | - |
| evidence | 2266 | 602 | 0.4819 | 0.4819 | 0.4801 | 0.5153 | 0.5318 | 0.573 |

Split rule: grouped by `paper_id` with a deterministic 80/20 paper-level split, so rows from the same paper do not appear in both train and test.

## Balanced Context NB Per-label Recall

| Task | Label | Support | Recall | F1 |
| --- | --- | ---: | ---: | ---: |
| correctness | Correct | 696 | 0.8649 | 0.8763 |
| correctness | Not Correct | 106 | 0.283 | 0.2609 |
| significance | Marginally Significant | 188 | 0.2181 | 0.2405 |
| significance | Not Significant | 94 | 0.0 | 0.0 |
| significance | Significant | 414 | 0.8333 | 0.721 |
| evidence | Requires More | 42 | 0.2381 | 0.2128 |
| evidence | Sufficient | 560 | 0.925 | 0.9333 |

## Evidence-aware Feature Baseline

| Model | Macro-F1 | Accuracy | Requires More recall | Requires More F1 | Threshold |
| --- | ---: | ---: | ---: | ---: | ---: |
| Balanced context NB | 0.5318 | 0.9169 | 0.0714 | 0.1071 | - |
| Evidence-aware feature logistic | 0.573 | 0.8771 | 0.2381 | 0.2128 | 0.6574 |

Top feature weights:

| Feature | Weight |
| --- | ---: |
| `paper_overlap_ratio` | 0.3305 |
| `evidence_demand_count_log` | -0.2561 |
| `category_reproducibility` | -0.2494 |
| `strong_claim_count_log` | -0.2247 |
| `quote_count_log` | 0.2095 |
| `review_token_count_log` | -0.1952 |
| `question_count_log` | -0.1819 |
| `mentions_missing` | 0.1693 |
| `sufficient_marker_count_log` | -0.1612 |
| `number_count_log` | -0.1343 |
| `category_clarity` | -0.132 |
| `category_method` | 0.1112 |

## Best Macro-F1 Baseline By Task

| Task | Best baseline | Macro-F1 | Accuracy | Note |
| --- | --- | ---: | ---: | --- |
| correctness | balanced_context_multinomial_naive_bayes_v2 | 0.5686 | 0.788 | context helps verifier signal |
| significance | balanced_multinomial_naive_bayes_v1 | 0.4207 | 0.5589 | review item priority signal |
| evidence | evidence_aware_feature_logistic_v1 | 0.573 | 0.8771 | context helps verifier signal |

## Interpretation

- This is a direct no-manual-label verifier/ranker-quality baseline aligned with the thesis modules.
- `correctness`, `significance`, and `evidence` map to verifier correctness, ranker priority, and evidence-grounding dimensions.
- The grouped split is stricter than row-level random/modulo splitting because it blocks same-paper leakage.
- Context NB concatenates paper title, short paper excerpt, review item, and annotator comments. It is still a simple lexical floor, not a final verifier.
- Balanced NB uses an inverse-frequency prior to expose minority-class recall trade-offs; it should be reported with Macro-F1 and per-label recall, not accuracy alone.
- The current baseline is intentionally transparent; stronger LLM or embedding models can be added after this floor is stable.
