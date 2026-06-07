# Query Planner Ablation On CLAIMCHECK

Ready-label comparison of direct weakness queries and transparent category-expansion queries using the same BM25 retriever.

| Planner | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR |
| --- | ---: | ---: | ---: | ---: |
| direct | 0.1806 | 0.3611 | 0.4167 | 0.3135 |
| category_expansion | 0.1806 | 0.3611 | 0.4167 | 0.3144 |

- Main Hit@3 delta: `+0.0000`.
- Metric boundary: gold mapped CLAIMCHECK targets; no manual labels added.
- A negative delta is retained as evidence that naive query expansion should not become the default planner.
