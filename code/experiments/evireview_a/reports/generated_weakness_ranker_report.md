# Generated Weakness Evidence-aware Ranker

This report ranks generated review weaknesses after hierarchical Paper-RAG retrieval and silver verifier diagnostics.

## Method

- Ranker: `generated_weakness_evidence_aware_ranker_v0`
- Score formula: `(0.45 + support_score) * verifier_label_weight * severity_weight`
- Inputs: generated weakness severity, silver verifier label, and support score.
- Scope: diagnostic ranking only; labels are not human gold.

## Results

| Source | Candidates | Papers | Top-3 rows | Candidate mean support | Top-3 mean support | Candidate partial+ | Top-3 partial+ | Top-3 labels |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| glm_reviewer | 21 | 8 | 21 | 0.5304 | 0.5304 | 0.7143 | 0.7143 | {'Supported': 3, 'Partially Supported': 12, 'Mentioned but Not Problem': 4, 'Unsupported': 2} |
| rubric_agent | 194 | 49 | 141 | 0.1999 | 0.2343 | 0.0258 | 0.0355 | {'Unsupported': 64, 'Mentioned but Not Problem': 72, 'Partially Supported': 5} |

## Interpretation

- The ranker converts verifier evidence into an ordered shortlist per paper, which matches the thesis goal of auditable reviewer ranking.
- A useful diagnostic is whether Top-3 rows have higher mean support and higher partially-supported-or-better rate than all candidates.
- Because the verifier labels are silver rules, this should be reported as architecture evidence, not final human evaluation.
