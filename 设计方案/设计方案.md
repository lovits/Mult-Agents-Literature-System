# EviReview-Lite 最终 Agent-RAG 创新与评审流程

日期：2026-06-13
状态：最终研究设计基线
设计原则：自动完成论文评审，不设置人工复核流程

## 1. 最终研究定位

系统以自动生成的候选弱点为基本单位，通过论文内部证据和外部文献证据进行双向审计，自动完成弱点过滤、改写、去重、排序、置信度标注与结构化评审报告生成。

最终主线：

```text
论文解析与结构识别
  -> 多维候选弱点生成
  -> Paper-RAG / Literature-RAG 检索
  -> Support / Refutation 双向证据审计
  -> Evidence Adjudicator 自动裁决
  -> Meta-Reviewer Ranker 去重、过滤、排序与置信度标注
  -> Top-K 自动评审报告
```

系统不包含 `human-check`。证据不足或冲突无法消解的意见标记为 `uncertain`，保留在审计日志中，但不进入核心 Top-K 评审结论。

## 2. 最终核心创新点

### 创新点一：评审意见级双向证据审计

普通自动评审直接生成评审文本，原 EviReview-Lite 只使用单一 Evidence Judge 判断候选意见。本文进一步为每条候选意见固定构建支持与反驳两类证据案例：

```text
Candidate Weakness
  -> Support Case
  -> Refutation Case
  -> Evidence Adjudicator
  -> keep / rewrite / reject / uncertain
```

#### Support Case

寻找证明候选意见成立的证据，例如：

- 实验部分确实缺少对应消融；
- 结论超过当前实验结果能够支持的范围；
- 方法关键步骤缺少实现说明。

#### Refutation Case

主动寻找证明候选意见不成立或论文已覆盖问题的证据，例如：

- 附录已经提供消融实验；
- 方法章节已经说明实现细节；
- 候选意见误读了实验设置。

#### 自动裁决动作

| 动作 | 条件 | 后续处理 |
| --- | --- | --- |
| `keep` | 支持证据充分，反驳证据不足 | 保留 |
| `rewrite` | 问题部分成立或表述过强 | 自动收窄后保留 |
| `reject` | 已覆盖、误读、无证据或被反驳 | 删除 |
| `uncertain` | 证据不足或冲突无法消解 | 不进入 Top-K，仅保留日志 |

不设置人工复核。`uncertain` 是系统自动拒绝形成确定评审结论的状态。

主要指标：

- Valid-Issue Precision；
- Covered/Refuted Recall；
- Evidence Attribution Accuracy；
- Adjudication Macro-F1；
- Uncertain Rate；
- False-Keep Rate。

### 创新点二：结构与证据类型感知的双 RAG 检索

系统包含两套职责不同的 RAG：

1. **Paper-RAG**：检索当前论文内部证据；
2. **Literature-RAG**：检索外部相关论文，验证新颖性、遗漏 baseline 和相关工作比较。

#### Paper-RAG

Query Planner 为候选意见声明目标章节和预期证据类型：

```json
{
  "aspect": "experiment",
  "target": "retrieval module",
  "expected_sections": ["Experiments", "Ablation", "Appendix"],
  "expected_evidence_types": ["table", "paragraph", "implementation_detail"],
  "queries": ["retrieval module ablation", "remove retriever component"]
}
```

检索流程：

```text
BM25 + Dense
  -> RRF Fusion
  -> Section Prior
  -> Evidence-Type Prior
  -> Neighbor Expansion
  -> Paper Evidence Bundle
```

#### Literature-RAG

Literature-RAG 不对所有候选意见运行，只处理以下固定评审类型：

- `novelty`
- `related_work`
- `missing_baseline`
- `external_comparison`

这是按评审任务类型确定的固定职责边界，不是争议触发或动态升级。

检索流程：

```text
Contribution / Baseline Query
  -> Local Reference Corpus + Scholarly Metadata Search
  -> BM25 + Dense
  -> Year / Topic / Citation Metadata Filter
  -> Literature Evidence Bundle
```

Literature-RAG 输出必须包含论文标题、年份、来源、链接或文献 ID，以及与候选意见相关的证据片段。

主要指标：

