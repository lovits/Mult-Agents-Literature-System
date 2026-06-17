# E6 Candidate Generation Diagnostics

## Protocol

- Source experiment: `e6-end-to-end-structured-report-v1`
- Gold usage: `diagnostic_only_official_review_weakness_proxy`
- Accept/reject decision: disabled

## Dataset

- OpenReview papers: 30
- OpenReview official reviews: 122

## System Summary

| System | Overall Proxy Overlap@K | Zero Overlap Rate | Paper Mean | Paper Median |
|---|---:|---:|---:|---:|
| B2_system_generated_structured_report | 0.0504 | 0.0556 | 0.0504 | 0.0497 |
| B3_cue_aware_structured_report | 0.0549 | 0.0222 | 0.0549 | 0.0556 |

## B3 vs B2 Paper-Level Comparison

- Mean delta: 0.0044
- Improved papers: 19
- Tied papers: 0
- Regressed papers: 11
- Failure-or-tie rate: 0.3667

## Aspect Distribution

### B2_system_generated_structured_report

| Aspect | Count | Proxy Overlap@K |
|---|---:|---:|
| experiment | 29 | 0.0459 |
| method | 8 | 0.0403 |
| missing_baseline | 29 | 0.0501 |
| novelty | 5 | 0.0565 |
| reproducibility | 19 | 0.0606 |

### B3_cue_aware_structured_report

| Aspect | Count | Proxy Overlap@K |
|---|---:|---:|
| experiment | 20 | 0.0477 |
| method | 23 | 0.0613 |
| missing_baseline | 16 | 0.0567 |
| novelty | 18 | 0.0479 |
| related_work | 3 | 0.0879 |
| reproducibility | 10 | 0.0543 |

## Failure Or Tie Cases

- `wVTJRnZ11Z` delta=-0.0244, B2=0.0584, B3=0.0341: When GNNs meet symmetry in ILPs: an orbit-based feature augmentation approach
- `5o9JJJPPm6` delta=-0.0201, B2=0.0654, B3=0.0453: ComaDICE: Offline Cooperative Multi-Agent Reinforcement Learning with Stationary Distribution Shift Regularization
- `h0vC0fm1q7` delta=-0.0164, B2=0.0679, B3=0.0515: Sensitivity Verification for Additive Decision Tree Ensembles
- `ONfWFluZBI` delta=-0.0146, B2=0.0899, B3=0.0753: Self-supervised contrastive learning performs non-linear system identification
- `r1KcapkzCt` delta=-0.0140, B2=0.0412, B3=0.0272: Monte Carlo Planning with Large Language Model for Text-Based Game Agents
- `GdXI5zCoAt` delta=-0.0133, B2=0.0525, B3=0.0392: RaSA: Rank-Sharing Low-Rank Adaptation
- `GM7cmQfk2F` delta=-0.0119, B2=0.0640, B3=0.0521: Rethinking Neural Multi-Objective Combinatorial Optimization via Neat Weight Embedding
- `Sd4wYYOhmY` delta=-0.0108, B2=0.0722, B3=0.0614: TabM: Advancing tabular deep learning with parameter-efficient ensembling

## Next Optimization Hints

- Inspect low-overlap B3 aspect `experiment` before adding more templates.
- Reduce zero-overlap candidates by requiring at least one paper-title or abstract cue in every Top-K item.
- Compare failure-case titles against B3 selected aspects before provider prompting; these cases define the first provider evaluation slice.
- Keep provider-generated candidates leakage-free: prompts may include paper metadata and retrieved paper evidence, not Official Review text.
