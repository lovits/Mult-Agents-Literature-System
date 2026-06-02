# GLM-4.6V Structured Reviewer Experiment

This report validates a GLM-4.6V structured reviewer deployment on the local OpenReview/PRISM sample.

## Setup

- Status: `ok`
- Model: `glm-4.6v`
- Endpoint: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- Selected papers: 10
- Generated weaknesses: 21
- Papers with generation: 8
- Elapsed seconds: 92.48
- Warning: Small GLM-4.6V reviewer deployment sample; API key is never written to disk.

## Coverage Proxy

- Generic rate: 0.0476

| Similarity threshold | Evaluated human weaknesses | Covered | Recall |
| ---: | ---: | ---: | ---: |
| 0.12 | 229 | 188 | 0.821 |
| 0.18 | 229 | 130 | 0.5677 |
| 0.24 | 229 | 30 | 0.131 |

## Verifier Handoff

- Retrieved generated weaknesses: 21
- Verified generated weaknesses: 21
- Label counts: {'Mentioned but Not Problem': 6, 'Partially Supported': 10, 'Unsupported': 3, 'Supported': 2}
- Mean support score: 0.4744

## Interpretation

- This is a small deployment validation, not a full-scale final reviewer result.
- The result should be compared against the deterministic rubric-agent baseline before expanding to all 50 papers.
- Generated weaknesses are immediately passed through local retrieval and silver verifier diagnostics so unsupported comments are visible.
