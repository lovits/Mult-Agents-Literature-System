# Agent-RAG Hybrid Retrieval Design Evidence

Date: 2026-06-07

## Research Question

Which retrieval and verification boundaries should govern the backend-first Agent-RAG refactor without adding a new runtime dependency?

## Evidence Synthesis

1. Qdrant's Hybrid Query API combines dense and sparse retrieval through independent `prefetch` queries followed by rank fusion. It supports RRF directly and therefore provides a stable remote equivalent of the local hybrid contract.
2. Recent scientific-literature retrieval evaluation reports that RRF can improve relevance over either sparse or dense retrieval, but the benefit depends on the corpus and query form. This supports evaluating hybrid rather than assuming it is always superior.
3. Recent evidence-sufficiency work distinguishes topical retrieval from support verification. This matches the project's explicit `retrieve -> verify -> rank` graph and argues against merging verifier decisions into retriever scores.
4. Recent agentic-RAG work separates trajectory diagnosis from targeted repair. This supports named graph profiles and auditable node traces as the basis for later repair loops.

## Architecture Decision

- Keep local `dense_search` injectable so experiments can use cached or provider embeddings without coupling the core to an SDK.
- Fuse BM25 and dense rankings with RRF rather than combining incomparable raw scores.
- Expose Qdrant through a dependency-free, transport-injected Query API adapter.
- Keep verification as a separate graph node and evaluate graph profiles by ablation.
- Treat retrieval metrics, silver verifier diagnostics, and provider diagnostics as separate metric boundaries.

## Sources

- Qdrant, Hybrid and Multi-Stage Queries: https://qdrant.tech/documentation/search/hybrid-queries/
- Prajapati, *Hybrid Retrieval for COVID-19 Literature: Comparing Rank Fusion and Projection Fusion with Diversity Reranking* (2026): https://arxiv.org/abs/2604.13728
- Qiu et al., *SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective Retrieval-Augmented Generation* (2026): https://arxiv.org/abs/2605.03534
- Jiao et al., *Doctor-RAG: Failure-Aware Repair for Agentic Retrieval-Augmented Generation* (2026): https://arxiv.org/abs/2604.00865

## Limitations

- The local hybrid experiment uses cached OpenRouter embeddings and does not benchmark Qdrant latency or indexing behavior.
- CLAIMCHECK target mapping remains constrained by the upstream mapped-claim protocol.
- Current graph ablation uses a shared silver verifier reference, not human gold evidence labels.
