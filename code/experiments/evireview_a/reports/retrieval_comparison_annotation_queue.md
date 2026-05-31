# Retrieval Comparison Annotation Queue

This queue prepares human gold labels for comparing section-aware retrieval and hierarchical Paper-RAG.

| Metric | Value |
| --- | ---: |
| Candidate pairs | 1463 |
| Selected rows | 300 |
| Top-1 disagreement rate | 0.6138 |
| Top-3 disagreement rate | 0.9645 |

## Selected Category Counts

| Category | Rows |
| --- | ---: |
| clarity | 43 |
| experiment | 54 |
| method | 54 |
| other | 54 |
| related_work | 53 |
| reproducibility | 18 |
| validity | 24 |

## Labeling Target

- Fill `gold_best_retriever` with `section`, `hierarchical`, `tie`, or `neither`.
- Fill `gold_label` using the existing weakness-evidence label schema.
- Fill `gold_evidence_block_ids` with the supporting evidence block ids when any evidence is useful.
