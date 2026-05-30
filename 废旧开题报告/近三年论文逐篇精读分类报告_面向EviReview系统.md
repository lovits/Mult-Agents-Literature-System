# 近三年 Agent/RAG 论文评审分类相关论文逐篇精读报告

面向选题：轻量多 Agent + RAG 的证据校验型论文自动评审与接收倾向分类系统（EviReview-Lite）

生成日期：2026-05-23

## 0. 文档来源与处理说明

本报告覆盖目录 `paper/近三年_Agent_RAG_论文评审分类_相关论文` 下的 17 篇论文。对应 Markdown 已整理到：

`paper/近三年_Agent_RAG_论文评审分类_相关论文/MinerU_md`

本次检查发现 17 篇 PDF 均已有 MinerU 解析结果，因此没有重复消耗 MinerU API 额度，而是复用已有 MinerU Markdown 并按当前论文编号重命名整理。`05_ReviewGrounder_existing.md` 与 `17_ReviewGrounder_arXiv_2026.md` 经过文件比对为完全相同内容，后文保留两个编号，但按同一篇论文处理。

这里的“精读报告”不是单纯摘要，而是按你的毕业论文选题回答四个问题：

1. 这篇论文属于哪类工作。
2. 它解决了什么问题，方法和实验是什么。
3. 它对你的系统有哪些可直接复用的模块、评价指标、数据或 baseline 价值。
4. 它不适合作为你主线的地方在哪里，避免硕士课题过重。

## 1. 面向 EviReview-Lite 的论文分类总览

你的系统不建议做“全自动替代审稿人”。更稳妥的硕士课题定义是：

给定一篇论文，系统生成候选弱点评审，检索论文内部和可选外部证据，对每条弱点给出证据支持标签，并用这些结构化证据特征辅助接收倾向分类。

按这个目标，17 篇论文可以分为五类。

### A. 自动评审生成与多 Agent 审稿框架

代表论文：

- 01 MARG
- 03 DeepReview
- 04 ScholarPeer
- 07 ReviewAgents
- 08 AgentReview
- 09 Can LLMs Provide Useful Feedback
- 13 Can LLMs Be Trusted Paper Reviewers

可用价值：

- 提供审稿生成任务定义、reviewer/AC 多角色设计、结构化评审输出格式。
- 可作为生成端 baseline：Direct LLM、Single Agent、Multi-Agent、Structured Prompt。
- 证明“LLM 评审可辅助但不能替代人”，适合写研究背景和问题动机。

不建议直接复现：

- DeepReview、ScholarPeer、ReviewAgents 都涉及大规模数据、训练或 web-scale 检索，作为硕士主线过重。
- MARG 成本高，可复现简化版，不建议完整复现。

### B. 证据支撑、事实校验与评审可验证性

代表论文：

- 02 FactReview
- 05/17 ReviewGrounder
- 10 SubstanReview
- 14 RAGChecker
- 15 RefChecker

可用价值：

- 直接支持你的创新点：从“生成评审”转向“证据校验评审”。
- 可复用 claim/evidence 标签体系、rubric 维度、claim-level evaluation。
- 可构造你的核心实验：判断生成弱点是否被论文证据支持。

优先级：

- 最高优先级：ReviewGrounder、FactReview、SubstanReview、RAGChecker、RefChecker。

### C. 新颖性/相关工作定位辅助

代表论文：

- 11 OpenNovelty
- 12 NoveltyAgent
- 04 ScholarPeer 的 historian/baseline scout 模块

可用价值：

- 可作为系统的“可选增强模块”：检索相关工作，判断弱点是否涉及 novelty、missing baseline、comparison 不充分。
- 适合放在扩展实验或未来工作中。

不建议作为主线：

- 全文外部文献检索、二阶引用数据库、500+ 投稿规模部署，对硕士实现和数据稳定性要求偏高。

### D. 通用 Agentic RAG 与 RAG 评估

代表论文：

- 14 RAGChecker
- 16 MA-RAG
- 15 RefChecker

可用价值：

- 设计你的 RAG verifier：query decomposition、evidence extraction、claim entailment、retriever/generator 分诊指标。
- 作为 RAG 模块 baseline：BM25、Dense Retrieval、Hybrid Retrieval、Multi-Agent RAG。

不建议：

- MA-RAG 是通用多跳 QA 框架，不是论文评审专用，只能借鉴架构，不宜作为主要相关工作。

### E. 评审质量数据集与分类辅助

代表论文：

