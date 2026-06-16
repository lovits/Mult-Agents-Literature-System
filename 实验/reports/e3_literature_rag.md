# E3 Controlled Literature-RAG Baselines

## Protocol

- Frozen local corpus: true
- Online retrieval: false
- Purpose: novelty, related work, and missing-baseline evidence support

## Dataset

- Markdown documents: 33
- Metadata-complete documents: 32
- Year range: 2017--2026

## Metrics

| System | Recall@10 | MRR | Literature Relevance@10 | Citation Validity | Future Leakage |
|---|---:|---:|---:|---:|---:|
| L0_no_literature | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |
| L1_keyword | 1.0000 | 0.8571 | 0.0264 | 1.0000 | 22 |
| L2_hybrid | 1.0000 | 0.8929 | 0.0265 | 1.0000 | 20 |
| L3_hybrid_metadata_filter | 1.0000 | 0.9048 | 0.0241 | 1.0000 | 0 |

## Interpretation

L0_no_literature is the no-external-evidence baseline. L3_hybrid_metadata_filter is the controlled Literature-RAG setting used by the proposed system: it keeps the hybrid ranking signal while enforcing the as-of-year metadata boundary.
