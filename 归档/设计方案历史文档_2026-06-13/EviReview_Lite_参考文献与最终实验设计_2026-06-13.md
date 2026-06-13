# EviReview-Lite 参考文献地图与最终实验设计

日期：2026-06-13
研究对象：基于证据验证的多 Agent-RAG 学术论文自动评审系统
范围：只设计后端与实验，不包含前端，不把接收/拒绝分类作为主任务

## 1. 结论先行

本课题最稳妥且工作量适中的主线是：

> 先由多个评审 Agent 生成原子化候选弱点，再使用结构与证据类型感知的 Paper-RAG 检索论文内部证据；对新颖性、遗漏 baseline 等固定类型补充受控 Literature-RAG；随后对每条候选弱点固定执行 Support 与 Refutation 双向证据审计，最后由 Evidence Adjudicator 和 Meta-Reviewer 自动过滤、改写、去重与 Top-K 排序。

核心贡献不应写成“生成更多评审意见”，而应写成：

1. **评审意见级双向证据审计**：同时寻找支持与反驳证据，降低错误保留；
2. **结构与证据类型感知的双 RAG**：Paper-RAG 负责论文内核验，受控 Literature-RAG 负责外部比较；
3. **双 RAG 证据驱动的 Meta-Reviewer Ranker**：自动过滤、去重、排序和置信度标注。

系统全自动运行，不设置人工复核。证据不足或冲突无法消解的候选意见标记为 `uncertain`，保留审计轨迹但不进入 Top-K 最终评审。

## 2. 参考文献在哪里

### 2.1 本地文献目录

当前本地文献库共有 **84 个 PDF** 和 **71 个 Markdown** 文件。

| 目录 | 内容 | 用法 |
| --- | --- | --- |
| `参考论文/开题用论文/` | 开题报告实际使用的 15 篇核心论文、MinerU 全文和精读笔记 | 优先阅读，支撑创新点、Baseline 和指标 |
| `参考论文/近三年_Agent_RAG_论文评审分类_相关论文/` | 2023–2026 年 Agent-RAG、自动评审、证据验证相关论文 | 补充近年相关工作 |
| `参考论文/整合去重_论文库/PDF_MD_成对论文库/` | 去重后的 PDF/Markdown 成对语料 | 可直接作为受控 Literature-RAG 语料 |
| `参考论文/重新分类/` | 按核心评审、Agent、数据集等重新分类的论文 | 按模块检索 |
| `参考论文/开题用论文/01_MARG_精读笔记.md` | MARG 单篇精读 | 候选弱点生成 Baseline |
| `参考论文/开题用论文/02-15_论文精读报告合集.md` | 其余核心论文的详细精读 | 快速核对方法、数据和指标 |

阅读顺序以以下两个索引为准：

- `参考论文/开题用论文/README.md`
- `参考论文/近三年_Agent_RAG_论文评审分类_相关论文/README.md`

### 2.2 核心文献与本课题的关系

| 文献 | 支撑内容 | 不应直接声称的内容 |
| --- | --- | --- |
| MARG (2024) | 多 Agent、分角度候选评审生成；作为生成端 Baseline | 不能证明生成意见具有证据真实性 |
| CLAIMCHECK (2025) | 真实评审弱点、争议论文 claim、有效性与客观性标签；最适合双向审计主实验 | 不是完整端到端自动评审系统 |
| PeerQA (2025) | 由同行评审问题构成的文档级 QA；适合 Paper-RAG 检索实验 | QA 正确不等于弱点评审正确 |
| RAGChecker (2024) | 将检索与生成分开诊断的指标设计 | 通用 RAG 指标不能替代评审有效性指标 |
| RefChecker (2024) | 细粒度 claim 检查与幻觉检测思路 | 其通用 claim-triplet 标签需适配评审意见 |
| SubstanReview (2023) | 评审 claim-evidence pair 与 substantiation 评价 | 主要检查评审文本内部论证，不直接核验论文正文 |
| ReviewGrounder (2026) | rubric-guided、tool-integrated、evidence-grounded critique | 完整复现工程成本较高 |
| ScholarPeer (2026) | 外部文献上下文、baseline scout、active verification | Web-scale Literature-RAG 超出本课题主实验规模 |
| OpenNovelty / NoveltyAgent (2026) | 贡献点拆分、逐点文献检索、引用真实性检查 | 不需要完整复现引用网络和大规模全文库 |
| RottenReviews (2025) | factuality、vagueness、actionability 等评审质量维度 | LLM judge 与专家对齐有限，不能只依赖单一 LLM 裁判 |
| PeerRead | 论文、评审和接收标签；仅适合辅助分类 | 接收倾向不能作为系统自动评审质量的主结论 |