- 06 RottenReviews
- 03 DeepReview
- 07 ReviewAgents
- 09 Can LLMs Provide Useful Feedback

可用价值：

- 接收倾向分类可使用 review text、rating、decision、weakness count、evidence-supported ratio 等特征。
- RottenReviews 的可解释质量特征可直接转化为分类特征和评审质量分析特征。

## 2. 论文与系统模块映射

| 系统模块 | 可参考论文 | 可直接借鉴内容 | 建议实现强度 |
|---|---|---|---|
| PDF/Markdown 解析 | 03 DeepReview, 13 Trusted Reviewers | MinerU/Markdown 化论文输入 | 必做 |
| 论文结构化表示 | 02 FactReview, 05 ReviewGrounder | section、claim、result、baseline、metric 抽取 | 必做简化版 |
| 候选弱点生成 | 01 MARG, 09 Liang, 07 ReviewAgents | structured prompt、多维度弱点生成 | 必做 |
| 证据检索 | 05 ReviewGrounder, 14 RAGChecker, 16 MA-RAG | BM25/dense/hybrid retrieval、section-level evidence | 必做 |
| 弱点证据校验 | 02 FactReview, 10 SubstanReview, 15 RefChecker | claim-evidence、entail/neutral/contradict、supported ratio | 核心创新 |
| 评审质量评价 | 05 ReviewGrounder, 06 RottenReviews | rubric、evidence-based critique、specificity、coverage | 必做 |
| 接收倾向分类 | 03 DeepReview, 06 RottenReviews, 13 Trusted Reviewers | rating/decision prediction、interpretable features | 辅助实验 |
| 外部新颖性分析 | 11 OpenNovelty, 12 NoveltyAgent, 04 ScholarPeer | missing baseline、related-work positioning | 可选增强 |

## 3. 推荐的主线系统设计

综合这些论文，最适合硕士毕业论文的系统不是 ScholarPeer/DeepReview 这种大系统，而是 ReviewGrounder + SubstanReview + RAGChecker 思路的轻量化组合。

推荐系统流程：

1. 输入论文 Markdown。
2. 抽取标题、摘要、引言、方法、实验、结论、表格附近文本。
3. 由 LLM 生成候选弱点，分为 novelty、method、experiment、clarity、reproducibility 五类。
4. 对每条弱点生成检索 query，在论文内部分块中检索 Top-K evidence。
5. 用 verifier 判断弱点与证据关系：Supported、Partially Supported、Generic、Unsupported、Contradicted。
6. 输出证据约束后的 Top-K 弱点和结构化评审。
7. 统计证据支持率、弱点类型分布、实验弱点数量、novelty 弱点数量等，训练或评估 Accept/Reject 辅助分类。

建议三点创新：

1. 评审弱点的证据支持标签：把自由文本评审转成 claim-evidence verification 问题。
2. 面向论文结构的轻量 RAG verifier：不是泛用问答，而是按论文 section、表格、实验描述检索证据。
3. 证据感知的接收倾向分类：用 supported weakness ratio、unsupported weakness ratio、critical weakness count 等可解释特征辅助分类。

## 4. Baseline 设置建议

### 4.1 评审生成/弱点发现 baseline

| Baseline | 说明 | 目的 |
|---|---|---|
| Direct LLM | 直接输入论文摘要/截断正文生成评审 | 最弱但必要 |
| Structured Prompt | 按 summary/strength/weakness/question/rating 输出 | 检查格式化提示收益 |
| MARG-lite | 分 section 生成弱点，再聚合 | 对比多 Agent/分块收益 |
| BM25-RAG Verifier | 候选弱点 + BM25 证据检索 + LLM 校验 | 核心检索 baseline |
| Dense-RAG Verifier | embedding 检索 + LLM 校验 | 对比语义检索 |
| Hybrid-RAG Verifier | BM25 + dense + rerank | 推荐主方法 |
| Ours without verifier | 只生成弱点，不做证据过滤 | 验证 evidence verifier 是否有效 |
| Ours full | 生成 + 检索 + 校验 + rerank | 主方法 |

### 4.2 接收倾向分类 baseline

| Baseline | 输入特征 | 备注 |
|---|---|---|
| Majority | 多数类 | 分类下限 |
| Paper metadata/text | title/abstract/introduction embedding | 基础文本分类 |
| Generated review only | 生成 review embedding | 测试自动评审是否有分类信号 |
| Review quality features | length、question count、weakness count 等 | 来自 RottenReviews |
| Evidence-aware features | supported weakness ratio、unsupported ratio、critical count | 你的系统特色 |
| Text + evidence-aware features | text embedding + 结构化证据特征 | 推荐最终模型 |

