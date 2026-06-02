# EviReview-Lite 免人工标注数据集筛选报告

日期：2026-06-01

## 1. 筛选口径

本轮只保留能支撑开题报告实验内容的数据集，不把“论文评审相关”作为唯一标准。数据集必须至少满足一项实验用途：

1. Paper-RAG 检索：有论文正文、问题或评审条目，可直接评估检索是否找到相关证据。
2. Evidence Verifier：已有 correctness、evidence、substantiation、groundedness 或类似标签。
3. Evidence-aware Ranker：已有 significance、quality、priority 或 review-quality 标签。
4. Reviewer Agent 对比：有人工评审、LLM 评审或结构化评审结果，可比较生成质量。
5. 辅助分类或泛化：有 decision、score、conference、review 等结构化字段，但不作为主贡献。

因此，本轮不再把“本地 300 条人工标注队列”作为第一实验入口，而是先用已有标签的公开数据集跑出可复现 baseline；本地标注队列保留为系统特定补充验证。

## 2. 结论

| 优先级 | 数据集 | 已有监督信号 | 对齐实验 | 当前决策 |
| --- | --- | --- | --- | --- |
| A | PeerReview Bench | `correctness` / `significance` / `evidence` expert annotations | Evidence verifier、evidence-aware ranker、review-quality baseline | 已接入完整 3,881-row baseline |
| A | PeerQA-XT | full paper、peer-review-derived question、answer | Paper-RAG retrieval QA | 已接入，并完成多检索方法 baseline |
| B | RottenReviews | human review-quality annotations | review-quality / ranker supplement | B 版补充 |
| B | ReviewBench | papers、reviews、rebuttals、decisions、markdown | 多会议泛化、reviewer generation 对比 | B 版补充 |
| B | SPECS Review Benchmark | controlled injected flaw specs / detection | reviewer robustness、flaw detection | 鲁棒性实验 |
| B | PeerCheck | human vs LLM reviews | reviewer generation / alignment | B 版对比 |
| C | OpenReview Raw | large-scale OpenReview notes | 扩容、辅助分类 | 系统稳定后再用 |
| C | PRISM paper data | large OpenReview-derived paper/review corpus | 扩容、PRISM 相关工作对齐 | license 谨慎 |

## 3. 已落地实验：PeerReview Bench

当前已新增脚本：

- `code/experiments/evireview_a/src/probe_ready_datasets.py`
- `code/experiments/evireview_a/src/prepare_peerreview_bench.py`
- `code/experiments/evireview_a/src/evaluate_peerreview_bench_baseline.py`

PeerReview Bench 已接入完整 3,881 条 expert annotations，并采用按 `paper_id` 分组的 deterministic 80/20 split，避免同一论文泄漏到 train/test 两侧：

| Task | Train | Test | Majority Macro-F1 | Review NB Macro-F1 | Balanced Review NB Macro-F1 | Context NB Macro-F1 | Balanced Context NB Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| correctness | 3079 | 802 | 0.4646 | 0.4901 | 0.4846 | 0.5601 | 0.5686 |
| significance | 2720 | 696 | 0.2486 | 0.3723 | 0.4207 | 0.3241 | 0.3205 |
| evidence | 2266 | 602 | 0.4819 | 0.4819 | 0.4801 | 0.5153 | 0.5318 |

解释：

- `significance` 能直接支撑 evidence-aware ranker 的优先级实验，balanced review-item NB 明显强于 majority。
- `correctness` 和 `evidence` 在完整数据上仍类别不均衡，accuracy 高但 Macro-F1 不高；后续必须报告 Macro-F1、per-label recall 和 label distribution。
- balanced context NB 对 correctness/evidence 有帮助，但 `evidence` 的 `Requires More` minority recall 仍只有 0.0714，说明仅用朴素词袋上下文不足以完成 evidence verifier，需要引入 evidence-aware features 或 LLM verifier。
- 当前脚本只保存短 `paper_excerpt`，不保存完整 `paper_content`，避免把大型论文正文直接提交到仓库。

