# Rubric-agent Weakness Generation Baseline

This report evaluates a deterministic rubric-guided reviewer baseline before running expensive or rate-limited LLM review generation.

## Generation Setup

- Generator: `rubric_agent_v0`
- Papers: 50
- Generated weaknesses: 194
- Mean generated per paper: 3.88
- Category counts: {'related_work': 35, 'limitation': 36, 'experiment': 55, 'reproducibility': 12, 'method': 56}
- Severity counts: {'major': 146, 'minor': 48}
- Warning: This is a deterministic rubric-agent baseline for pipeline validation; it is not a final LLM reviewer.

## Coverage Proxy

- Human weaknesses: 1463
- Generic rate: 0.1804
- Redundancy rate: 0.1531
- Coverage warning: Lexical/character overlap is a weak proxy for semantic coverage; use this as a pipeline baseline before LLM pairwise judging or human review.

| Similarity threshold | Human weakness recall | Mean paper recall | Covered / Total |
| ---: | ---: | ---: | ---: |
| 0.12 | 0.8243 | 0.8331 | 1206 / 1463 |
| 0.18 | 0.4805 | 0.4798 | 703 / 1463 |
| 0.24 | 0.0834 | 0.0844 | 122 / 1463 |

## Top Lexical Matches

| Paper | Human weakness | Generated weakness | Similarity | Human category | Generated category |
| --- | --- | --- | ---: | --- | --- |
| SyuQKk7sX2 | 048_r4_weaknesses_021 | SyuQKk7sX2_rubric_agent_v0_04 | 0.3393 | experiment | reproducibility |
| b2XfOm3RJa | 020_r1_weaknesses_001 | b2XfOm3RJa_rubric_agent_v0_05 | 0.3238 | other | method |
| SyuQKk7sX2 | 048_r2_weaknesses_010 | SyuQKk7sX2_rubric_agent_v0_05 | 0.3234 | related_work | method |
| EmQSOi1X2f | 003_r2_weaknesses_006 | EmQSOi1X2f_rubric_agent_v0_03 | 0.3079 | method | method |
| 8JCn0kmS8W | 017_r3_weaknesses_021 | 8JCn0kmS8W_rubric_agent_v0_01 | 0.3071 | method | experiment |
| clU5xWyItb | 015_r4_questions_029 | clU5xWyItb_rubric_agent_v0_01 | 0.3029 | related_work | method |
| FQepisCUWu | 010_r3_questions_018 | FQepisCUWu_rubric_agent_v0_03 | 0.2925 | experiment | reproducibility |
| v6a1pXXADC | 044_r3_questions_036 | v6a1pXXADC_rubric_agent_v0_03 | 0.2922 | related_work | method |

## Retrieval Handoff

- Retriever: `rubric_section_aware_lexical_v0`
- Generated weaknesses with retrieval: 194 / 194
- Top-1 section-prior hit rate: 1.0
- Warning: Retrieval is for deterministic generated weakness pipeline validation; evidence support still needs verifier evaluation.

## Interpretation

- This baseline validates the generation interface and creates structured candidate weaknesses for downstream retrieval, verifier, ranker, and classification experiments.
- The overlap-based recall is expected to be conservative because generated rubric critiques are templated while human reviewer weaknesses are more specific.
- The next generation experiment should replace or augment this deterministic baseline with an OpenRouter free-model structured reviewer on a small paper subset.