## 5. 逐篇精读报告

### 01. MARG: Multi-Agent Review Generation for Scientific Papers

分类：自动评审生成；多 Agent；长论文上下文管理。

核心问题：单个 LLM 受上下文长度和任务复杂度限制，容易生成泛泛而谈的审稿意见，尤其不能稳定覆盖实验、清晰度、影响力等不同评审维度。

方法：MARG 把论文按段落切块分给多个 worker agent，由 leader agent 协调通信；MARG-S 进一步设置实验、清晰度、影响力等专门 expert agent。它的重点不是 RAG，而是通过多 Agent 分工保留全文信息，并让不同 agent 专注不同类型的评论。

数据与实验：使用 GPT-4 进行评审生成，和 SARG-B、SARG-TP、MARG-TP、Liang 等 baseline 比较。自动评价使用与人工评论的 overlap/recall/precision/Jaccard；用户研究显示 MARG-S 将泛化评论比例从约 60% 降到 29%，每篇 good comment 数从 1.7 提升到 3.7。

局限：成本极高，论文报告中 token 使用量非常大；通信协议会出错；没有显式证据校验，生成的“具体”评论未必真实；主要适合生成候选评论，不适合作为最终可信评审。

对你的系统可用处：

- 可作为 `MARG-lite` baseline：按 Introduction/Method/Experiment/Conclusion 分块生成弱点，再汇总。
- 可借鉴多维弱点生成：experiments、clarity、impact。
- 不建议完整复现其 agent 通信机制，太重且不是你的创新中心。

推荐定位：中高优先级。用于“候选弱点生成 baseline”，不是主方法。

### 02. FactReview: Evidence-Grounded Reviews with Literature Positioning and Execution-Based Claim Verification

分类：证据校验型自动评审；claim verification；文献定位；代码执行验证。

核心问题：现有 LLM 审稿系统主要阅读论文叙述本身，容易接受作者话术，对外部文献和代码复现实证证据利用不足。

方法：FactReview 把评审转化为“claim-level evidence assessment”。系统抽取主要 claim、reported result、dataset、baseline、metric；检索邻近文献定位论文贡献；如果有代码仓库，则在受控环境中执行实验，最后给每个 claim 标注 Supported、Supported by the paper、Partially supported、In conflict、Inconclusive。

数据与实验：以 CompGCN 作为端到端案例。系统能复现部分 link prediction 和 node classification 结果，但发现 graph classification 上作者的广义优越性 claim 只部分成立。论文还分析了执行验证的 backend sensitivity 和 failure mode。

局限：实验规模偏案例研究，不是大规模 benchmark；代码执行验证工程复杂，不适合作为硕士主线完整复现；对有代码仓库的论文才有执行验证价值。

对你的系统可用处：

- 直接借鉴 claim label 体系，但可简化为 Supported / Partially Supported / Generic / Unsupported / Contradicted。
- 借鉴“不要给最终录用建议，而是给证据报告”的安全定位。
- 代码执行验证可写为未来工作，不建议主线实现。

推荐定位：最高优先级。你的系统可以把 FactReview 的重执行验证改成轻量 RAG 证据验证。

### 03. DeepReview / DeepReview-13K

分类：大规模自动评审数据集；结构化推理；评审模型训练；接收倾向预测。

核心问题：缺乏带细粒度评审推理链的数据，导致自动评审系统只会生成表层评论，评分/排序/选择能力不稳定。

方法：DeepReview 设计三阶段 review-with-thinking：novelty verification、multi-dimension review、reliability verification。它构造 DeepReview-13K，训练 DeepReviewer-14B，并在评分预测、排序、paper selection 和 LLM-as-judge 评审质量上评估。

数据与实验：数据来自 ICLR 2024/2025，训练集约 13,378 篇，测试集 DeepReview-Bench 约 1,286 篇。任务包括 rating prediction、paper quality ranking、pairwise selection、review text quality。论文报告 DeepReviewer-14B 在 Spearman、MSE、decision accuracy、LLM judge win rate 上优于多种 baseline。

局限：依赖大规模数据构造和模型训练，复现成本高；LLM-as-judge 比重较大；完整系统不是轻量硕士实现。

对你的系统可用处：