- Recall@K；
- MRR；
- nDCG@K；
- Section Match；
- Evidence-Type Match；
- Literature Relevance@K；
- Citation Validity Rate。

### 创新点三：双 RAG 证据驱动的 Meta-Reviewer Ranker

Meta-Reviewer Ranker 将弱点过滤、论文内去重、排序和置信度标注统一设计，而不是单独生成新的评审意见。

输入：

```text
Candidate Weakness
+ Paper Evidence
+ Literature Evidence
+ Support Case
+ Refutation Case
+ Adjudication Result
```

主要职责：

1. 删除 `reject` 和 `uncertain` 意见；
2. 使用裁决结果自动改写 `rewrite` 意见；
3. 只在同一论文内合并语义和证据范围重复的意见；
4. 综合证据充分性、有效概率、严重性、具体性和可操作性排序；
5. 输出置信度等级和 Top-K 核心弱点；
6. 生成最终结构化评审报告。

推荐排序公式：

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

置信度使用自动等级：

| 等级 | 条件 | 输出位置 |
| --- | --- | --- |
| High | 证据充分、支持与反驳裁决清晰 | Major Weakness |
| Medium | 问题成立但证据或影响范围有限 | Minor Weakness / Question |
| Low | 证据不足或冲突未消解 | 不进入最终报告 |

主要指标：

- Top-3/5 Precision；
- Major Weakness Coverage；
- nDCG；
- Redundancy Rate；
- Evidence Coverage；
- Confidence Calibration；
- False-Keep Rate。

## 3. Agent 与普通模块

### 3.1 核心 Agent：8 个

| Agent | 作用 |
| --- | --- |
| Method Reviewer | 生成方法设计类候选弱点 |
| Experiment Reviewer | 生成实验、baseline 和消融类候选弱点 |
| Reproducibility Reviewer | 生成实现和复现类候选弱点 |
| Query Planner | 为 Paper-RAG 和 Literature-RAG 生成查询计划 |
| Support Agent | 构建支持候选意见的证据案例 |
| Refutation Agent | 构建反驳或已覆盖证据案例 |
| Evidence Adjudicator | 自动执行 keep/rewrite/reject/uncertain 裁决 |
| Meta-Reviewer | 去重、排序、置信度标注并生成报告 |

### 3.2 普通算法模块

以下模块不包装成 Agent：

- Paper Parser；
- Evidence-Type Classifier：优先使用规则；
- BM25、Dense、RRF 和 reranker；
- Candidate Normalizer；
- Deduplicator；
- Rank Score Calculator；
- Confidence Score Calculator；
- Metric Evaluator；
- Classification Head。

## 4. 完整自动评审流程

```text
Stage 0 论文解析
  PDF / Markdown
  -> section / paragraph / table caption / appendix
  -> Paper Evidence Index

Stage 1 候选生成
  Method Reviewer
  + Experiment Reviewer
  + Reproducibility Reviewer
  -> Candidate Weakness Pool
  -> Atomic Weaknesses

Stage 2 查询规划与双 RAG
  Query Planner
  -> Paper-RAG：所有 weakness
  -> Literature-RAG：novelty / related_work / missing_baseline / external_comparison
  -> Evidence Bundle

Stage 3 双向证据审计
  Evidence Bundle
  -> Support Agent
  -> Refutation Agent
  -> Evidence Adjudicator
  -> keep / rewrite / reject / uncertain

Stage 4 Meta-Reviewer Ranker
  -> 删除 reject / uncertain
  -> 自动改写 rewrite
  -> 论文内去重
  -> rank score
  -> confidence label
  -> Top-3 / Top-5

Stage 5 自动评审报告
  -> Summary
  -> Major Weaknesses
  -> Minor Weaknesses
  -> Questions
  -> Evidence Anchors
  -> Confidence Statistics
```

## 5. 实验流程

### E1：候选生成诊断

比较：

- Direct LLM；
- Structured Prompt；
- 三 Reviewer Agent。

指标：

- Weakness Recall；
- Generic Rate；
- Redundancy Rate；
- Average Weakness Count；
- Token/Cost。

该实验用于固定候选生成器，不作为核心创新实验。

### E2：Paper-RAG 检索实验

比较：

