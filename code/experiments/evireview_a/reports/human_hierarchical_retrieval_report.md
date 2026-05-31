# Human Weakness Hierarchical Paper-RAG

This report applies the hierarchical Paper-RAG retriever to human reviewer weaknesses.

## Overall

| Queries | Non-empty | Top-1 section align | Top-3 any align | Top-1 tool mix |
| ---: | ---: | ---: | ---: | --- |
| 1463 | 1.0 | 0.9993 | 1.0 | {'semantic_search': 807, 'keyword_search': 567, 'section_read': 89} |

## Category Diagnostics

| Category | Queries | Top-1 section align |
| --- | ---: | ---: |
| clarity | 43 | 1.0 |
| experiment | 425 | 1.0 |
| method | 377 | 1.0 |
| other | 447 | 1.0 |
| related_work | 129 | 1.0 |
| reproducibility | 18 | 1.0 |
| validity | 24 | 0.9583 |

## Interpretation

- This is a proxy retrieval diagnostic over existing human reviewer weaknesses.
- It prepares a direct comparison with section-aware retrieval once gold weakness-evidence labels are available.
- The next required evidence is human annotation of whether retrieved blocks truly support each weakness.