### 2.3 已核验的官方入口

- MARG: https://arxiv.org/abs/2401.04259
- CLAIMCHECK: https://aclanthology.org/2025.findings-emnlp.1185/
- PeerQA: https://aclanthology.org/2025.naacl-long.22/
- RAGChecker: https://github.com/amazon-science/RAGChecker
- RefChecker: https://github.com/amazon-science/RefChecker
- SubstanReview: https://aclanthology.org/2023.findings-emnlp.684/
- ScholarPeer: https://arxiv.org/abs/2601.22638
- OpenReview API: https://docs.openreview.net/getting-started/using-the-api

## 3. 研究问题

| 编号 | 研究问题 |
| --- | --- |
| RQ1 | 结构与证据类型感知检索能否比普通 BM25、Dense 和 Hybrid RAG 更准确地找到评审意见所需证据？ |
| RQ2 | 同时构建 Support 与 Refutation 案例，能否比单 Judge 验证更准确地过滤不成立或已被论文覆盖的弱点？ |
| RQ3 | 受控 Literature-RAG 能否提高新颖性、遗漏 baseline 和相关工作类意见的可验证性？ |
| RQ4 | Meta-Reviewer Ranker 能否在不降低主要弱点覆盖率的情况下，提高 Top-K 弱点精度并减少重复？ |
| RQ5 | 完整系统能否比 Direct LLM 和多 Agent 生成 Baseline 输出更有证据、更具体、更少错误的自动评审？ |

## 4. Agent-RAG 架构

### 4.1 总体流程

```text
论文 PDF / Markdown
  -> Parser：章节、段落、表格、附录与元数据
  -> 三个 Reviewer Agents：生成原子化候选弱点
  -> Query Planner：声明章节、证据类型与检索查询
  -> Paper-RAG：所有候选弱点的论文内证据
  -> Literature-RAG：固定外部比较类型的文献证据
  -> Support Agent + Refutation Agent
  -> Evidence Adjudicator：keep / rewrite / reject / uncertain
  -> Meta-Reviewer：去重、过滤、排序、置信度与 Top-K 报告
```

### 4.2 八个固定 Agent

| Agent | 输入 | 输出 | 主要职责 |
| --- | --- | --- | --- |
| Method Reviewer | 方法、算法、理论章节 | 方法类原子弱点 | 发现假设、推导、方法设计问题 |
| Experiment Reviewer | 实验、表格、消融、结果 | 实验类原子弱点 | 发现实验设计、baseline、消融和结论问题 |
| Reproducibility Reviewer | 方法细节、设置、附录 | 复现类原子弱点 | 发现实现和报告缺失 |
| Query Planner | 候选弱点、论文结构 | Paper/Literature 查询计划 | 声明目标章节和预期证据类型 |
| Support Agent | 候选弱点、证据包 | Support Case | 建立候选弱点成立的证据链 |
| Refutation Agent | 候选弱点、证据包 | Refutation Case | 主动寻找已覆盖、误读或反例证据 |
| Evidence Adjudicator | 双向案例 | 自动裁决 | 输出 `keep/rewrite/reject/uncertain` |
| Meta-Reviewer | 所有裁决与证据 | Top-K 结构化评审 | 去重、排序、置信度标注和报告生成 |

