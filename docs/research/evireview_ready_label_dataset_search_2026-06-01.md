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
| A | PeerReview Bench | `correctness` / `significance` / `evidence` expert annotations | Evidence verifier、evidence-aware ranker、review-quality baseline | 已接入并跑 300-row baseline |
| A | PeerQA-XT | full paper、peer-review-derived question、answer | Paper-RAG retrieval QA | 下一步接入 |
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

PeerReview Bench 当前 300-row probe：

| Task | Train | Test | Majority Macro-F1 | NB Macro-F1 | NB Accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| correctness | 240 | 60 | 0.4643 | 0.4643 | 0.8667 |
| significance | 214 | 54 | 0.2622 | 0.4935 | 0.7593 |
| evidence | 199 | 50 | 0.4898 | 0.4898 | 0.9600 |

解释：

- `significance` 能直接支撑 evidence-aware ranker 的优先级实验，NB 明显强于 majority。
- `correctness` 和 `evidence` 在 300-row 小样本里类别不均衡，accuracy 高但 Macro-F1 不高；后续必须报告 Macro-F1、per-label recall 和 label distribution。
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

1. 将 PeerReview Bench 从 300-row probe 扩展到完整 3,881 expert annotations，复跑三类标签的 Macro-F1 和 per-label recall。
2. PeerQA-XT 已完成 question-only BM25 / TF-IDF / hybrid baseline，并加入 lightweight section-aware / hierarchical retrieval；当前结构先验没有超过 question-only floor，下一步应改成 domain-aware section mapping 或 query decomposition。
3. 把 PeerReview Bench 的 `significance` 标签并入 evidence-aware ranker 设计，验证它是否比纯 lexical score 更适合排序。
4. RottenReviews / ReviewBench / PeerCheck 只在 A 版核心链路稳定后作为补充，不抢主实验。
5. 本地 300 条 retrieval comparison queue 保留为最终系统特定人工 gold，对外部数据集不能覆盖的“论文内证据块选择”做补充。

## 6. PeerQA-XT 已完成 baseline

当前 80-row test probe：

| Method | Hit@1 | Hit@3 | Hit@5 | Mean answer recall@5 |
| --- | ---: | ---: | ---: | ---: |
| bm25_question | 0.2750 | 0.6500 | 0.8625 | 0.5248 |
| tfidf_question | 0.2500 | 0.7000 | 0.8000 | 0.5216 |
| hybrid_question | 0.2625 | 0.6750 | 0.8375 | 0.5232 |
| section_aware_question | 0.2625 | 0.6750 | 0.8375 | 0.5236 |
| hierarchical_question | 0.2500 | 0.6750 | 0.8375 | 0.5237 |
| oracle_answer_query | 0.5000 | 0.9125 | 0.9750 | 0.6337 |

该结果说明 PeerQA-XT 可以直接支撑 Paper-RAG 检索实验，但因为它没有 gold evidence span，当前指标仍是 answer-token support proxy。正式论文中应把它写成“外部检索 QA 诊断集”，不能替代本地 weakness-evidence gold labels。当前 lightweight section-aware / hierarchical variants 没有超过 question-only floor，因此这一结果也提示：section prior 必须针对数据集领域和论文结构重新设计，不能机械迁移。
