# MiniMax M2.7 Structured Reviewer Diagnostic

This is a provider and Agent-RAG handoff diagnostic on the local OpenReview/PRISM sample, not human-gold evaluation.

## Result

- Status: `ok`
- Model: `MiniMax-M2.7`
- Selected papers: 5
- Papers with generation: 5
- Generated weaknesses: 15
- Failed papers: 0
- Recall@0.18 coverage proxy: 0.5232
- Mean silver support score: 0.467
- Silver verifier labels: {'Partially Supported': 5, 'Mentioned but Not Problem': 7, 'Supported': 2, 'Unsupported': 1}

## Boundary

- The API key was read from `MINIMAX_API_KEY` and was not persisted.
- Generated weaknesses are silver diagnostic outputs.
- Retrieval and verifier metrics are diagnostic proxies and are not final thesis gold metrics.
