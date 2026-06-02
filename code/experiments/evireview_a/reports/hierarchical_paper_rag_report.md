# Hierarchical Paper-RAG Retrieval Experiment

This report evaluates a transparent hierarchical retrieval interface for generated review weaknesses.

## Retrieval Tools

- `keyword_search`: exact term overlap with section prior.
- `semantic_search`: lexical + character n-gram similarity with section prior.
- `section_read`: category-guided reads over expected paper sections.
- `RRF merge`: reciprocal-rank fusion plus lexical, character, and section scores.

## Results

| Source | Weaknesses | Top-1 section align | Top-3 section align | Mean support | Partially-supported-or-better | Labels |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| glm_reviewer | 21 | 1.0 | 1.0 | 0.5304 | 0.7143 | {'Partially Supported': 12, 'Mentioned but Not Problem': 4, 'Unsupported': 2, 'Supported': 3} |
| rubric_agent | 194 | 1.0 | 1.0 | 0.1999 | 0.0258 | {'Unsupported': 113, 'Mentioned but Not Problem': 76, 'Partially Supported': 5} |

## Interpretation

- The hierarchical interface makes retrieval decisions auditable as explicit tool traces.
- This is an architecture diagnostic: current labels still come from the silver verifier, not human gold.
- Next step: compare this retriever against section-aware lexical retrieval on human-labeled gold items when the gold set reaches 200-300 items.
