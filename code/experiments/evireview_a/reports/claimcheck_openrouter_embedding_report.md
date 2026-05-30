# CLAIMCHECK OpenRouter Embedding Retrieval

This report records the OpenRouter free-model embedding retrieval experiment for CLAIMCHECK.

## Setup

- Status: `ok`
- Model: `nvidia/llama-nemotron-embed-vl-1b-v2:free`
- Endpoint: `https://openrouter.ai/api/v1/embeddings`
- Texts embedded: 1696
- License note: Raw CLAIMCHECK text, embeddings cache, and row-level rankings are not committed.

## Main Split Results

| Hit@1 | Hit@3 | Hit@5 | Hit@10 | MRR | Mapped / Grounded |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.2222 | 0.5 | 0.6944 | 0.7917 | 0.4067 | 72 / 108 |

## Interpretation

- This result should be compared against the current lexical floor: char trigram Hit@3 = 0.375.
- If OpenRouter embeddings do not improve over that floor, the next step should be LLM reranking rather than more embedding-only retrieval.