## 4. 与开题报告实验模块的对应关系

| 开题报告实验模块 | 当前可用数据 | 方法 | 论文写法 |
| --- | --- | --- | --- |
| Agent 生成候选弱点 | 本地 OpenReview/PRISM、PeerCheck、ReviewBench | rubric-agent / GLM reviewer 生成，和人工评审或 LLM 评审对比 | 生成不是最终判断，必须进入 verifier |
| Paper-RAG 证据检索 | 本地 OpenReview/PRISM、PeerQA-XT、CLAIMCHECK | section-aware retrieval、hierarchical tools、QA retrieval | 强调结构化论文内检索 |
| Evidence Verifier | PeerReview Bench、SubstanReview、CLAIMCHECK | majority / NB / feature fusion / LLM verifier | 评估 weakness 或 review item 是否有依据 |
| Evidence-aware Ranker | PeerReview Bench、RottenReviews、CLAIMCHECK | significance / evidence / quality label 排序 | 排序重点是高重要性且有证据的弱点 |
| 辅助 accept/reject 分类 | 本地 OpenReview/PRISM、PeerRead、ReviewBench | metadata、review/evidence features | 明确为辅助实验，不是主贡献 |

## 5. 下一步实验顺序

1. PeerReview Bench 已扩展到完整 3,881 expert annotations，并加入 context NB；下一步加入 evidence-aware features 或 LLM verifier，重点提升 minority recall。
2. PeerQA-XT 已扩展到 500-row question-only、section-aware、hierarchical 和 domain-aware query decomposition baseline；当前 section-aware 是最稳 non-oracle 方法，但只小幅超过 lexical floor，手写 query/domain expansion 下降，下一步应改成数据驱动/LLM 子查询。
3. 把 PeerReview Bench 的 `significance` 标签并入 evidence-aware ranker 设计，验证它是否比纯 lexical score 更适合排序。
4. RottenReviews / ReviewBench / PeerCheck 只在 A 版核心链路稳定后作为补充，不抢主实验。
5. 本地 300 条 retrieval comparison queue 保留为最终系统特定人工 gold，对外部数据集不能覆盖的“论文内证据块选择”做补充。

## 6. PeerQA-XT 已完成 baseline

当前 500-row test probe：

| Method | Hit@1 | Hit@3 | Hit@5 | Mean answer recall@5 |
| --- | ---: | ---: | ---: | ---: |
| bm25_question | 0.2400 | 0.5980 | 0.7940 | 0.5001 |
| tfidf_question | 0.2300 | 0.5920 | 0.7740 | 0.4906 |
| hybrid_question | 0.2420 | 0.5960 | 0.7920 | 0.4988 |
| section_aware_question | 0.2460 | 0.6060 | 0.8060 | 0.5005 |
| hierarchical_question | 0.2220 | 0.5900 | 0.7880 | 0.4995 |
| query_decomposed_question | 0.2080 | 0.5320 | 0.7340 | 0.4751 |
| domain_section_aware_question | 0.2080 | 0.5360 | 0.7420 | 0.4774 |
| domain_hierarchical_question | 0.2140 | 0.5260 | 0.7340 | 0.4752 |
| oracle_answer_query | 0.4960 | 0.9020 | 0.9660 | 0.6257 |

该结果说明 PeerQA-XT 可以直接支撑 Paper-RAG 检索实验，但因为它没有 gold evidence span，当前指标仍是 answer-token support proxy。正式论文中应把它写成“外部检索 QA 诊断集”，不能替代本地 weakness-evidence gold labels。扩展到 500 条后，section-aware rerank 是最稳 non-oracle 方法，但相对 BM25/Hybrid 只小幅提升；手写 query decomposition 和 domain-aware expansion 会伤害结果，因此不能把“多工具/多查询”直接写成必然提升，只能写成需要验证的 agentic retrieval 组件。
