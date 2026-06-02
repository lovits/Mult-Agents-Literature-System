# Generated Reviewer Fair Comparison

This report compares the deterministic rubric-agent and GLM-4.6V reviewer on the exact paper overlap where GLM output is available.

## Scope

- Overlap papers: 10
- Human weaknesses in overlap: 289
- Warning: this is a small paired diagnostic, not a final provider benchmark.

## Paired Metrics

| Metric | Rubric-agent | GLM-4.6V reviewer |
| --- | ---: | ---: |
| Generated weaknesses | 34 | 27 |
| Mean generated per paper | 3.4 | 2.7 |
| Generic rate | 0.2059 | 0.1111 |
| Redundancy rate | 0.1373 | 0.0 |
| Coverage recall @ 0.18 | 0.3875 | 0.5952 |
| Mean paper recall @ 0.18 | 0.4072 | 0.5968 |
| Mean support score | 0.2 | 0.467 |
| Partially-supported-or-better rate | 0.0 | 0.5556 |

## Verifier Label Counts

- Rubric-agent: {'Mentioned but Not Problem': 15, 'Unsupported': 19}
- GLM-4.6V reviewer: {'Mentioned but Not Problem': 9, 'Partially Supported': 13, 'Unsupported': 3, 'Supported': 2}

## Interpretation

- On this 10-paper overlap, GLM-4.6V produces fewer but more supported weaknesses than the deterministic rubric-agent.
- Rubric-agent remains useful as a cheap structure-risk generator, but its overlap-sample support score is much lower.
- The current clean 10-paper effective sample is stronger than the initial deployment sample, but still not a final provider benchmark.