固定执行 Support、Refutation 和 Adjudicator，不采用“争议触发升级”。固定协议便于复现和消融；成本通过候选数量上限、批处理、缓存和共享索引控制。

### 4.3 两套 RAG

#### Paper-RAG

对每条候选弱点运行：

```text
BM25 + Dense Retrieval
  -> Reciprocal Rank Fusion
  -> Section Prior
  -> Evidence-Type Prior
  -> Neighbor Expansion
  -> Paper Evidence Bundle
```

证据类型至少包括：`paragraph`、`table/caption`、`algorithm`、`implementation_detail`、`appendix`、`absence_signal`。

#### Literature-RAG

仅对固定类型运行：`novelty`、`related_work`、`missing_baseline`、`external_comparison`。

```text
贡献点/比较对象拆分
  -> 本地受控文献库检索
  -> BM25 + Dense + 元数据过滤
  -> Top-K 文献片段
  -> 标题、年份、来源、ID/URL 与证据片段
```

论文主实验使用本地 `参考论文/整合去重_论文库/PDF_MD_成对论文库/`，保证可复现。OpenAlex、Semantic Scholar 只作为扩展数据源，不作为主实验依赖。

### 4.4 自动裁决与排序

裁决标签：

| 标签 | 含义 | 是否进入最终 Top-K |
| --- | --- | --- |
| `keep` | 支持充分，反驳不足 | 是 |
| `rewrite` | 问题部分成立，但表述需收窄 | 改写后进入 |
| `reject` | 已覆盖、误读、泛化或无证据 | 否 |
| `uncertain` | 证据不足或冲突不能自动消解 | 否，仅保留日志 |

排序建议：

```text
rank_score =
  0.30 * evidence_sufficiency
  + 0.20 * validity_probability
  + 0.20 * severity
  + 0.15 * specificity
  + 0.10 * actionability
  + 0.05 * literature_support
  - redundancy_penalty
  - uncertainty_penalty
```

## 5. 数据源

### 5.1 必做数据

| 数据源 | 获取地址 | 用途 | 是否需要新增人工标注 |
| --- | --- | --- | --- |
| CLAIMCHECK | https://github.com/JHU-CLSP/CLAIMCHECK | E4 双向证据审计主实验 | 否，使用现有标签 |
| PeerQA | https://github.com/UKPLab/peerqa 或 https://huggingface.co/datasets/UKPLab/PeerQA | E2 Paper-RAG 检索与证据定位 | 否 |
| OpenReview ICLR/NeurIPS 子集 | https://docs.openreview.net/getting-started/using-the-api | E1 候选生成、E6 端到端案例 | 否，使用公开评审和决策 |
| 本地参考论文库 | `参考论文/整合去重_论文库/PDF_MD_成对论文库/` | E3 受控 Literature-RAG | 否 |

OpenReview 当前默认使用 API 2；部分 2024 年以前会议仍可能需要 API 1。下载时保存 venue、paper id、版本、review id 和抓取日期，避免数据漂移。

### 5.2 推荐辅助数据

| 数据源 | 获取地址 | 用途 |
| --- | --- | --- |
| SubstanReview | https://github.com/YanzhuGuo/SubstanReview | 评审意见证据充分性辅助实验 |
| RottenReviews | https://github.com/Reviewerly-Inc/RottenReviews | 最终报告 factuality、vagueness、actionability 辅助评价 |
| PeerRead | https://github.com/allenai/PeerRead | 仅用于可选分类实验 |

### 5.3 数据划分原则

1. 按论文划分训练、验证和测试，不能让同一论文的弱点跨集合；
2. 主结果只报告现成 gold 标签，不以模型生成标签替代 gold；
3. OpenReview 端到端结果作为真实案例和辅助量化，不冒充严格 gold；
4. Literature-RAG 主实验采用受控文献集合，并记录每次索引快照；
5. 数据和模型输出均保存 `paper_id`、`candidate_id`、`query_plan`、`retrieved_evidence`、`decision` 和运行配置。

## 6. Baseline 设计

### 6.1 候选弱点生成

