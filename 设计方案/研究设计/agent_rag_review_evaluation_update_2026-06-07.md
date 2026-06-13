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

## 2026-06-07 增量监测：Agentic RAG 与自动评审评估新方向

本轮网络检索与本地论文库交叉确认后，将新增论文分为两组：一组校正自动论文评审任务边界，一组校正 Agentic RAG 的中间过程评估方式。

| 论文/方向 | 年份 | 对 EviReview-Lite 的实验影响 | 对创新点表述的影响 |
| --- | --- | --- | --- |
| ReviewArena: Benchmarking LLMs' Judgement Ability in Academic Peer Review | 2025 | 自动评审 evaluation 需要单独看 judgement / preference，而不是只看生成文本。当前系统应把 review generation 与 evidence verification/ranking 分开报告。 | 强化“审稿辅助中的证据审计”，避免声称端到端替代 reviewer。 |
| PaperAudit-Bench: Benchmarking LLMs' Ability to Generate Feedback for Scientific Papers | 2025 | 反馈生成 benchmark 支持继续扩 provider comparison，但必须配合 groundedness / substantiation 指标，否则只是在比较语言流畅度。 | Provider 生成只是候选弱点来源，主贡献仍是 audit graph。 |
| LIMITGEN-Syn: Teasing Out LLM Opinion Bias in Synthetic Review Generation | 2025 | 生成式 reviewer 可能带 opinion bias，后续 provider paired comparison 应记录 generic rate、重复率、focus coverage，而不是只看数量。 | 支持“failure-preserving optimization”和“boundary-aware evaluation”。 |
| RAGCap-Bench: Benchmarking Capabilities of LLMs in Agentic RAG Systems | 2025/2026 | Agentic RAG 评估应拆分规划、检索、证据选择、回答/判断等中间能力；当前 graph trace 与 manifest component method 正好对应这种拆分。 | 强化“auditable Agent-RAG configuration”作为系统创新点。 |
| AgenticRAGTracer: Explainable Evaluation Framework for Agentic Retrieval-Augmented Generation | 2026 | 需要保存 agent trace 和组件级状态，不应只保存最终结果。当前 `agent_trace` 的 public-redacted 设计合理，后续可扩展 node latency / selected component。 | 强化可解释审计，而不是黑盒 RAG。 |
| CRAG: Comprehensive RAG Benchmark | 2024 | RAG 评测应覆盖多任务、多源和鲁棒性；当前论文内 RAG 仍是窄域，应明确限定在 paper-local evidence audit。 | 将 CLAIMCHECK/SubstanReview/PeerReview Bench 分层报告，避免泛化到通用 RAG。 |
| RAGChecker / GroUSE / RAG-Critic 类细粒度评估 | 2024-2025 | 指标应区分 retriever、verifier、ranker 与 generator，且给出错误类型。当前统一 metric boundary 与 comparison export 可以直接承载这一点。 | 强化 gold/silver/proxy/diagnostic 边界。 |

本轮对实验计划的直接调整：

1. 后端 manifest 指标导出需要支持跨 manifest comparison，以便把 `full/no_verifier/no_ranker/no_dedup/qdrant_sparse/qdrant_hybrid` 放在同一张表中。
2. 论文实验章节应先报告 ready-label retrieval/verifier/ranker 消融，再报告 provider 生成诊断；不要把 provider 生成结果作为主质量结论。
3. 后续真实 hosted provider 验收需要同时输出：success rate、weakness count、mean support、ranked finding count、supported / partial-or-better / unsupported / generic 比例、duplicate count、论文内去重率。
4. Agent trace 应作为系统可解释性证据进入架构章节，但公开 API 仍只能暴露 node/status/component/error type，不能暴露 provider 原始响应或论文原文。
5. 以上 manifest 诊断指标必须进入统一 CLI 产物 `unified_metrics.json/csv/md`，否则论文实验表会与真实后端复跑脱节。

## 2026-06-08 增量监测：后端实验重构后的对齐结论

本轮继续核查近两年 Agentic RAG / 自动评审评估方向后，新增三个与当前后端重构直接相关的约束。网页核查时间为 2026-06-08，优先使用 arXiv 页面记录的提交/修订时间。

