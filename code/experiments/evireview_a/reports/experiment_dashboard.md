# EviReview-Lite Experiment Dashboard

This dashboard aggregates the current A-version experiment state across dataset audit, retrieval, verification, ranking, generation, and auxiliary classification.

## Environment

- OpenRouter API key: `missing`
- GLM/Zhipu API key: `missing`; accepted env names: `GLM_API_KEY, ZHIPU_API_KEY, ZHIPUAI_API_KEY, BIGMODEL_API_KEY, ZAI_API_KEY`.
- Raw CLAIMCHECK row-level text policy: do not commit raw text because no upstream LICENSE was detected.
- Local OpenReview/PRISM sample remains the end-to-end application dataset.

## Module Metrics

| Module | Dataset | Primary metric | Result | Status | Note |
| --- | --- | --- | ---: | --- | --- |
| Source audit | Local OpenReview/PRISM | Matched papers | 50 / 50 | done | OpenReview source chain validated. |
| Human weakness extraction | Local OpenReview/PRISM | Weakness items | 1463 | done | Human-review upper-bound source for generation coverage. |
| Evidence blocks | Local OpenReview/PRISM | Blocks | 2597 | done | Paper-RAG substrate. |
| Section-aware retrieval | Local OpenReview/PRISM | Top-3 section alignment | 0.8618 | done | Best local retrieval proxy so far. |
| Substantiation verifier floor | SubstanReview | Naive Bayes Macro-F1 | 0.6411 | done | Licensed supervised review-internal substantiation baseline. |
| Ready dataset search | External datasets | Reachable candidates | 7 | ok | Prioritizes no-new-manual-label datasets aligned with the opening report. |
| PeerReview Bench baseline | PeerReview Bench | Significance NB Macro-F1 | 0.4207 | ok | 3881 rows; balanced evidence context Macro-F1 0.5318. |
| Paper-RAG QA retrieval | PeerQA-XT | section_aware_question Hit@3 | 0.606 | ok | 500 rows; section-aware Hit@3 0.606; oracle ceiling Hit@3 0.902. |
| Claim retrieval | CLAIMCHECK | OpenRouter embedding Hit@3 | 0.5 | done | Semantic retrieval improves over lexical baselines. |
| Groundedness verifier | CLAIMCHECK | Feature verifier Macro-F1 | 0.5076 | diagnostic | Verifier still weak, especially as final decision module. |
| Evidence-aware ranker | CLAIMCHECK | bm25_max_similarity MAP | 0.7771 | diagnostic | BM25 currently beats feature-verifier probability for ranking. |
| Auxiliary classifier | Local OpenReview/PRISM | metadata Macro-F1 | 0.68 | diagnostic | Classification remains auxiliary; metadata baseline is strongest. |
| Rubric-agent generation | Local OpenReview/PRISM | Coverage recall @ 0.18 | 0.4805 | pipeline baseline | Deterministic reviewer validates Agent -> RAG interface. |
| GLM-4.6V reviewer sample | Local OpenReview/PRISM | Coverage recall @ 0.18 | 0.5047 | ok | 8 generated; labels: {'Mentioned but Not Problem': 4, 'Partially Supported': 2, 'Unsupported': 2} |
| Paired reviewer comparison | GLM overlap papers | Coverage recall @ 0.18 | 0.5047 | diagnostic | GLM vs rubric: 0.5047 vs 0.3738 |
| Hierarchical Paper-RAG | Generated weaknesses | GLM mean support | 0.4411 | diagnostic | GLM partial+ 0.625; rubric support 0.1999 |
| Human hierarchical retrieval | Local OpenReview/PRISM | Top-1 section alignment | 0.9993 | diagnostic | 1463 human weaknesses; top tools {'semantic_search': 807, 'keyword_search': 567, 'section_read': 89} |
| Retrieval comparison queue | Human weaknesses | Selected annotation rows | 300 | ready | Top-1 disagreement 0.6138; Top-3 disagreement 0.9645 |
| Retrieval comparison gold | Human weaknesses | Gold rows | 0 | needs_labels | Evaluation status: blocked |
| Generated weakness verifier/ranker | Local OpenReview/PRISM | Generated weaknesses verified | 194 | pipeline baseline | Label counts: {'Unsupported': 121, 'Mentioned but Not Problem': 70, 'Partially Supported': 3} |

## Dataset Coverage

| Dataset | Current use | Evidence | Remaining gap |
| --- | --- | --- | --- |
| Local OpenReview/PRISM | End-to-end A-version dataset | 50 papers, 1463 human weakness items, 2597 evidence blocks | Human weakness-evidence gold labels still incomplete |
| SubstanReview | Supervised substantiation floor | Test Macro-F1 0.6411 | Review-internal evidence only, not full paper-grounding |
| PeerReview Bench | No-manual-label review-quality/verifier baseline | 3881 local rows from 3881 expert annotations; significance balanced review Macro-F1 0.4207; evidence balanced context Macro-F1 0.5318 | Labels remain imbalanced; minority recall is the main gap |
| PeerQA-XT | No-manual-label Paper-RAG QA retrieval | 500 local retrieval rows from 1252 test rows; best Hit@3 0.606 via section_aware_question | No gold evidence spans; current metric is answer-token support proxy |
| CLAIMCHECK | Paper-grounded critique benchmark | 155 main weaknesses; embedding Hit@3 0.5 | Raw row-level text not committed; verifier still weak |

## Current Risks

- OpenRouter chat reranker status: `blocked`; reason: OpenRouter HTTP error 429: Provider returned error; provider=Venice; retry_after_seconds=12.
- GLM-4.6V reviewer result is a 3-paper deployment sample, so it proves provider integration and pipeline handoff only.
- Paired GLM-vs-rubric comparison currently covers only the GLM overlap papers.
- Hierarchical Paper-RAG currently uses silver verifier labels; treat support gains as architecture diagnostics, not final truth.
- Human hierarchical retrieval has high section-alignment proxy scores, but true evidence support still needs the 300-row comparison queue to be labeled.
- Retrieval comparison gold status: `needs_labels`; current gold rows: 0.
- Generated rubric-agent weaknesses are mostly heuristic structure warnings; current verifier labels are mostly Unsupported / Mentioned.
- Local classification is exploratory: metadata baseline is stronger than evidence-proxy features.
- PeerReview Bench sample labels are imbalanced, so Macro-F1 is more important than accuracy.
- PeerQA-XT does not provide gold evidence spans; answer-support Hit@K is a retrieval proxy, not final evidence precision.
- CLAIMCHECK and local silver labels are diagnostics until human gold labels or licensed row-level benchmark evaluation are stronger.

## Next Experiments

1. Add context-aware PeerReview Bench features or an LLM verifier because full-data review-item NB still misses minority evidence labels.
2. Improve PeerQA-XT query decomposition using data-driven or LLM-generated subqueries; current hand-written expansion hurts retrieval while section-aware scoring only ties the best lexical floor.
3. Expand the GLM-4.6V structured-reviewer sample to 5-10 papers and compare it with rubric-agent on coverage, generic rate, redundancy, and verifier-label distribution.
4. Keep OpenRouter chat reranker/verifier as optional because the free provider is rate-limited.
5. Label the 300-row retrieval comparison queue only if external ready-label datasets still leave a gap in local Paper-RAG evidence support.
