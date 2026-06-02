# PeerQA-XT Paper-RAG Retrieval Baseline

This experiment uses PeerQA-XT as a no-new-manual-label Paper-RAG QA dataset.

- Dataset: https://huggingface.co/datasets/UKPLab/PeerQA-XT
- Paper: https://arxiv.org/abs/2502.13668
- License: CC-BY-NC-SA-4.0
- Split / rows used: `test` / 500 of 1252
- Gold evidence spans are not provided, so this report uses answer-token support as a retrieval proxy.

| Method | Rows | Hit@1 | Hit@3 | Hit@5 | Mean answer recall@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| bm25_question | 500 | 0.24 | 0.598 | 0.794 | 0.5001 |
| tfidf_question | 500 | 0.23 | 0.592 | 0.774 | 0.4906 |
| hybrid_question | 500 | 0.242 | 0.596 | 0.792 | 0.4988 |
| section_aware_question | 500 | 0.246 | 0.606 | 0.806 | 0.5005 |
| hierarchical_question | 500 | 0.222 | 0.59 | 0.788 | 0.4995 |
| query_decomposed_question | 500 | 0.208 | 0.532 | 0.734 | 0.4751 |
| domain_section_aware_question | 500 | 0.208 | 0.536 | 0.742 | 0.4774 |
| domain_hierarchical_question | 500 | 0.214 | 0.526 | 0.734 | 0.4752 |
| oracle_answer_query | 500 | 0.496 | 0.902 | 0.966 | 0.6257 |

## Interpretation

- PeerQA-XT fits the thesis retrieval module because each row has a peer-review-derived question, a final answer, and full paper context.
- `hybrid_question` is the fair baseline for question-only retrieval; `query_decomposed_question` adds rule-based QA intent expansion.
- `domain_section_aware_question` uses biomedical article section markers such as Background, Methods, Results, and Discussion.
- `domain_hierarchical_question` fuses BM25, TF-IDF, and domain-aware section_read rankings with weighted reciprocal rank fusion.
- In this probe, section-aware retrieval ties the best lexical Hit@1/Hit@3 floor, while hand-written query expansion degrades retrieval.
- `oracle_answer_query` is a diagnostic ceiling, not a deployable system.
