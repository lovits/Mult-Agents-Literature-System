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
| Generated weakness verifier/ranker | Local OpenReview/PRISM | Generated weaknesses verified | 194 | pipeline baseline | Label counts: {'Unsupported': 121, 'Mentioned but Not Problem': 70, 'Partially Supported': 3} |

## Dataset Coverage

| Dataset | Current use | Evidence | Remaining gap |
| --- | --- | --- | --- |
| Local OpenReview/PRISM | End-to-end A-version dataset | 50 papers, 1463 human weakness items, 2597 evidence blocks | Human weakness-evidence gold labels still incomplete |
| SubstanReview | Supervised substantiation floor | Test Macro-F1 0.6411 | Review-internal evidence only, not full paper-grounding |
| CLAIMCHECK | Paper-grounded critique benchmark | 155 main weaknesses; embedding Hit@3 0.5 | Raw row-level text not committed; verifier still weak |

## Current Risks

- OpenRouter chat reranker status: `blocked`; reason: OpenRouter HTTP error 429: Provider returned error; provider=Venice; retry_after_seconds=12.
- GLM-4.6V reviewer result is a 3-paper deployment sample, so it proves provider integration and pipeline handoff only.
- Paired GLM-vs-rubric comparison currently covers only the GLM overlap papers.
- Hierarchical Paper-RAG currently uses silver verifier labels; treat support gains as architecture diagnostics, not final truth.
- Human hierarchical retrieval has high section-alignment proxy scores, but true evidence support still needs the 300-row comparison queue to be labeled.
- Generated rubric-agent weaknesses are mostly heuristic structure warnings; current verifier labels are mostly Unsupported / Mentioned.
- Local classification is exploratory: metadata baseline is stronger than evidence-proxy features.
- CLAIMCHECK and local silver labels are diagnostics until human gold labels or licensed row-level benchmark evaluation are stronger.

## Next Experiments

1. Expand the GLM-4.6V structured-reviewer sample to 5-10 papers and compare it with rubric-agent on coverage, generic rate, redundancy, and verifier-label distribution.
2. Keep OpenRouter chat reranker/verifier as optional because the free provider is rate-limited.
3. Label the 300-row retrieval comparison queue to decide whether section-aware or hierarchical retrieval is better for human reviewer weaknesses.
4. Expand local human gold weakness-evidence labels from pilot toward 200-300 usable rows.
5. Use generated + verified weaknesses as features in the auxiliary classifier only after generated evidence support improves over metadata baseline.
