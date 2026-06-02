# GLM-4.6V Structured Reviewer Experiment

This report validates a GLM-4.6V structured reviewer deployment on the local OpenReview/PRISM sample.

## Setup

- Status: `ok`
- Model: `glm-4.6v`
- Endpoint: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- Selected papers: 10
- Generated weaknesses: 27
- Papers with generation: 10
- Elapsed seconds: 48.56
- Warning: Small GLM-4.6V reviewer diagnostic sample; API key is never written to disk.

## Coverage Proxy

- Generic rate: 0.0741

| Similarity threshold | Evaluated human weaknesses | Covered | Recall |
| ---: | ---: | ---: | ---: |
| 0.12 | 289 | 239 | 0.827 |
| 0.18 | 289 | 172 | 0.5952 |
| 0.24 | 289 | 39 | 0.1349 |

## Verifier Handoff

- Retrieved generated weaknesses: 27
- Verified generated weaknesses: 27
- Label counts: {'Mentioned but Not Problem': 9, 'Partially Supported': 13, 'Unsupported': 3, 'Supported': 2}
- Mean support score: 0.467

## Interpretation

- This is a small deployment validation, not a full-scale final reviewer result.
- The result should be compared against the deterministic rubric-agent baseline before expanding to all 50 papers.
- Generated weaknesses are immediately passed through local retrieval and silver verifier diagnostics so unsupported comments are visible.
