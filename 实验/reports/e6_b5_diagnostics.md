# E6 B5 Balanced Agent-RAG Diagnostics

## Protocol

- Source experiment: `e6-end-to-end-structured-report-v1`
- Gold usage: `diagnostic_only_official_review_weakness_proxy`
- Accept/reject decision: disabled

## Dataset

- OpenReview papers: 30
- OpenReview official reviews: 122

## System Summary

| System | Overall Proxy Overlap@K | Zero Overlap Rate | Paper Mean | Paper Median | Support Mean | Refutation Mean |
|---|---:|---:|---:|---:|---:|---:|
| B3_cue_aware_structured_report | 0.0549 | 0.0222 | 0.0549 | 0.0556 | 0.0000 | 0.0000 |
| B4_agent_rag_pipeline_report | 0.0559 | 0.0333 | 0.0559 | 0.0563 | 0.4430 | 0.4258 |
| B5_balanced_agent_rag_pipeline_report | 0.0570 | 0.0333 | 0.0570 | 0.0541 | 0.4446 | 0.4267 |

## B5 Comparisons

- B5 minus B4 mean delta: 0.0011
- B5 improved/tied/regressed vs B4: 7/21/2
- B5 minus B3 mean delta: 0.0021
- B5 improved/tied/regressed vs B3: 17/2/11

## Aspect Bottlenecks

| Aspect | Count | Proxy Overlap@K |
|---|---:|---:|
| related_work | 1 | 0.0370 |
| experiment | 26 | 0.0510 |
| reproducibility | 19 | 0.0576 |
| missing_baseline | 17 | 0.0592 |
| method | 27 | 0.0617 |

## Low-Overlap B5 Cases

- `GdXI5zCoAt` B5=0.0284, support=0.5297, refutation=0.4178, aspects=['reproducibility', 'missing_baseline', 'experiment']: RaSA: Rank-Sharing Low-Rank Adaptation
- `sb1HgVDLjN` B5=0.0336, support=0.6772, refutation=0.7063, aspects=['missing_baseline', 'reproducibility', 'experiment']: Offline Model-Based Optimization by Learning to Rank
- `r1KcapkzCt` B5=0.0363, support=0.5556, refutation=0.5334, aspects=['experiment', 'method', 'reproducibility']: Monte Carlo Planning with Large Language Model for Text-Based Game Agents
- `O6znYvxC1U` B5=0.0407, support=0.4558, refutation=0.3735, aspects=['experiment', 'reproducibility', 'method']: Bayesian Treatment of the Spectrum of the Empirical Kernel in (Sub)Linear-Width Neural Networks
- `yRKelogz5i` B5=0.0420, support=0.4032, refutation=0.3419, aspects=['method', 'experiment', 'missing_baseline']: Causally Motivated Sycophancy Mitigation for Large Language Models
- `TbTJJNjumY` B5=0.0432, support=0.5759, refutation=0.4455, aspects=['experiment', 'method', 'missing_baseline']: Boosting Neural Combinatorial Optimization for Large-Scale Vehicle Routing Problems
- `wVTJRnZ11Z` B5=0.0439, support=0.3347, refutation=0.3008, aspects=['experiment', 'reproducibility', 'method']: When GNNs meet symmetry in ILPs: an orbit-based feature augmentation approach
- `PwxYoMvmvy` B5=0.0440, support=0.4463, refutation=0.4678, aspects=['experiment', 'reproducibility', 'missing_baseline']: Beyond Random Masking: When Dropout meets Graph Convolutional Networks

## B5 Regressions vs B4

- `l11DZY5Nxu` delta=-0.0104, B4=0.0630, B5=0.0526: Robust Root Cause Diagnosis using In-Distribution Interventions
- `PwxYoMvmvy` delta=-0.0041, B4=0.0481, B5=0.0440: Beyond Random Masking: When Dropout meets Graph Convolutional Networks

## Next Optimization Hints

- Inspect B5 low-overlap aspect slices first: related_work, experiment.
- Compare B5 regressions against B4 selected aspects before changing candidate templates.
- For zero-overlap B5 items, require candidate weaknesses to include at least one paper-local cue or literature cue.
- Keep the next optimization bounded: change candidate filtering or aspect-specific query planning, not provider prompts.
