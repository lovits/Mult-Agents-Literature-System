# Retrieval Proxy Evaluation

These are proxy diagnostics before manual weakness-evidence gold labels are complete. They should not be reported as final retrieval accuracy.

| Retriever | Non-empty | Top-1 Section Align | Top-3 Any Align | Avg Section Diversity | Avg Top-1 Score |
| --- | ---: | ---: | ---: | ---: | ---: |
| bm25 | 0.9891 | 0.6151 | 0.8341 | 2.6503 | 24.839129 |
| tfidf_cosine | 0.9891 | 0.6247 | 0.8238 | 2.5847 | 0.153045 |
| hybrid_bm25_tfidf | 0.9891 | 0.6164 | 0.8300 | 2.6455 | 0.883120 |
| section_aware_hybrid | 0.9891 | 0.7021 | 0.8618 | 2.6192 | 0.949624 |
| human_hierarchical_paper_rag | 1.0000 | 0.9993 | 1.0000 | 1.8640 | 0.246929 |

## Interpretation

- `Top-1 Section Align` checks whether the first retrieved block's section type matches a lightweight category-to-section rubric.
- `Top-3 Any Align` is more forgiving and checks whether any of the first three blocks matches the rubric.
- `Avg Section Diversity` helps detect retrieval collapse into one section type.
- Manual gold labels are still required for true Evidence Recall@K and verifier evaluation.
