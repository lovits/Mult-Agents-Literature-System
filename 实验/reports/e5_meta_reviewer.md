# E5 Meta-Reviewer Ranker

## Protocol

- Gold labels are used only for metrics.
- Candidate severity is not read from gold-derived smoke traces.
- Covered/refuted Gold is not claimed.

## Dataset

- Evaluated candidates: 155
- Paper groups: 54
- Gold keep candidates: 94

## Metrics

| System | Top-K Agreement Precision | Keep Coverage@K | High-Agreement Coverage@K | Redundancy Rate | Confidence Brier |
|---|---:|---:|---:|---:|---:|
| R0_input_order | 0.6543 | 0.8298 | 0.8298 | 0.0000 | 0.6003 |
| R1_text_severity | 0.6543 | 0.8298 | 0.8298 | 0.0000 | 0.2400 |
| R2_text_dedup | 0.6543 | 0.8298 | 0.8298 | 0.0000 | 0.2400 |
| R3_evidence_aware | 0.6543 | 0.8298 | 0.8298 | 0.0000 | 0.2515 |

## Interpretation

R3_evidence_aware combines text severity, audit decisions, support/refutation strength, SubstanReview substantiation prior, and the E3 controlled Literature-RAG boundary. It is evaluated as a ranking component, not as an accept/reject classifier.
