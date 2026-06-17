# E6 NeurIPS 2023 Stability Diagnostic

## Protocol

- Name: `e6-neurips-2023-stability-v1`
- Sample size: 50
- Top-K: 3
- Gold boundary: official review text is used only as a proxy, not strict weakness gold
- Accept/reject decision: False

## Dataset

- Papers: 50
- Reviews: 230
- Source: `dataset/processed/candidate_expansion_2026_06_17`

## Metrics

| System | Coverage | Trace Coverage | Top-K Compliance | Review Proxy Overlap@K | Aspect Diversity@K | Redundancy@K | Accept/Reject Decisions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| B2_system_generated_structured_report | 1.0000 | 1.0000 | 1.0000 | 0.0437 | 1.0000 | 0.0000 | 0 |
| B3_cue_aware_structured_report | 1.0000 | 1.0000 | 1.0000 | 0.0515 | 1.0000 | 0.0000 | 0 |
| B4_agent_rag_pipeline_report | 0.9400 | 1.0000 | 1.0000 | 0.0504 | 0.9220 | 0.0000 | 0 |
| B5_balanced_agent_rag_pipeline_report | 0.9400 | 1.0000 | 1.0000 | 0.0499 | 1.0000 | 0.0000 | 0 |

## Comparison

- B5 overlap delta vs B3: -0.001569
- B5 overlap delta vs B4: -0.000480
- B5 aspect diversity delta vs B4: 0.078014
- B5 redundancy delta vs B4: 0.000000
- Experiment verdict: `failed_with_metrics`

## Interpretation

This diagnostic tests whether the existing E6 Agent-RAG assembly remains stable when moved from the OpenReview seed to a 50-paper NeurIPS 2023 processed sample. The official review text is used only as a weak proxy for weakness overlap; it is not a strict human Gold weakness annotation.

No paper-level accept/reject decision is produced. The result should be used to guide the next engineering step, not as final thesis evidence.
