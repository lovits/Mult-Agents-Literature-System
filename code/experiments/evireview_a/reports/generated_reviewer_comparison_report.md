# Generated Reviewer Fair Comparison

This report compares the deterministic rubric-agent and GLM-4.6V reviewer on the exact paper overlap where GLM output is available.

## Scope

- Overlap papers: 8
- Human weaknesses in overlap: 229
- Warning: this is a small paired diagnostic, not a final provider benchmark.

## Paired Metrics

| Metric | Rubric-agent | GLM-4.6V reviewer |
| --- | ---: | ---: |
| Generated weaknesses | 30 | 21 |
| Mean generated per paper | 3.75 | 2.625 |
| Generic rate | 0.2 | 0.0952 |
| Redundancy rate | 0.1333 | 0.0 |
| Coverage recall @ 0.18 | 0.4148 | 0.5677 |
| Mean paper recall @ 0.18 | 0.4303 | 0.5725 |
| Mean support score | 0.2079 | 0.4744 |
| Partially-supported-or-better rate | 0.0 | 0.5714 |

## Verifier Label Counts

- Rubric-agent: {'Mentioned but Not Problem': 14, 'Unsupported': 16}
- GLM-4.6V reviewer: {'Mentioned but Not Problem': 6, 'Partially Supported': 10, 'Unsupported': 3, 'Supported': 2}

## Interpretation

- On this 8-paper overlap, GLM-4.6V produces fewer but more supported weaknesses than the deterministic rubric-agent.
- Rubric-agent remains useful as a cheap structure-risk generator, but its overlap-sample support score is much lower.
- The current 8-paper effective sample is a stronger diagnostic than the initial deployment sample, but still not a final provider benchmark.