| 编号 | Baseline | 目的 |
| --- | --- | --- |
| G0 | Direct LLM Review | 最低成本生成基线 |
| G1 | Structured Prompt Reviewer | 检验结构化提示的收益 |
| G2 | Three Reviewer Agents / MARG-lite | 检验多角度候选生成收益 |

候选生成不是核心创新，只测候选数量、有效弱点覆盖率、具体性与泛化率。

### 6.2 Paper-RAG

| 编号 | Baseline |
| --- | --- |
| P0 | BM25 |
| P1 | Dense Retrieval |
| P2 | BM25 + Dense + RRF |
| P3 | P2 + Section Prior |
| P4 | P3 + Evidence-Type Prior + Neighbor Expansion（本文） |

### 6.3 Literature-RAG

| 编号 | Baseline |
| --- | --- |
| L0 | Keyword / Metadata Search |
| L1 | Dense Literature Retrieval |
| L2 | Hybrid Literature Retrieval |
| L3 | Hybrid + Year/Topic/Metadata Filter（本文） |

### 6.4 双向证据审计

| 编号 | Baseline |
| --- | --- |
| A0 | No Verification |
| A1 | LLM-only Judge |
| A2 | Single Judge + Paper-RAG |
| A3 | Support-only + Adjudicator |
| A4 | Support + Refutation + Adjudicator（本文） |

### 6.5 Meta-Reviewer Ranker

| 编号 | Baseline |
| --- | --- |
| K0 | 原始生成顺序 |
| K1 | Severity-only |
| K2 | Evidence-only |
| K3 | Evidence-aware Ranker |
| K4 | 双 RAG Meta-Reviewer Ranker（本文） |

### 6.6 端到端系统

1. Direct LLM Review；
2. Three Reviewer Agents；
3. Reviewer Agents + Single Judge Paper-RAG；
4. Full EviReview-Lite。

## 7. 实验流程

### E0：数据与协议准备

1. 下载 CLAIMCHECK、PeerQA 和 OpenReview 子集；
2. 将论文解析为 section、paragraph、table/caption、appendix；
3. 建立 Paper-RAG 与本地 Literature-RAG 索引；
4. 固定测试集、随机种子、模型版本、Prompt 和 token 预算；
5. 定义统一 JSONL 运行记录。

输出：可复现实验清单、数据审计报告和索引快照。

### E1：候选弱点生成诊断实验

对比 G0–G2。每篇论文限制相同候选数量和 token 预算，测量：

- Weakness Recall / Coverage；
- Valid Candidate Precision；
- Specificity；
- Generic Rate；
- 候选重复率；
- 成本和延迟。

该实验只证明上游候选池质量，不作为主要创新结论。

### E2：结构与证据类型感知 Paper-RAG

在 PeerQA 和 CLAIMCHECK 可定位证据样本上对比 P0–P4。

指标：

- Recall@3/5/10；
- MRR；
- nDCG@5；
- Section Match；
- Evidence-Type Match；
- 检索延迟。

消融：

- 去掉 Section Prior；
- 去掉 Evidence-Type Prior；
- 去掉 Neighbor Expansion；
- 仅 BM25 / 仅 Dense。

### E3：受控 Literature-RAG

从本地语料中构建可复现候选集合，对 `novelty`、`missing_baseline` 和 `related_work` 查询对比 L0–L3。

指标：

- Recall@5/10；
- MRR；
- Literature Relevance@K；
- Citation Validity Rate；
- Temporal Validity；
- 查询延迟。

该实验规模控制在 20–30 个查询、每个查询一个固定候选文献池，不做大规模在线学术搜索。

### E4：双向证据审计主实验

使用 CLAIMCHECK 为主，SubstanReview 为辅助，对比 A0–A4。

指标：

- Valid-Issue Precision；
- Covered/Refuted Recall；
- Adjudication Macro-F1；
- Evidence Attribution Accuracy；
- False-Keep Rate；
- `uncertain` Rate；
- 每条候选的成本和延迟。

