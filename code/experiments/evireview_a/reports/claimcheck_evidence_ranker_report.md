# CLAIMCHECK Evidence-aware Ranker

This report evaluates whether verifier signals can rank critique weaknesses by paper-groundedness inside each paper-review group.

## Setup

- Status: `ok`
- Dataset: CLAIMCHECK
- Validation: Feature-verifier scores are out-of-fold by paper_review_id; lexical and embedding baselines are unsupervised.
- Rows: 155
- Paper-review groups: 54
- Label counts: {'Grounded': 108, 'Ungrounded': 47}
- Warning: Aggregate diagnostic only; CLAIMCHECK row-level text is not committed because the upstream repository has no detected LICENSE.

## Ranking Results

| Method | Groups | MAP | NDCG@3 | NDCG@5 | Top-1 grounded | Bottom-1 ungrounded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OpenRouter embedding max similarity | 24 | 0.7502 | 0.7632 | 0.8193 | 0.5833 | 0.5833 |
| BM25 max similarity | 24 | 0.7771 | 0.7934 | 0.8205 | 0.625 | 0.6667 |
| Out-of-fold feature verifier probability | 24 | 0.7424 | 0.7828 | 0.8198 | 0.5833 | 0.5417 |
| Candidate claim count | 24 | 0.7597 | 0.7806 | 0.8077 | 0.5833 | 0.625 |

## Interpretation

- Best aggregate ranker in this diagnostic: BM25 max similarity with MAP 0.7771 and Top-1 grounded rate 0.625.
- The out-of-fold feature verifier does not beat BM25 as a ranking signal, so the current ranker should keep retrieval similarity as the primary ordering feature.
- The verifier remains useful as a separate grounded/ungrounded decision module, but its probability should not be treated as a mature evidence-aware ranking score yet.