- DeepReview-Bench/ICLR 2024-2025 拆分适合作为接收倾向分类参考数据。
- 三阶段结构可以简化为：novelty/method/experiment/reliability 四类弱点生成。
- 可作为强相关工作和不可复现的大模型训练 baseline。

推荐定位：高优先级。用于数据来源和分类辅助实验，不作为主方法复现。

### 04. ScholarPeer: Context-Aware Multi-Agent Framework for Automated Peer Review

分类：外部上下文增强评审；search-enabled multi-agent；高级自动审稿框架。

核心问题：很多自动评审系统在“参数真空”中评估论文，缺少领域历史、当前 SOTA、遗漏 baseline 等外部上下文，因此 novelty 和 significance 判断浅。

方法：ScholarPeer 使用 summary agent、literature expansion agent、historian agent、baseline scout agent 和 multi-aspect Q&A engine。它构造动态外部上下文，形成 domain narrative，寻找 missing baselines，并用 probing questions 验证论文 claim。

数据与实验：在 DeepReview-13K test split 约 1,286 篇上评估，比较 CycleReviewer、DeepReviewer、AgentReview、AI Scientist、single-agent LLM、Stanford Agent Reviewer 等。指标包括 SxS win rate、H-Max score、review diversity、Spearman human correlation。

局限：依赖 Google Search-enabled LLM 和强闭源模型；web-scale 检索不稳定，难复现；评估也依赖 LLM judge 和专家标注，工程量大。

对你的系统可用处：

- baseline scout 的思想很适合写入系统扩展：针对实验弱点检索 missing baseline。
- H-Max 和 review diversity 可作为文献综述中的先进评价方式，不建议实现。
- 可把“外部文献定位”作为 optional module，而不是主线。

推荐定位：中高优先级。用于说明你的系统为什么先做“内部证据校验”，未来再扩展外部文献。

### 05. ReviewGrounder: Improving Review Substantiveness with Rubric-Guided, Tool-Integrated Agents

分类：证据支撑型评审生成；rubric-guided evaluation；tool-integrated agents。

核心问题：LLM 审稿经常生成模板化、缺少证据、缺少可操作建议的评论。原因是没有显式 rubric，也没有充分使用论文内容和相关工作来 grounding。

方法：提出 REVIEWBENCH 和 REVIEWGROUNDER。REVIEWBENCH 从 DeepReview-13K 构造 paper-specific rubrics，用 8 个维度评估评审质量：Core Contribution Accuracy、Results Interpretation、Comparative Analysis、Evidence-Based Critique、Critique Clarity、Completeness Coverage、Constructive Tone、False/Contradictory Claims。REVIEWGROUNDER 先由 Drafter 生成初稿，再由 Literature Searcher、Insight Miner、Result Analyzer 做 grounding，最后 Aggregator 汇总。

数据与实验：REVIEWBENCH 基于 DeepReview-13K，过滤后抽取约 1.3K 篇。对比 foundation models、AgentReview、AI Scientist、CycleReviewer、DeepReviewer。论文报告 ReviewGrounder 在 rubric overall score 上显著优于各类 baseline，尤其 Evidence-Based Critique 提升明显。

局限：完整系统使用 Phi-4-14B drafter 和 GPT-OSS-120B grounding stage，训练与部署较重；paper-specific rubric 构造本身也是复杂任务。

对你的系统可用处：

- 这是你的主线最切题论文之一。你的系统可简化为“不训练 drafter，只做 evidence-grounded weakness filtering”。
- 8 个 rubric 维度可以改成你的评价指标，尤其 Evidence-Based Critique、False/Contradictory Claims、Completeness Coverage。
- Drafter + Grounder 架构可直接变成你的系统结构：候选弱点生成器 + RAG 证据校验器。

推荐定位：最高优先级。建议作为核心相关工作和主要对比对象。

### 06. RottenReviews: Benchmarking Review Quality with Human and LLM-Based Judgments

分类：评审质量 benchmark；可解释特征；LLM judge 可靠性分析。

核心问题：评审质量难以规模化评价，LLM 能否作为评审质量 judge 并不可靠。

方法：构造 RottenReviews，包含多 venue 投稿、reviewer profile、paper metadata，并定义 review-dependent 和 reviewer-dependent 质量指标。review-dependent 包括长度、引用数量、section-specific comments、semantic alignment、timeliness、politeness、readability、lexical diversity、raised questions、sentiment、hedging 等。还用人类专家标注 13 个 review quality dimensions，比较 LLM judge 与人类的一致性。

