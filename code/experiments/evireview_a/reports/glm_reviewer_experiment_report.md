# GLM-4.6V Structured Reviewer Experiment

This report validates a GLM-4.6V structured reviewer deployment on the local OpenReview/PRISM sample.

## Setup

- Status: `ok`
- Model: `glm-4.6v`
- Endpoint: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- Selected papers: 3
- Generated weaknesses: 8
- Papers with generation: 3
- Elapsed seconds: 93.53
- Warning: Small GLM-4.6V reviewer deployment sample; API key is never written to disk.

## Coverage Proxy

- Generic rate: 0.125

| Similarity threshold | Evaluated human weaknesses | Covered | Recall |
| ---: | ---: | ---: | ---: |
| 0.12 | 107 | 83 | 0.7757 |
| 0.18 | 107 | 54 | 0.5047 |
| 0.24 | 107 | 14 | 0.1308 |

## Verifier Handoff

- Retrieved generated weaknesses: 8
- Verified generated weaknesses: 8
- Label counts: {'Mentioned but Not Problem': 4, 'Partially Supported': 2, 'Unsupported': 2}
- Mean support score: 0.3448

## Interpretation

- This is a small deployment validation, not a full-scale final reviewer result.
- The result should be compared against the deterministic rubric-agent baseline before expanding to all 50 papers.
- Generated weaknesses are immediately passed through local retrieval and silver verifier diagnostics so unsupported comments are visible.
