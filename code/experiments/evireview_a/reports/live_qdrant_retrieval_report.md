# Live Qdrant CLAIMCHECK Retrieval

Real Qdrant indexing and Query API evaluation on the same ready-label CLAIMCHECK mapped targets.

| Method | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR | Mean ms | P95 ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qdrant_bm25_sparse | 0.1806 | 0.3611 | 0.4167 | 0.3130 | 4.232 | 5.999 |
| qdrant_openrouter_dense | 0.2222 | 0.5000 | 0.6944 | 0.4067 | 4.406 | 6.791 |
| qdrant_bm25_openrouter_rrf_hybrid | 0.2639 | 0.4306 | 0.5972 | 0.4039 | 3.647 | 4.086 |

- Indexed points: `6606` in `7.636` seconds.
- Best main Hit@3: `qdrant_openrouter_dense`.
- Dense representation: cached OpenRouter embeddings, so this isolates live Qdrant execution from local model changes.
- Sparse representation reproduces the existing per-row BM25 scoring as sparse dot products.
- Queries return the complete filtered candidate set and break equal scores by claim index for reproducible metrics.
- No manual labels or row-level raw CLAIMCHECK outputs were added.