数据与实验：数据来自 NeurIPS、ICLR、F1000Research、Semantic Web Journal，共超过 15,000 篇论文/提交和 55,000 条 review，并有 9,000+ reviewer profiles。结论是 zero-shot 和 fine-tuned LLM judge 与专家标注对齐有限，简单可解释特征模型反而更好。

局限：目标是评审质量评价，不是生成评审；部分 reviewer profile 数据只适用于开放身份 venue；不直接解决论文弱点是否真实。

对你的系统可用处：

- 可解释特征很适合接收倾向分类辅助实验。
- 论文结论能支持你的论点：不要只依赖 LLM judge，要有结构化证据指标。
- 可引入 section-specific comments、reference count、question count、evidence-supported weakness ratio 作为可解释特征。

推荐定位：高优先级。用于分类辅助实验和评审质量指标设计。

### 07. ReviewAgents: Bridging the Gap Between Human and AI-Generated Paper Reviews

分类：结构化 CoT 评审数据集；多角色评审 agent；相关论文感知训练。

核心问题：直接 prompt LLM 生成 review 与人类评审过程差距大，缺少 summary-analysis-conclusion 的结构化推理，也缺少相关论文参考。

方法：构造 Review-CoT 数据集，把 review 转录为 Summary、Analysis、Conclusion 三阶段结构，并加入每篇论文提交时间前最相关的两篇论文标题和摘要。训练 reviewer agent 和 area chair agent，推理时多个 reviewer 生成评论，AC 汇总 meta-review。

数据与实验：Review-CoT 包含 37,403 篇论文和 142,324 条 review comments/meta-reviews，来自 ICLR 2017-2024 和 NeurIPS 2016-2024。ReviewBench 测试集包含 ICLR 2024 和 NeurIPS 2024 各 100 篇。指标包括 language diversity、semantic consistency、sentiment consistency、Review Arena win rate。

局限：依赖大规模数据转录和训练；用 ROUGE/SPICE/sentiment 等评价 review 与人类 review 的相似度，未必等价于真实有用性；完整复现成本高。

对你的系统可用处：

- 可借鉴输出结构：Summary -> Analysis -> Conclusion。
- “相关论文感知”可在你的系统中简化成可选 Top-2 related papers，而非训练。
- 可以作为多角色 baseline 的理论依据，但不建议复现训练。

推荐定位：中高优先级。用于结构化输出和多角色 baseline。

### 08. AgentReview: Exploring Peer Review Dynamics with LLM Agents

分类：审稿过程模拟；社会机制分析；多角色 agent。

核心问题：传统自动评审只生成评论，忽略 reviewer、author、area chair、rebuttal、最终决策之间的互动过程。

方法：用 LLM agent 模拟 reviewer、author、AC 等角色，研究 reviewer commitment、intention、knowledgeability、AC involvement、author anonymity、review mechanism 等对结果的影响。

数据与实验：论文构造了大规模模拟数据，包含 53,800+ generated reviews、rebuttals、updated reviews、meta-reviews 和 final decisions。主要实验目标是分析审稿机制，而不是提高单篇评审证据质量。

局限：离你的系统主线较远。它关注社会动态模拟，不关注 claim-level evidence grounding。模拟结果能否对应真实评审机制也需要谨慎。

对你的系统可用处：

- 可作为“多 Agent 评审流程模拟”的相关工作。
- 不建议纳入 baseline，除非只做非常简化的 reviewer/AC 聚合对照。
- 可用于论文背景中说明多 Agent 不等于证据可靠，仍需要 grounding。

推荐定位：中低优先级。相关但不核心。

### 09. Can Large Language Models Provide Useful Feedback on Research Papers?

分类：LLM 科研反馈大规模实证；单模型反馈生成；用户研究。

核心问题：LLM 生成科研反馈到底有没有用，是否与人类 reviewer 意见有重合。

方法：用 GPT-4 对完整 PDF 生成结构化科研反馈，包含 significance/novelty、acceptance reasons、rejection reasons、suggestions。通过 retrospective matching 比较 LLM feedback 与人类 reviewer comment 的重叠，并做 prospective user study。

数据与实验：Nature family journals 3,096 篇 accepted papers 和 8,745 条 human comments；ICLR 1,709 篇 papers 和约 6,505 条 comments。结果显示 GPT-4 与人类 reviewer 的点重叠在 Nature 上约 30.85%，ICLR 上约 39.23%，接近 human-human reviewer overlap；308 名研究者用户研究中，57.4% 认为有帮助，82.4% 认为比至少部分人类 review 更有帮助。

