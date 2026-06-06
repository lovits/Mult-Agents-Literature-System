# CLAIMCHECK Dense And Hybrid Retrieval

Ready-label comparison on the same mapped CLAIMCHECK targets. Dense retrieval reuses the committed experiment's OpenRouter embedding cache; hybrid retrieval fuses BM25 and dense ranks with RRF.

| Method | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR |
| --- | ---: | ---: | ---: | ---: |
| bm25_sparse | 0.1806 | 0.3611 | 0.4167 | 0.3135 |
| openrouter_dense | 0.2222 | 0.5000 | 0.6944 | 0.4067 |
| bm25_openrouter_rrf_hybrid | 0.2361 | 0.4306 | 0.5556 | 0.3834 |

- Best main Hit@3: `openrouter_dense`.
- Metric boundary: gold mapped targets supplied by CLAIMCHECK; no manual labels were added.
- Qdrant is an execution adapter for the same dense+sparse RRF contract, not a separate accuracy method in this local comparison.
