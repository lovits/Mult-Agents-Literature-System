# Agent-RAG 论文评审评估与创新点更新

日期：2026-06-07

## 研究结论

近期工作共同表明，自动论文评审不能只评价生成文本或最终评分，还应分别评估检索、证据充分性、规划和排序。

- ReviewRL 将科学文献检索与复合质量评价结合。
- SciCompanion 使用图结构和多跳推理，并评价 retrieval accuracy、semantic overlap 与 multi-hop sensitivity。
- CLAIMCHECK 将科学评审转化为 claim-grounded reviewing tasks。
- SubstanReview 将 substantiation 定义为评审主张是否得到充分证据支持。

## 更新后的创新点

1. **Evidence-gated review audit**：候选弱点先检索论文内证据，再由独立 verifier 判断支持充分性，最后排序。
2. **Auditable Agent-RAG configuration**：Query Planner、Retriever、Verifier、Ranker 使用显式配置与 agent trace，可独立消融。
3. **Boundary-aware evaluation**：统一区分 gold、silver、proxy、diagnostic。
4. **Failure-preserving optimization**：实验未提升时保留负结果，用于决定默认组件和后续方向。

## 架构决策

- 在检索前增加独立 `plan_weakness_queries` 节点。
- Query Planner 与 Retriever 必须能够分别选择和追踪。
- 默认 planner 只有在 ready-label 实验中优于 direct query 后才允许切换。
- Verifier 继续作为独立节点，后续使用 CLAIMCHECK / SubstanReview 验证更强模型。

## 来源

- ReviewRL, EMNLP 2025: https://aclanthology.org/2025.emnlp-main.857/
- SciCompanion, Findings of EMNLP 2025: https://aclanthology.org/2025.findings-emnlp.1315/
- CLAIMCHECK, Findings of EMNLP 2025: https://aclanthology.org/2025.findings-emnlp.1185/
- Automatic Analysis of Substantiation in Scientific Peer Reviews, Findings of EMNLP 2023: https://aclanthology.org/2023.findings-emnlp.684/
