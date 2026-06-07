# Agent-RAG 论文评审评估与创新点更新

日期：2026-06-07

## 研究结论

近期工作共同表明，自动论文评审不能只评价生成文本或最终评分，还应分别评估检索、证据充分性、规划和排序。

- ReviewRL 将科学文献检索与复合质量评价结合。
- SciCompanion 使用图结构和多跳推理，并评价 retrieval accuracy、semantic overlap 与 multi-hop sensitivity。
- CLAIMCHECK 将科学评审转化为 claim-grounded reviewing tasks。
- SubstanReview 将 substantiation 定义为评审主张是否得到充分证据支持。
- PRISM（2026）不再用单一文本相似度评价 reviewer，而是分别评价分析深度、新颖性判断、缺陷识别与优先级、建设性，并结合 argument mining、retrieval-augmented verification 和 consensus scoring。
- Mind the Blind Spots 使用 `target × aspect` 的 focus-level 分布比较 LLM 与人工评审，说明总体分数会掩盖 reviewer 的结构性盲区。
- LLM-as-a-Reviewer 与 Breaking the Reviewer 表明自动评审必须单独评价 prompt injection 和文本对抗鲁棒性。
- Stop Automating Peer Review Without Rigorous Evaluation 报告 AI reviewer 存在跨论文和论文内的过度一致性，即 `hivemind effect`；因此 reviewer 评估需要把观点多样性与重复率作为独立维度。
- ReviewEval 将与人工评价对齐、事实准确性、分析深度、建设性和 guideline adherence 分开评价，进一步支持多维验收而非单一生成质量分数。

## 更新后的创新点

1. **Evidence-gated review audit**：候选弱点先检索论文内证据，再由独立 verifier 判断支持充分性，最后排序。
2. **Auditable Agent-RAG configuration**：Query Planner、Retriever、Verifier、Ranker 使用显式配置与 agent trace，可独立消融。
3. **Boundary-aware evaluation**：统一区分 gold、silver、proxy、diagnostic。
4. **Failure-preserving optimization**：实验未提升时保留负结果，用于决定默认组件和后续方向。
5. **Focus-aware reviewer coverage**：按 `paper target × review aspect` 输出覆盖矩阵，避免把生成数量或总体相似度误当作全面评审。
6. **Adversarially bounded paper processing**：将论文正文视为不可信数据，provider prompt 与 Paper-RAG 节点不得执行正文中的指令，并单独记录鲁棒性实验。
7. **Evidence-aware intra-paper deduplication**：只在同一论文和同一评审类别内合并高度重复的候选，并优先保留证据支持和严重度综合分数更高的候选；禁止用跨论文模板相似度删除具体论文的弱点。

## 架构决策

- 在检索前增加独立 `plan_weakness_queries` 节点。
- Query Planner 与 Retriever 必须能够分别选择和追踪。
- 默认 planner 只有在 ready-label 实验中优于 direct query 后才允许切换。
- Verifier 继续作为独立节点，后续使用 CLAIMCHECK / SubstanReview 验证更强模型。
- Provider 生成必须是显式可选组件，生成结果必须继续经过检索、verifier 与 ranker，不能绕过 evidence gate。
- 后续 verifier 评估增加校准、少数类 F1 和 evaluator agreement；最终 reviewer 评估增加 focus coverage 与 adversarial robustness。
- TreeReview 的动态问题树适合作为未来 planner 候选，但当前 category-expansion planner 在 CLAIMCHECK 上没有提升，因此不能直接替换默认 direct planner。
- 在 verifier 与 ranker 之间增加可审计 `deduplicate_weaknesses` 节点。Rubric-agent silver 消融将 194 条候选压缩为 172 条，减少 11.34%，而 partial-or-better rate 基本保持；该结果只证明减少模板重复，不证明提高 human-gold review quality。
- 原有全局 redundancy proxy 会混入跨论文模板相似，因此后续只报告论文内重复率，并将 focus diversity 与 evidence groundedness 分开评价。
- Qdrant/Hybrid 已从离线适配器升级为 Worker 可选择组件，但组件是否成为默认值仍由 ready-label 指标决定；当前 dense Hit@3 高于 native RRF hybrid，说明“采用向量库”与“检索质量提升”必须分开验收。
- 辅助 evidence-risk classification 已进入后端但真实 decision 标签 Macro-F1 仅为 `0.4007`，低于 metadata baseline `0.68`；因此论文创新点应聚焦 evidence-gated audit、可审计组件消融、论文内去重与鲁棒性，而不是 accept/reject 分类。

## 来源

- ReviewRL, EMNLP 2025: https://aclanthology.org/2025.emnlp-main.857/
- SciCompanion, Findings of EMNLP 2025: https://aclanthology.org/2025.findings-emnlp.1315/
- CLAIMCHECK, Findings of EMNLP 2025: https://aclanthology.org/2025.findings-emnlp.1185/
- Automatic Analysis of Substantiation in Scientific Peer Reviews, Findings of EMNLP 2023: https://aclanthology.org/2023.findings-emnlp.684/
- PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers, arXiv 2026: https://arxiv.org/abs/2605.26730
- LLM-as-a-Reviewer: Benchmarking Their Ability, Divergence, and Prompt Injection Resistance as Paper Reviewers, arXiv 2026: https://arxiv.org/abs/2605.25415
- Mind the Blind Spots: A Focus-Level Evaluation Framework for LLM Reviews, EMNLP 2025: https://aclanthology.org/2025.emnlp-main.1805/
- TreeReview: A Dynamic Tree of Questions Framework for Deep and Efficient LLM-based Scientific Peer Review, EMNLP 2025: https://aclanthology.org/2025.emnlp-main.790/
- Breaking the Reviewer: Assessing the Vulnerability of Large Language Models in Automated Peer Review Under Textual Adversarial Attacks, Findings of EMNLP 2025: https://aclanthology.org/2025.findings-emnlp.259/
- ReviewEval: An Evaluation Framework for AI-Generated Reviews, Findings of EMNLP 2025: https://aclanthology.org/2025.findings-emnlp.1120/
- Stop Automating Peer Review Without Rigorous Evaluation, ICML 2026 Position Paper: https://arxiv.org/abs/2605.03202
