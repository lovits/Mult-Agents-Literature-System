# CLAIMCHECK OpenRouter LLM Reranking

This report evaluates whether a free OpenRouter chat model improves paper-claim ranking after embedding retrieval.

## Setup

- Status: `blocked`
- Model: `qwen/qwen3-next-80b-a3b-instruct:free`
- Endpoint: `https://openrouter.ai/api/v1/chat/completions`
- Blocked reason: OpenRouter HTTP error 429: Provider returned error; provider=Venice; retry_after_seconds=12
- Required env: `OPENROUTER_API_KEY`

## Interpretation

- The script is ready, but the required OpenRouter runtime condition is not satisfied.