关键消融：A2 与 A4 的差异直接验证双向审计价值；A3 与 A4 的差异验证 Refutation Agent 价值。

### E5：Meta-Reviewer Ranker

在同一论文的候选弱点集合上对比 K0–K4。

指标：

- Top-3 / Top-5 Precision；
- nDCG@5；
- Major Weakness Coverage；
- Redundancy Rate；
- Evidence Coverage；
- Confidence Calibration。

消融：

- 无证据分；
- 无 Literature-RAG 分；
- 无重复惩罚；
- 无不确定性惩罚。

### E6：端到端自动评审

在固定 OpenReview 小样本上运行四个端到端系统。最终报告只包含自动保留或自动改写后的 Top-K 意见。

指标：

- Valid Weakness Precision；
- Evidence Coverage；
- Generic Rate；
- False-Keep Rate；
- Redundancy Rate；
- Citation Validity；
- 成本、延迟和稳定性。

报告 3–5 个完整案例，展示候选意见、检索证据、支持/反驳案例、裁决和最终排序。

## 8. 实验成功标准

所有主实验预先固定主指标，使用同一测试集上的配对 bootstrap 或配对显著性检验，报告 95% 置信区间，而不是只比较单次均值。

| 实验 | 成功标准 |
| --- | --- |
| E2 Paper-RAG | P4 相对最强非结构 Baseline（P0–P2）的 Evidence Recall@5 和 nDCG@5 显著提升；目标 Recall@5 至少提升 5 个百分点；Evidence-Type Match 至少提升 10 个百分点；延迟不超过 P2 的 2 倍 |
| E3 Literature-RAG | Citation Validity Rate ≥ 95%；L3 的 Recall@10 / MRR 显著优于 L0；受控语料 Recall@10 目标 ≥ 0.70 |
| E4 双向审计 | A4 相对 A2 的 Valid-Issue Precision 和 Covered/Refuted Recall 均提升至少 5 个百分点，或其中一项提升至少 8 个百分点且另一项非劣于 2 个百分点；False-Keep Rate 相对降低至少 20%；Evidence Attribution Accuracy 目标 ≥ 0.75；成本不超过 A2 的 2.5 倍 |
| E5 Ranker | K4 相对 K1/K2 的 Top-5 Precision 提升至少 5 个百分点；Redundancy Rate 相对降低至少 20%；Major Weakness Coverage 非劣于 3 个百分点 |
| E6 端到端 | Full EviReview-Lite 相对 Direct LLM 和 Three Reviewer Agents 提高有效弱点精度与证据覆盖率，并降低 False-Keep、Generic 和重复率；最终报告不得包含无法定位来源的外部引用 |

总体成功条件：

1. E4 双向审计必须通过主成功标准；
2. E2、E3、E5 中至少再有一项通过主成功标准；
3. 若 E4 未通过，则论文应收窄为“结构感知检索与证据化排序研究”，不能声称双向审计有效；
4. 分类实验不影响主课题成功与否。

## 9. 推荐后端技术栈

| 层 | 技术 |
| --- | --- |
| 语言与实验 | Python 3.11、Jupyter/脚本、pytest |
| Agent 编排 | LangGraph，或轻量自定义状态机；固定流程优先，不需要复杂动态路由 |
| LLM 接口 | OpenAI-compatible adapter，模型名和密钥仅由环境变量配置 |
| 数据模型 | Pydantic |
| API | FastAPI，仅用于后端实验服务化 |
| 稀疏检索 | BM25 / Pyserini 或 rank-bm25 |
| Dense Embedding | sentence-transformers，优先科学文献向量模型 |
| 向量库 | Qdrant；小规模实验可先用 FAISS |
| 融合与排序 | RRF + 可解释线性 Ranker；必要时再增加 cross-encoder reranker |
| 数据与追踪 | JSONL/Parquet、SQLite/PostgreSQL；MLflow 或本地 manifest |
| PDF 解析 | MinerU 或 GROBID；已有 Markdown 优先 |
| 统计分析 | scipy、statsmodels、pandas |

