# EviReview-Lite PeerQA-XT 500-row Progress Update

日期：2026-06-02

## 1. 本轮完成内容

本轮按照“先不做人工标注，优先使用可直接拿来实验的数据集”的路线，将 PeerQA-XT Paper-RAG QA retrieval probe 从 80 条扩展到 500 条，并将默认复跑规模固定为 500。

已完成：

- 将 `evaluate_peerqa_xt_retrieval.py` 的默认样本数从 80 改为 500。
- 使用 PeerQA-XT `test` split 中 500 / 1252 条样本复跑 Paper-RAG retrieval。
- 重新生成：
  - `peerqa_xt_retrieval_metrics.json`
  - `peerqa_xt_retrieval_predictions.jsonl`
  - `reports/peerqa_xt_retrieval_report.md`
  - `reports/experiment_dashboard.md`
- 同步更新 ready-label 数据集说明、技术设计文档和当前进度文档。

## 2. 使用方法

数据集：`UKPLab/PeerQA-XT`

数据来源：Hugging Face Dataset Viewer API

实验对象：peer-review-derived question 到 full paper chunks 的检索。

评估代理指标：PeerQA-XT 不提供 gold evidence span，因此当前使用 answer-token support proxy：

- Hit@1 / Hit@3 / Hit@5：top-k chunk 中是否有 chunk 覆盖足够答案关键词。
- Mean answer recall@5：top-5 chunks 对答案关键词的平均覆盖程度。
- `oracle_answer_query`：用 gold answer 作为 query 的诊断上界，不作为系统方法。

检索方法：

| 方法 | 说明 |
| --- | --- |
| BM25 | 词面检索基线 |
| TF-IDF | 稀疏向量检索基线 |
| Hybrid | BM25 + TF-IDF 融合 |
| Section-aware | 加入论文 section 结构先验 |
| Hierarchical | 融合 BM25、TF-IDF、section_read 风格排名 |
| Query decomposition | 静态规则子查询扩展 |
| Domain-aware | 加入 biomedical section/domain query expansion |
| Oracle answer query | 诊断上界 |

## 3. 当前 500-row 结果

| Method | Rows | Hit@1 | Hit@3 | Hit@5 | Mean answer recall@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| bm25_question | 500 | 0.2400 | 0.5980 | 0.7940 | 0.5001 |
| tfidf_question | 500 | 0.2300 | 0.5920 | 0.7740 | 0.4906 |
| hybrid_question | 500 | 0.2420 | 0.5960 | 0.7920 | 0.4988 |
| section_aware_question | 500 | 0.2460 | 0.6060 | 0.8060 | 0.5005 |
| hierarchical_question | 500 | 0.2220 | 0.5900 | 0.7880 | 0.4995 |
| query_decomposed_question | 500 | 0.2080 | 0.5320 | 0.7340 | 0.4751 |
| domain_section_aware_question | 500 | 0.2080 | 0.5360 | 0.7420 | 0.4774 |
| domain_hierarchical_question | 500 | 0.2140 | 0.5260 | 0.7340 | 0.4752 |
| oracle_answer_query | 500 | 0.4960 | 0.9020 | 0.9660 | 0.6257 |

## 4. 对开题报告实验计划的对齐

该结果支撑开题报告中的 Paper-RAG 证据检索实验线：

- 不依赖人工新增标注，满足当前阶段“直接拿来用的数据集”要求。
- 使用 full paper context，和本项目的论文内证据检索目标一致。
- 将 retrieval 独立成可诊断模块，避免把 reviewer generation、retrieval、verifier、ranker 混成一个不可解释端到端分数。
- 结果显示 section-aware 结构先验有稳定但有限的提升，因此创新点应写成“可审计的论文结构化检索流程”，不能夸大为显著性能突破。

## 5. 本轮实验结论

1. 500 条结果比 80 条 pilot 更适合写入论文实验章节。
2. `section_aware_question` 是当前最稳 non-oracle 方法，Hit@3 为 0.6060，Hit@5 为 0.8060。
3. `oracle_answer_query` Hit@3 为 0.9020，说明检索空间中存在足够支持信息，问题在于如何从 question 构造更好的 evidence-seeking query。
4. 手写 query decomposition 和 domain-aware expansion 明显下降，说明不能把“多查询/多工具”直接写成必然提升。
5. 下一步应把 query expansion 改成数据驱动或 LLM 生成，并通过同一 500-row PeerQA-XT probe 验证。

## 6. 仍未完成

- PeerQA-XT 仍没有 gold evidence spans，answer-token support 只能作为 retrieval proxy。
- 本地 OpenReview/PRISM 的 300 条 retrieval comparison queue 仍未人工标注，不能替代最终系统特定 evidence gold labels。
- PeerReview Bench evidence-aware feature baseline 已完成，evidence Macro-F1 从 0.5318 提升到 0.5730，但 `Requires More` recall 仍只有 0.2381，需要继续优化。
- GLM reviewer 扩样脚本已准备好默认 10 篇与续跑保护；当前小样本仍只有 3 篇，因为本轮环境未设置 GLM key。
- Hierarchical retrieval tools 还没有落成完整 LangGraph-style agent graph。

## 7. 下一步建议顺序

1. 基于 PeerQA-XT 500-row probe 尝试数据驱动/LLM 子查询生成，验证能否提高 Hit@1/Hit@3。
2. 在 PeerReview Bench 上继续做 LLM verifier 或更强特征，重点提升 `Requires More` recall。
3. 注入 `GLM_API_KEY` / `ZAI_API_KEY` 后扩 GLM reviewer 到 5-10 篇，复跑 generation -> retrieval -> verifier -> ranker。
4. 整理实验章节表格：数据集表、retrieval 表、verifier 表、ranker 表、消融实验表。