局限：单次 GPT-4 反馈容易偏向“增加更多数据集”等泛化建议；缺少深入 method design critique；没有显式证据校验；对图表理解有限。

对你的系统可用处：

- 可作为 Direct LLM baseline 的代表论文。
- 可借鉴 comment matching 方法评估生成弱点与人类弱点重合。
- 其局限正好支撑你的核心问题：需要证据校验和细粒度 grounding。

推荐定位：高优先级。用于动机和 baseline。

### 10. SubstanReview: Automatic Analysis of Substantiation in Scientific Peer Reviews

分类：评审论证充分性；claim-evidence pair extraction；评审质量检测。

核心问题：好的 review 不应只有主观判断，claim 应该有 evidence 支撑。现有评审质量评价缺少可解释的 claim-evidence 分析。

方法：把 review substantiation 定义为“主观 claim 中有 evidence 支持的比例”。任务分两步：claim tagging 识别正/负向主观评价；evidence linkage 为每个 claim 找支持 span。论文构造 SubstanReview 数据集，并提出 SubstanScore。

数据与实验：SubstanReview 包含 550 条 NLP conference reviews，来自 NLPeer，领域专家标注 claim/evidence span。IAA 使用 Krippendorff unitizing alpha，主标注轮约 0.657。数据覆盖 CoNLL 2016、ACL 2017、COLING 2020、ARR 2022，并分析 supported claims 比例变化。

局限：它检查的是 review 内部是否给出 evidence，不判断 evidence 是否真实对应论文内容；数据规模较小；主要是 review quality，不是自动生成 review。

对你的系统可用处：

- 这是你 evidence-supported weakness 的最直接理论来源。
- 可以把 SubstanScore 改造成 EviScore：生成弱点中有论文证据支持的比例。
- 可借鉴 claim/evidence span 标注思想，做小规模人工标注集。

推荐定位：最高优先级。建议作为核心方法理论依据。

### 11. OpenNovelty: Verifiable Scholarly Novelty Assessment

分类：新颖性评估；agentic retrieval；证据化 novelty report。

核心问题：评审中的 novelty 判断需要大量相关工作检索，LLM 仅凭参数知识容易幻觉或遗漏近作。

方法：四阶段流程：抽取 core task 和 contribution claims；生成 query 并语义扩展；用 Wispaper 等语义搜索检索 prior work；构造层级 taxonomy 并进行 contribution-level full-text comparison；最终生成带引用和 evidence snippet 的 novelty report。

数据与实验：部署到 500+ ICLR 2026 submissions，公开 novelty reports。论文强调所有 novelty 判断都基于真实检索论文和证据片段。

局限：系统依赖外部搜索引擎和大量文献处理，复现难度较高；实验更多是系统报告和部署分析，不一定有标准 ground truth。

对你的系统可用处：

- 可借鉴 contribution claim extraction 和 query expansion。
- 可作为 novelty weakness 的可选增强：发现“作者没有比较某类近似工作”。
- 不建议主线实现 full-text external comparison，可作为未来工作。

推荐定位：中等优先级。适合作为 novelty 模块参考。

### 12. NoveltyAgent: Point-wise Novelty Analysis and Self-Validation

分类：新颖性报告生成；point-wise RAG；self-validation。

核心问题：通用 DeepResearch 和 AI Reviewer 对 novelty 分析不够专门，容易遗漏细粒度 novelty point，且对外部文献 faithful 不够。

方法：三阶段：构造一阶/二阶引用全文数据库；把论文拆成离散 novelty points，每个点独立检索和比较；Validator/Improver 对报告中引用外部工作的句子做 faithful self-validation。评价上提出 checklist-based evaluation，覆盖 fluency、faithfulness、completeness、effectiveness、depth 五类 69 个条目。

数据与实验：基于 ICLR 2025 submissions 选 50 篇目标论文，每篇构造约 200 个一阶/二阶引用 PDF 数据库。对比 GPT-5 Thinking、GPT-5 DeepResearch、Gemini DeepResearch、Kimi、AgentReviewer、DeepReview。NoveltyAgent overall 9.33，优于 GPT-5 DeepResearch 8.47 和 DeepReview 8.54。

局限：每篇 200 个 PDF 的本地数据库过重；依赖 GPT-5 Mini 等模型；任务集中在 novelty report，不是完整 review。

对你的系统可用处：