工程架构可采用常规后端分层：

```text
controller/     API 与实验入口
service/        评审流程与实验用例编排
agent/          八个 Agent 的独立实现和 Prompt
rag/            Paper-RAG、Literature-RAG、索引与检索
dao/            数据集、运行记录、索引元数据访问
models/         Pydantic 数据模型
conf/           模型、检索、实验配置
evaluation/     指标、显著性检验和表格生成
scripts/        数据准备、运行和复现实验脚本
tests/          单元、集成和回归测试
```

## 10. 实施顺序与工作量边界

### 第一阶段：可复现实验底座

- 完成数据下载、解析、统一 schema 和索引；
- 完成 G0–G2、P0–P2；
- 输出 E0 和 E1。

### 第二阶段：核心检索创新

- 实现 Query Planner、Section Prior、Evidence-Type Prior；
- 完成 P3/P4 和 E2；
- 搭建受控 Literature-RAG，完成 E3。

### 第三阶段：核心审计创新

- 实现 Support、Refutation、Adjudicator；
- 完成 A1–A4、E4 和消融；
- 优先保证标签映射、证据引用和运行轨迹可复查。

### 第四阶段：排序与端到端

- 实现 K0–K4；
- 完成 E5 与 E6；
- 生成论文表格、案例和误差分析。

### 明确不做

- 不训练或微调大模型；
- 不做 Web-scale Literature-RAG；
- 不复现所有现有自动评审系统；
- 不把自动接收/拒绝分类作为主要创新；
- 不设置人工复核或人工决策流程；
- 不把 LLM-as-Judge 单独作为最终 gold 标准。

## 11. 风险与控制

| 风险 | 控制方法 |
| --- | --- |
| OpenReview 数据格式和版本变化 | 保存原始 JSON、API 版本、抓取日期和转换脚本 |
| PDF 解析破坏表格或章节 | 使用已有 Markdown；保留页码、标题和邻近块 |
| CLAIMCHECK 标签与系统标签不完全一致 | 预先编写固定映射表，并报告不能映射的样本 |
| LLM 输出不稳定 | 固定 Prompt、模型版本、温度和随机种子；至少重复三次 |
| LLM Judge 偏差 | 主实验优先使用现有 gold；Judge 只作辅助指标 |
| Literature-RAG 引用错误 | 每条外部证据强制包含文献 ID/URL 和片段；计算 Citation Validity |
| 双向审计成本过高 | 固定候选上限、共享索引、检索缓存、批量推理和统一 token 预算 |

## 12. 最终论文可使用的创新点表述

1. **提出评审意见级双向证据审计机制。** 针对每条候选弱点分别构建支持与反驳证据案例，并通过统一裁决协议自动执行保留、改写、删除或不确定判断，以减少自动评审中的误读和错误保留。
2. **提出结构与证据类型感知的双 RAG 检索机制。** Paper-RAG 根据弱点类型优先检索目标章节和所需证据类型；受控 Literature-RAG 为新颖性、遗漏 baseline 和相关工作意见提供可追溯外部证据。
3. **提出双 RAG 证据驱动的 Meta-Reviewer Ranker。** 综合裁决结果、证据充分性、严重性、具体性、可操作性和重复度，自动过滤并排序 Top-K 核心弱点，生成带证据与置信度的结构化评审报告。

候选弱点生成是必要的系统组成和 Baseline，但不单独作为创新点。接收倾向分类最多作为辅助实验，不应表述为自动录用决策能力。

## 13. 研究工具与限制说明

本报告结合本地 PDF、MinerU Markdown、精读笔记以及官方论文和数据集页面进行核验。`arxiv-reader` 运行所需的 `LLM_API_KEY` 与 `LLM_BASE_URL` 当前未配置，因此本轮未调用其 LLM 阅读管线，改用本地已解析全文和官方页面完成核验。该限制不影响本文献位置盘点和实验设计，但正式撰写论文前仍应逐条导出规范 BibTeX 并再次核对版本与作者信息。
