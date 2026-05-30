# CLAIMCHECK OpenRouter Embedding Verifier

This report evaluates whether max embedding similarity can classify CLAIMCHECK weaknesses as Grounded or Ungrounded.

## Setup

- Status: `ok`
- Embedding model: `nvidia/llama-nemotron-embed-vl-1b-v2:free`
- Warning: This is a diagnostic verifier baseline; pilot split is tiny and skewed.

## Main Split Results

| Setting | Threshold | Accuracy | Macro-F1 | Grounded F1 | Ungrounded F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pilot-selected threshold | 0.0 | 0.6968 | 0.4106 | 0.8213 | 0.0 |
| Oracle main threshold diagnostic | 0.3087 | 0.6839 | 0.5524 | 0.795 | 0.3099 |

## Interpretation

- Embedding similarity is useful for retrieval, but threshold-only classification is not a reliable verifier.
- The pilot-selected threshold collapses because the pilot set has only one Ungrounded item.
- Even the oracle main threshold remains modest, so the next verifier should use richer features or an LLM judgment prompt.