| 论文/方向 | 年份 | 对当前实验的落地要求 | 对架构创新点的修正 |
| --- | --- | --- | --- |
| RAGCap-Bench: Benchmarking Capabilities of LLMs in Agentic RAG Systems | 2025 | Agentic RAG 评估应拆成规划、检索、证据选择、判断等中间能力，因此 manifest export 不能只汇总 run success，必须保留 planner、retriever、verifier、dedup、ranker 的组件级 method 和 metric。 | `Auditable Agent-RAG configuration` 应写成“组件级可复验能力评估”，不是简单 trace 展示。 |
| AgenticRAGTracer: Hop-aware / step-aware diagnosis for Agentic RAG | 2026 | 后续真实 hosted 复跑要导出 node-level trace、失败类型、retrieval hit 与 verifier support 的联动，避免只报告最终 Markdown 报告是否生成。 | 架构中 `agent_trace` 是评价对象的一部分，应进入实验章节而不是只作为调试日志。 |
| MMReview: Multidisciplinary and Multimodal Benchmark for LLM-based Peer Review Automation | 2025 | 当前系统暂时不处理图表视觉内容，因此论文中必须把实验边界限定为 MinerU/Markdown 后的 paper-local textual evidence audit；若接入 GLM-4.6V，多模态能力应作为后续扩展，不作为当前已完成贡献。 | 创新点避免声称“完整多模态审稿自动化”，改为“可接入多模态解析后的证据审计框架”。 |
| AAAI-26 AI Review Pilot: AI-Assisted Peer Review at Scale | 2026 | 大规模部署结果说明 AI review 可以作为明确标识的辅助意见进入会议流程，但系统必须保留 safeguards、基准对照和人工使用边界。当前 hosted acceptance 应把 report 生成、证据判断、队列清空和 auxiliary `not_for_decision` 都作为验收项。 | 创新点表述应落在“human-AI peer-review support / evidence audit”，不能写成自动替代 PC/reviewer 的决策系统。 |

更新后的实验优先级：

1. 已完成的离线 strict gate 继续服务于主链路可信度：统一指标、论文表格、后端 API/worker/core 测试、无前端改动、无密钥泄漏。
2. hosted-provider strict acceptance 不应跳过 Redis/Qdrant/RQ Worker 真实链路；它是最终验收项，不是可由单元测试替代的项。
3. 后续若使用 GLM-4.6V，应只通过环境变量注入 key，并先跑 5-10 篇 structured reviewer / evidence judge 诊断；生成结果仍必须经过 Paper-RAG 检索、verifier、dedup 和 ranker。
4. 论文实验章节建议按 `ready-label retrieval/verifier/ranker -> silver graph ablation -> provider diagnostic -> hosted backend readiness` 排序，不把 provider 文本生成质量放在主结论前面。

## 2026-06-08 增量监测：自动评审行为偏差与互评式评估

本轮继续检索 2025-2026 自动论文评审评估工作后，新增四个与实验边界有关的方向：

| 论文/方向 | 年份 | 对当前实验的落地要求 | 对创新点表述的修正 |
| --- | --- | --- | --- |
| PRAIB: Peer Review AI Benchmark of Behaviour of LLM-Assisted Reviewing | 2026 | 评估自动评审时要看行为差异和系统性偏差，不能只看候选弱点数量或流畅度。当前 provider comparison 应继续报告 generic rate、论文内重复率、support distribution 和 focus coverage。 | 强化“审稿辅助审计”，避免把 LLM reviewer 写成直接替代人工评审。 |
| Gen-Review: AI-generated and human-written peer reviews | 2025 | AI 生成评审可能可检测、可能带偏差，并且 rating 与真实接收/拒稿关系不稳定。当前辅助分类负结果应保留，不能把 accept/reject 预测作为主贡献。 | 支持将分类节点固定为 `not_for_decision=true` 的诊断能力。 |
| DeepReview: Improving LLM-based Paper Review with Human-like Deep Thinking Process | 2025 | 深度评审流程强调结构化推理，但仍需要证据和多维评价约束。当前可以把 TreeReview / DeepReview 类 planner 作为未来 query planner 候选，但必须通过 ready-label retrieval/verifier 实验证明后才可替换默认 direct planner。 | 将“Agent”创新从 prompt flow 改写为“可消融的规划-检索-验证-排序图”。 |
| AutoBench: Automating LLM Evaluation through Reciprocal Peer Assessment | 2025 | 互评式自动评价可以降低人工成本，但也可能放大 evaluator bias；当前使用 hosted verifier 时必须保留 metric boundary，并把 LLM judge 结果标为 silver/diagnostic。 | 强化 boundary-aware evaluation，拒绝把模型互评结果写成 gold。 |

对当前实验计划的新增约束：

1. Provider 生成实验继续作为 diagnostic，不进入主质量结论，除非有 human-gold 或外部 ready-label 证据支撑。
2. 后续 GLM/MiniMax 扩样时，必须同时记录 `generic_rate`、`duplicate_count`、`deduplication_reduction_rate`、`supported_rate` 和 `partial_or_better_rate`。
3. 自动评审行为偏差相关工作支持保留负结果：简单 query expansion 无提升、辅助 accept/reject 分类低于 metadata baseline、untuned hybrid 未超过 dense Hit@3，都应写入论文讨论而不是删除。
4. 如果未来引入互评式 LLM evaluator，统一指标必须将其标为 `silver` 或 `diagnostic`，并在 source artifact 中明确 evaluator/provider，不得混入 human gold。