- point-wise decomposition 很适合你的弱点校验：每条 weakness 独立检索证据。
- checklist evaluation 可改成你的证据校验评价表。
- 一阶/二阶引用数据库不建议做，硕士阶段可用论文内部 RAG 或少量外部文献。

推荐定位：中高优先级。用于“逐点证据校验”和评估表设计。

### 13. Can Large Language Models Be Trusted Paper Reviewers? A Feasibility Study

分类：RAG + AutoGen 自动评审可行性研究；接收决策实验。

核心问题：LLM 能否作为真正 paper reviewer，甚至给出接收结果。

方法：系统结合 RAG、AutoGen 多 Agent、CoT prompt，用 reviewer agent 和 chair agent 执行格式检查、评分、评论生成、论文排序和最终接收决策。论文先将 PDF 转为文本/向量库，再按角色 prompt 评审。

数据与实验：使用 WASA 2024 的 290 篇 submissions，GPT-4o 平均用时 2.48 小时、成本 104.28 美元。LLM 选择论文与真实录用论文的相似度平均只有 38.6%。论文认为 LLM 缺乏独立判断，存在 retrieval preference，不适合替代人类。

局限：会议和领域较窄；把系统目标设为直接输出 accepted papers 风险较高；CoT/AutoGen 流程对结果可靠性提升有限。

对你的系统可用处：

- 可作为“为什么不做最终自动录用决策”的反例。
- 可借鉴 reviewer/chair 两级流程做分类辅助，但要避免声称替代 PC 决策。
- 支持你的论文表述：分类只是辅助实验，不是系统的主要伦理定位。

推荐定位：中等优先级。用于风险论证和系统边界。

### 14. RAGChecker: Fine-grained Framework for Diagnosing RAG

分类：RAG 评价框架；claim-level entailment；retriever/generator 分诊。

核心问题：RAG 系统评估不能只看最终答案，需要细粒度地区分 retrieval error 和 generator error。

方法：RAGChecker 把回答和 ground truth 拆成 claim，用 entailment checking 评价正确性、完整性，并分别设计 overall metrics、retriever metrics、generator metrics。检索器看 claim recall/context precision，生成器看 context utilization、noise sensitivity、hallucination、faithfulness 等。

数据与实验：构造 4,162 queries，覆盖 10 个领域。比较 8 个 RAG 系统，即 BM25/E5-Mistral 两类 retriever 与 GPT-4、Mixtral、Llama3-8B、Llama3-70B 四类 generator 组合。Meta-evaluation 显示 RAGChecker 与人类偏好相关性优于 BLEU、ROUGE、BERTScore、TruLens、ARES、RAGAS、CRUD-RAG。

局限：面向通用 RAG 问答，不是论文评审；需要 ground truth answer 才能完整计算部分指标。

对你的系统可用处：

- 你的 evidence verifier 可以直接借鉴 claim-level entailment。
- 可设计两个诊断指标：weakness evidence recall、evidence precision。
- 可比较 BM25 vs dense vs hybrid retrieval 对 supported weakness 检测的影响。

推荐定位：最高优先级。用于 RAG 评价方法和实验指标。

### 15. RefChecker: Reference-based Fine-grained Hallucination Checker

分类：幻觉检测；claim-triplet；reference-based verification。

核心问题：长回答的 hallucination 不能只做 response-level 或 sentence-level 检查，需要更细粒度、边界清晰的 claim 单元。

方法：RefChecker 用 extractor 把回答拆成 knowledge triplets / claim-triplets，再用 checker 和 reference 比较，标注 Entailment、Contradiction、Neutral。它覆盖 Zero Context、Noisy Context、Accurate Context 三种设置，并支持开源和闭源 extractor/checker。

数据与实验：benchmark 含 300 examples，人工标注 2,100 个 responses 的 11k claim-triplets，7 个 LLM。实验显示 triplet-level 检查优于 response/sentence/sub-sentence 粒度，RefChecker 比 SelfCheckGPT、FActScore、FacTool 更好。

局限：triplet 对学术评审弱点不一定自然，很多评审 claim 是复杂判断而非实体关系；需要适配论文评审语境。

对你的系统可用处：

- 可借鉴三分类 Entailment/Contradiction/Neutral，但不必强制三元组化。
- 适合做生成评审的 hallucination/unsupported claim 检测。
- 可作为 verifier baseline 或评估工具思路。

推荐定位：高优先级。用于 claim verification 和 label 设计。

### 16. MA-RAG: Multi-Agent Retrieval-Augmented Generation via Collaborative CoT Reasoning

