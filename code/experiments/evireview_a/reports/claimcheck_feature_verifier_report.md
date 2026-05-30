# CLAIMCHECK Feature Verifier

This report evaluates whether a lightweight feature-fusion verifier can classify CLAIMCHECK weaknesses as Grounded or Ungrounded.

## Setup

- Status: `ok`
- Dataset: CLAIMCHECK
- Validation: 5-fold grouped cross-validation by paper_review_id on the CLAIMCHECK main split
- Rows: 155
- Paper-review groups: 54
- Features: 17
- Warning: Diagnostic experiment only; CLAIMCHECK row-level text is not committed because the upstream repository has no detected LICENSE.
- Leakage controls:
  - Grouped cross-validation keeps paper_review_id groups out of both train and test folds.
  - Gold target claim counts, annotation confidence, target claim text, and human weakness type annotations are excluded from features.
  - Weakness category features are inferred from weakness text with the local rule-based classifier.

## Cross-Validation Results

| Method | Accuracy | Macro-F1 | Grounded F1 | Ungrounded F1 |
| --- | ---: | ---: | ---: | ---: |
| Train-fold majority baseline | 0.6968 | 0.4106 | 0.8213 | 0.0 |
| Train-fold embedding threshold | 0.6774 | 0.5477 | 0.7899 | 0.3056 |
| Feature-fusion verifier | 0.5548 | 0.5076 | 0.6601 | 0.3551 |

## Highest-Magnitude Mean Weights

| Feature | Mean logistic weight |
| --- | ---: |
| `type_clarity` | 0.4135 |
| `type_method` | 0.3434 |
| `mean_top5_embedding_similarity` | 0.3387 |
| `type_experiment` | -0.3234 |
| `type_reproducibility` | 0.2586 |
| `type_related_work` | -0.1833 |
| `weakness_token_count_log` | -0.1763 |
| `type_other` | -0.1273 |
| `candidate_claim_count_log` | 0.104 |
| `max_bm25_similarity` | 0.0964 |
| `max_lexical_similarity` | 0.0964 |
| `max_tfidf_similarity` | 0.0964 |

## Interpretation

- The feature-fusion verifier improves the Ungrounded class compared with a majority baseline, but it is not yet a deployable final verifier.
- The result supports the architecture decision that RAG retrieval and verifier judgment should be separate modules.
- The next experiment should add an LLM-as-judge prompt on a small, rate-limited subset or train a stronger supervised verifier if a larger licensed split is available.
