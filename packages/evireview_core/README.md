# evireview_core

Reusable Python core for the EviReview-Lite Agent-RAG refactor.

This package contains dependency-free domain models, parsing helpers, retrieval baselines, verification labels, evidence-aware ranking, and deterministic workflow helpers. It is intentionally separate from `code/experiments/evireview_a`, which remains the reproducible experiment sandbox.

Review audits are orchestrated by an explicit dependency-free Agent-RAG state graph:

`retrieve_evidence -> verify_weaknesses -> rank_findings`

The graph records a public node trace and keeps nodes pure enough to substitute retrievers, verifiers, rankers, and provider-backed generation in later experiments.

Verifier and workflow labels from this package are `silver diagnostic` outputs. They are not human gold evidence labels.

Run tests from the repository root:

```bash
PYTHONPATH=packages/evireview_core python3 -m unittest discover -s tests/evireview_core -v
```