分类：通用 multi-agent RAG；复杂 QA；可解释检索推理。

核心问题：传统 RAG 对模糊、多跳、复杂信息需求处理不好，因为 query decomposition、evidence extraction、answer synthesis 混在一起。

方法：MA-RAG 设置 Planner、Step Definer、Extractor、QA Agent。Planner 拆解问题，Step Definer 生成检索步骤，Extractor 提取相关证据，QA Agent 生成答案。训练-free，通过模块化协作提升多跳 QA。

数据与实验：在 NQ、HotpotQA、2WikimQA、TriviaQA 等多跳/开放 QA benchmark 上评估，并扩展到 PubMedQA、MedMCQA。Ablation 显示 Planner 和 Extractor 对多跳任务重要，QA Agent 对最终性能影响最大。

局限：不是论文评审任务；CoT agent 多，可能增加成本；对你的硕士系统来说完整 MA-RAG 偏重。

对你的系统可用处：

- 可借鉴轻量两级结构：Planner 生成 evidence query，Extractor 找证据。
- 不建议做完整四 agent，可做 `Query Planner + Evidence Extractor + Verifier` 三步。
- 可作为 Hybrid-RAG/Agentic-RAG baseline 的理论来源。

推荐定位：中等优先级。作为 RAG 架构辅助参考。

### 17. ReviewGrounder arXiv 版本

分类：同 05。

文件比对结果：`17_ReviewGrounder_arXiv_2026.md` 与 `05_ReviewGrounder_existing.md` 内容完全一致。

处理建议：

- 文献综述中只引用一次 ReviewGrounder。
- 论文库编号可保留 05 和 17，但实验/报告中不要重复计数。
- 如果后续写参考文献，以 arXiv 版本或正式版本中元数据最完整者为准。

对你的系统可用处：同 05。它是最贴近你课题的核心论文之一。

## 6. 这些论文对开题报告的取舍建议

### 必须重点写的 7 篇

1. ReviewGrounder：最贴合“证据支撑评审”的系统与 benchmark。
2. FactReview：claim-level evidence report 和 evidence-grounded review 定位。
3. SubstanReview：review claim-evidence/substantiation 理论依据。
4. RAGChecker：RAG 诊断指标和 claim-level RAG evaluation。
5. RefChecker：fine-grained hallucination checking。
6. DeepReview：数据、评分/分类、评审推理链。
7. Liang et al. GPT-4 Feedback：LLM 反馈有用但泛化，作为动机与 direct baseline。

### 可以作为辅助相关工作的 6 篇

- MARG：多 Agent 分块生成候选弱点。
- ScholarPeer：外部上下文和 missing baseline。
- ReviewAgents：结构化 CoT 与 reviewer/AC。
- RottenReviews：评审质量可解释特征。
- NoveltyAgent：逐点 novelty 分析与 self-validation。
- OpenNovelty：verifiable novelty report。

### 只需简述的 3 篇

- AgentReview：审稿社会过程模拟，离主线稍远。
- Trusted Paper Reviewers：LLM 不能替代审稿人，适合边界论证。
- MA-RAG：通用 RAG 结构参考。

## 7. 对你的论文题目和实验主线的最终建议

建议题目：

《基于轻量多 Agent 与检索增强生成的证据校验型学术论文评审与接收倾向分类研究》

或者更短：

《面向学术论文评审的证据校验型 RAG 方法研究》

主实验建议：

1. 数据：优先使用 ICLR/OpenReview 数据，选择有 PDF、review、rating、decision 的子集；如可获得 DeepReview/ReviewBench/PRISM 则优先使用。
2. 标注：抽样 100-200 篇论文，对生成弱点做人工或半自动证据支持标注，形成小型 evaluation set。
3. 任务一：弱点证据校验，指标为 label accuracy、macro-F1、supported weakness precision、unsupported hallucination rate。
4. 任务二：评审质量提升，指标为 evidence-supported ratio、specificity、rubric score、人工偏好。
5. 任务三：接收倾向分类，指标为 accuracy、macro-F1、AUC，比较 text-only 与 evidence-aware feature 的增益。

最推荐的系统版本：

`Structured Weakness Generator + Hybrid Paper-RAG Evidence Retriever + LLM/NLI Verifier + Evidence-aware Reranker + Classification Features`

这个版本工作量足够、论文相关性强、实验可复现，且比直接复现 MARG/DeepReview/ScholarPeer 更适合硕士毕业论文。