## 2026-06-12 增量监测：何时需要 Agentic RAG 与人机协作评审边界

本轮只保留已通过 arXiv 页面核验的论文。检索中出现的错误标题/编号组合已排除，不进入研究结论。

| 论文/方向 | 年份 | 对当前实验的落地要求 | 对创新点与架构的修正 |
| --- | --- | --- | --- |
| Is Agentic RAG worth it? An experimental comparison of RAG approaches | 2026 | Agentic RAG 不能因架构更复杂就默认优于固定流程。当前 `direct` planner、固定可审计 graph 与动态/增强式候选必须同时报告质量、延迟和调用成本；只有 ready-label 指标改善后才切换默认配置。 | 将创新点限定为“可消融、可追踪、由证据决定是否启用的 Agent-RAG”，不宣称 agent orchestration 本身必然提升质量。 |
| AgenticRAGTracer | 2026 | 最终结果分数不足以定位多步检索失败。后端 manifest 与 `agent_trace` 应保留节点级状态、retrieval hit、verifier support、失败类型和执行步数，后续可增加 latency/cost。 | 进一步强化组件级/轨迹级诊断；固定 graph 是当前可复验基线，动态路由属于需单独验证的候选。 |
| Agentic Artificial Intelligence: Architectures, Taxonomies, and Evaluation of Large Language Model Agents | 2026 | Agent 系统的风险不仅是生成幻觉，还包括循环、错误动作与 prompt injection。当前 paper text 必须继续视为不可信输入，公开 trace 必须脱敏，节点要有明确终止条件。 | 架构创新增加“受约束的 agent execution boundary”，而不是追求无限自主性。 |
| PeerPrism: Peer Evaluation Expertise vs Review-writing AI | 2026 | 人工观点来源与 AI 表面改写不能被二元“人工/AI”标签混为一谈。Provider comparison 应区分候选弱点/判断来源与最终文本实现，不能用文本风格作为评审质量代理。 | 将系统定位为辅助审计与证据组织工具；保留 human-gold、provider diagnostic、silver judge 的来源边界。 |
| LLM-as-a-Reviewer | 2026 | 自动 reviewer 存在评分偏差、主题侧重点偏差和 prompt injection 风险。后续 hosted 扩样除 groundedness 外，还应单独记录 topical/focus distribution 与 adversarial robustness。 | `Adversarially bounded paper processing` 从未来方向升级为明确实验边界；不能把 provider rating 当作决策依据。 |

据此，当前最合理的流程架构仍是受约束、显式、可消融的固定主链路：

```text
candidate generation
  -> explicit query planning
  -> paper-local retrieval
  -> evidence verification
  -> intra-paper deduplication
  -> evidence-aware ranking
  -> diagnostic report
```

动态路由、多代理协作和循环检索只作为候选配置；它们必须在 ready-label 指标、失败轨迹、延迟和成本上优于上述固定主链路后，才允许成为默认配置。

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
- RAGCap-Bench: Benchmarking Capabilities of LLMs in Agentic Retrieval Augmented Generation Systems, arXiv 2025: https://arxiv.org/abs/2510.13910
- AgenticRAGTracer: A Hop-Aware Benchmark for Diagnosing Multi-Step Retrieval Reasoning in Agentic RAG, arXiv 2026: https://arxiv.org/abs/2602.19127
- MMReview: A Multidisciplinary and Multimodal Benchmark for LLM-Based Peer Review Automation, arXiv 2025: https://arxiv.org/abs/2508.14146
- PRAIB: Peer Review AI Benchmark of Behaviour of LLM-Assisted Reviewing, arXiv 2026: https://arxiv.org/abs/2605.29815
- Gen-Review: A Large-scale Dataset of AI-Generated and Human-written Peer Reviews, arXiv 2025: https://arxiv.org/abs/2510.20106
- DeepReview: Improving LLM-based Paper Review with Human-like Deep Thinking Process, ACL 2025: https://aclanthology.org/2025.acl-long.1420/
- AutoBench: Automating LLM Evaluation through Reciprocal Peer Assessment, arXiv 2025: https://arxiv.org/abs/2510.22593
- AI-Assisted Peer Review at Scale: The AAAI-26 AI Review Pilot, arXiv 2026: https://arxiv.org/abs/2604.13940
- Is Agentic RAG worth it? An experimental comparison of RAG approaches, arXiv 2026: https://arxiv.org/abs/2601.07711
- Agentic Artificial Intelligence (AI): Architectures, Taxonomies, and Evaluation of Large Language Model Agents, arXiv 2026: https://arxiv.org/abs/2601.12560
- PeerPrism: Peer Evaluation Expertise vs Review-writing AI, arXiv 2026: https://arxiv.org/abs/2604.14513
