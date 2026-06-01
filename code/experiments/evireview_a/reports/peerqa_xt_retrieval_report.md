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
| section_aware_question | 80 | 0.275 | 0.7 | 0.8375 | 0.5248 |
| hierarchical_question | 80 | 0.2375 | 0.675 | 0.825 | 0.5161 |
| query_decomposed_question | 80 | 0.1875 | 0.625 | 0.7625 | 0.5113 |
| domain_section_aware_question | 80 | 0.1875 | 0.6125 | 0.775 | 0.5144 |
| domain_hierarchical_question | 80 | 0.2125 | 0.575 | 0.7875 | 0.5067 |
| oracle_answer_query | 80 | 0.5 | 0.9125 | 0.975 | 0.6337 |

## Interpretation

- PeerQA-XT fits the thesis retrieval module because each row has a peer-review-derived question, a final answer, and full paper context.
- `hybrid_question` is the fair baseline for question-only retrieval; `query_decomposed_question` adds rule-based QA intent expansion.
- `domain_section_aware_question` uses biomedical article section markers such as Background, Methods, Results, and Discussion.
- `domain_hierarchical_question` fuses BM25, TF-IDF, and domain-aware section_read rankings with weighted reciprocal rank fusion.
- In this probe, section-aware retrieval ties the best lexical Hit@1/Hit@3 floor, while hand-written query expansion degrades retrieval.
- `oracle_answer_query` is a diagnostic ceiling, not a deployable system.