- BM25；
- Dense；
- Hybrid RRF；
- Hybrid + Section Prior；
- Hybrid + Section + Evidence-Type Prior。

数据：

- PeerQA-XT；
- CLAIMCHECK。

指标：

- Recall@K；
- MRR；
- nDCG@K；
- Section Match；
- Evidence-Type Match。

### E3：Literature-RAG 实验

比较：

- Keyword Search；
- Dense Literature Retrieval；
- Hybrid Literature-RAG；
- Hybrid + Metadata Filter。

建议数据与评价：

- 使用本地参考论文库构建受控语料；
- 从 OpenReview 论文中选择 20–30 条 novelty、missing-baseline 或 related-work 候选意见；
- 使用真实引用和已知相关工作作为检索目标；
- 评价 Literature Recall@K、MRR、Citation Validity 和检索成本。

Literature-RAG 只需完成小规模受控实验，不做大规模在线学术搜索。

### E4：双向证据审计主实验

比较：

- No Verification；
- LLM-only Judge；
- Single Judge + Paper-RAG；
- Support-only + Adjudicator；
- Support + Refutation + Adjudicator。

数据：

- CLAIMCHECK 为主；
- PeerReview Bench / SubstanReview 为辅助；
- OpenReview 案例用于端到端展示。

指标：

- Macro-F1；
- Valid-Issue Precision；
- Covered/Refuted Recall；
- Evidence Attribution Accuracy；
- False-Keep Rate；
- Uncertain Rate；
- Token/Cost。

### E5：Meta-Reviewer Ranker 实验

比较：

- Original Order；
- Severity-only；
- Evidence-only；
- Evidence-aware Ranker；
- Evidence-aware Meta-Reviewer Ranker。

指标：

- Top-3/5 Precision；
- Major Weakness Coverage；
- nDCG；
- Redundancy Rate；
- Evidence Coverage；
- Confidence Calibration；
- 报告压缩率。

### E6：端到端自动评审

比较：

- Direct LLM Review；
- 三 Reviewer Agent；
- Reviewer + Single Judge Paper-RAG；
- 完整 EviReview-Lite。

指标：

- 有效弱点 Precision；
- 主要弱点覆盖率；
- Generic Rate；
- Redundancy Rate；
- Evidence Coverage；
- False-Keep Rate；
- Token、延迟和成本。

## 6. 数据源

| 数据源 | 用途 | 优先级 |
| --- | --- | --- |
| CLAIMCHECK | 双向证据审计主实验 | 必做 |
| PeerQA-XT | Paper-RAG 检索实验 | 必做 |
| OpenReview ICLR 小样本 | 候选生成和端到端评审 | 必做 |
| 本地 `参考论文/` | Literature-RAG 受控语料 | 必做 |
| PeerReview Bench | 审计与排序辅助评价 | 推荐 |
| SubstanReview | 评审意见证据充分性辅助评价 | 推荐 |
| PeerRead | 可选分类实验 | 可选 |

## 7. 工作量控制

### 必做

- 8 个固定 Agent；
- 2 套 RAG；
- E1、E2、E4、E5、E6；
- Literature-RAG 小规模受控 E3；
- 主要消融和失败分析。

### 不做

- 人工复核流程；
- 动态争议升级；
- 自由讨论式 Agent；
- 强化学习；
- 大规模 Literature-RAG 在线抓取；
- 多模态和代码执行；
- 大规模人工标注；
- 自动接收或拒绝分类主线。

## 8. 最终创新表述

最终建议将论文创新点写为：

1. **评审意见级双向证据审计机制**：为每条候选意见分别构建支持与反驳证据案例，并自动执行保留、改写、删除或不确定裁决。
2. **结构与证据类型感知的双 RAG 检索机制**：使用 Paper-RAG 验证论文内部事实，并使用受控 Literature-RAG 验证新颖性、相关工作和遗漏 baseline。
3. **双 RAG 证据驱动的 Meta-Reviewer Ranker**：基于审计结果完成自动过滤、论文内去重、证据感知排序、置信度标注和 Top-K 评审报告生成。

该方案保留 Agent-RAG 自动评审特征，不依赖人工决策，同时通过固定流程、小规模 Literature-RAG 和明确实验边界控制硕士论文工作量。
