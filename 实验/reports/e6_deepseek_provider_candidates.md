# E6 Provider Candidate Failure-Slice Comparison

## Protocol

- Status: `completed`
- Model: `deepseek-v4-flash-free`
- Selection: `e6_candidate_diagnostics_failure_cases`
- Prompt boundary: `paper_metadata_and_b3_candidates_only_no_official_reviews`
- Gold usage: `offline_proxy_evaluation_only`
- Accept/reject decision: disabled

## Dataset

- Selected papers: 8
- OpenReview reviews in selected papers: 33

## System Metrics

| System | Proxy Overlap@K | Trace Coverage | Top-K Compliance | Zero Overlap Rate | Review Leakage Free |
|---|---:|---:|---:|---:|---:|
| B2_failure_slice | 0.0639 | 1.0000 | 1.0000 | 0.0000 | True |
| B3_failure_slice | 0.0483 | 1.0000 | 1.0000 | 0.0417 | True |
| P1_provider_generated_failure_slice | 0.0000 | 0.0000 | 1.0000 | 0.0000 | True |

## Comparison

- P1 minus B3 proxy delta: -0.0483
- P1 minus B2 proxy delta: -0.0639
- P1 improved over B3 papers: 0

## Integrity

- Provider failures: 8
- Evidence attribution accuracy: 1.0000
- Invalid citations: 0
