# Generated Reviewer Fair Comparison

This report compares all available reviewer generators on their exact common paper overlap.

## Scope

- Overlap papers: 5
- Human weaknesses in overlap: 151
- Warning: this is a small paired diagnostic, not a final provider benchmark.

## Paired Metrics

| Metric | Rubric-agent | GLM-4.6V reviewer | MiniMax-M2.7 reviewer |
| --- | ---: | ---: | ---: |
| Generated weaknesses | 20 | 12 | 15 |
| Mean generated per paper | 4.0 | 2.4 | 3.0 |
| Generic rate | 0.15 | 0.0833 | 0.0667 |
| Redundancy rate | 0.1316 | 0.0 | 0.0 |
| Coverage recall @ 0.18 | 0.4437 | 0.5232 | 0.5232 |
| Mean paper recall @ 0.18 | 0.4483 | 0.53 | 0.5421 |
| Mean support score | 0.2061 | 0.3751 | 0.467 |
| Partially-supported-or-better rate | 0.0 | 0.3333 | 0.4667 |

## Verifier Label Counts

- Rubric-agent: {'Mentioned but Not Problem': 10, 'Unsupported': 10}
- GLM-4.6V reviewer: {'Mentioned but Not Problem': 6, 'Partially Supported': 4, 'Unsupported': 2}
- MiniMax-M2.7 reviewer: {'Partially Supported': 5, 'Mentioned but Not Problem': 7, 'Supported': 2, 'Unsupported': 1}

## Interpretation

- The 5-paper common overlap enables a paired diagnostic without paper-selection differences.
- This remains a small provider diagnostic and must not be interpreted as a final model ranking.
