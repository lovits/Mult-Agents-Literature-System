# Dense, Hybrid, And Qdrant Retrieval Plan

**Goal:** Add dependency-free dense and hybrid retrieval contracts, a Qdrant Query API adapter, and a ready-label retrieval comparison.

**Architecture:** Keep local dense scoring injectable, fuse sparse and dense rankings with reciprocal rank fusion, and isolate Qdrant behind a transport-injected HTTP adapter. Evaluate BM25, dense LSA, and RRF hybrid on the same CLAIMCHECK mapped targets.

**Tasks**

1. Write RED tests for dense cosine ranking, RRF hybrid fusion, and Qdrant request/response mapping.
2. Implement local dense/hybrid retrieval and the Qdrant adapter without new dependencies.
3. Run a CLAIMCHECK ready-label dense/hybrid experiment and validator.
4. Export results through unified metrics and Phase 2H-B validator.
5. Run regression, document, commit, and push.
