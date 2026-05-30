# Weakness-Evidence Annotation Guideline

Purpose: label whether a review weakness is supported by the paper evidence retrieved from the same paper.

Do not judge whether the paper should be accepted. Judge only the relation between the weakness statement and the provided evidence blocks.

## Labels

| Label | Definition |
| --- | --- |
| Supported | The evidence clearly supports the weakness. |
| Partially Supported | The evidence is related and supports part of the weakness, but the full criticism needs extra judgment. |
| Mentioned but Not Problem | The paper mentions the topic, but the evidence does not establish it as a weakness. |
| Generic / Vague | The weakness is too broad, generic, or underspecified to verify. |
| Unsupported | The retrieved evidence does not support the weakness. |
| Contradicted | The evidence says the opposite of the weakness. |

## Annotation Rules

1. Prefer concrete evidence over general impression.
2. If a weakness says "missing X", evidence can be either a clear absence in the relevant section or a limitation statement admitting X.
3. If a weakness needs external related-work comparison, label `Partially Supported` and mention that literature evidence is required.
4. If a weakness only says "experiments are insufficient" without specifying what is missing, label `Generic / Vague`.
5. If the retrieved block explicitly shows the paper did what the weakness says it did not do, label `Contradicted`.
6. If none of the top-5 evidence blocks are useful, label `Unsupported`.

## Required Fields

- `gold_label`
- `gold_evidence_block_ids`
- `annotator_rationale`
- `annotator_confidence`

Confidence values:

- `high`
- `medium`
- `low`

