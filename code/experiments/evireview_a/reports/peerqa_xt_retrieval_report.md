# PeerQA-XT Paper-RAG Retrieval Baseline

This experiment uses PeerQA-XT as a no-new-manual-label Paper-RAG QA dataset.

- Dataset: https://huggingface.co/datasets/UKPLab/PeerQA-XT
- Paper: https://arxiv.org/abs/2502.13668
- License: CC-BY-NC-SA-4.0
- Split / rows used: `test` / 80 of 1252
- Gold evidence spans are not provided, so this report uses answer-token support as a retrieval proxy.

| Method | Rows | Hit@1 | Hit@3 | Hit@5 | Mean answer recall@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| bm25_question | 80 | 0.275 | 0.65 | 0.8625 | 0.5248 |
| tfidf_question | 80 | 0.25 | 0.7 | 0.8 | 0.5216 |
| hybrid_question | 80 | 0.2625 | 0.675 | 0.8375 | 0.5232 |
| oracle_answer_query | 80 | 0.5 | 0.9125 | 0.975 | 0.6337 |

## Interpretation

- PeerQA-XT fits the thesis retrieval module because each row has a peer-review-derived question, a final answer, and full paper context.
- `hybrid_question` is the fair baseline for question-only retrieval; `oracle_answer_query` is a diagnostic ceiling, not a deployable system.
- The next improvement should add section-aware / hierarchical retrieval tools and compare them against this question-only floor.
