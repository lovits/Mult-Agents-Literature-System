# EviReview-Lite 创新点、数据源与 Baseline 重定稿

日期：2026-06-13
唯一设计依据：`新版完整开题报告_EviReview-Lite_基于证据校验的学术论文自动评审系统.md`

## 1. 重新定位

保留原开题报告基本流程：

```text
候选弱点生成
  -> 结构感知 Paper-RAG
  -> Weakness Evidence Verifier
  -> Evidence-aware Ranker
  -> 带证据锚点的 Top-K 评审报告
```

研究范围调整为：

- 保留三个核心创新；
- 候选弱点生成是必要模块和 baseline，不单独作为创新；
- 接收倾向分类降为可选辅助实验；
- Literature-RAG、双向证据陪审、多模态和代码执行不进入主线；
- 不要求构建 300–500 条人工标注集；
- 主实验优先使用已有公开标签，只补充 50–100 条人工案例复核。

推荐题目：

> **基于证据校验与结构感知 RAG 的轻量级学术论文弱点评审研究**

## 2. 核心创新点

### 创新点一：评审弱点级证据校验机制

系统以单条候选 weakness 为最小验证单位，不直接相信 LLM 生成的批评。系统为 weakness 检索论文内部证据，并输出：

```text
Supported
Partially Supported
Covered
Generic
Unsupported
Contradicted
```

每条结果包含标签、置信度、evidence block ID、判断理由及必要的改写版本。

与普通自动评审的差异：

- 普通方法主要评价完整 review 是否流畅或有帮助；
- 本方法直接判断每条批评是否有论文证据；
- 可以单独统计错误意见、已覆盖问题和泛化意见。

主要数据：CLAIMCHECK、PeerReview Bench、少量 OpenReview 案例复核。

主要指标：Macro-F1、Supported Precision、Unsupported/Contradicted Recall、Evidence Attribution Accuracy、Evidence Coverage。

### 创新点二：面向弱点评审的结构感知 Hybrid Paper-RAG

普通 RAG 主要按文本相似度检索。本文根据 weakness 类型设置章节先验：

| Weakness 类型 | 优先章节 |
| --- | --- |
| method | Method、Approach、Algorithm |
| experiment | Experiments、Results、Ablation |
| reproducibility | Implementation、Appendix、Experimental Setup |
| clarity | 对应目标章节及邻近块 |

检索流程：

```text
Weakness
  -> Query Planner
  -> BM25 + Dense
  -> RRF 融合
  -> Section-aware Rerank
  -> 邻近证据块扩展
  -> Evidence Bundle
```

主要数据：PeerQA-XT、CLAIMCHECK、OpenReview 小样本。

主要指标：Recall@1/3/5、MRR、nDCG@K、Section Match、检索延迟。

### 创新点三：证据感知的弱点过滤与 Top-K 排序

Verifier 完成后，Ranker：

1. 删除 Unsupported、Contradicted 和 Covered；
2. 降权 Generic；
3. 合并同一论文内的重复 weakness；
4. 综合证据强度、严重性、具体性、可操作性和置信度；
5. 输出 Top-3 或 Top-5 核心问题。

推荐排序公式：

```text
score(w) =
  0.35 * evidence_strength
  + 0.25 * severity
  + 0.20 * specificity
  + 0.10 * actionability
  + 0.10 * confidence
  - redundancy_penalty
```

主要数据：CLAIMCHECK、PeerReview Bench、50–100 条 OpenReview 候选 weakness 抽样复核。

主要指标：Top-3/5 Precision、nDCG、Major Weakness Coverage、Redundancy Rate、Evidence Coverage。

### 可选辅助实验：证据化特征用于接收倾向分类

该部分不作为核心创新。只用于回答：

> 经过证据校验的 weakness 特征是否具有下游解释价值？

只保留三个分类 baseline：

1. Text TF-IDF + Logistic Regression；
2. Evidence Features + Logistic Regression；
3. Text + Evidence Features + Logistic Regression。

数据使用 PeerRead 或 OpenReview。若结果未超过文本 baseline，保留为负结果，不影响主线成立。

## 3. 候选弱点生成的定位

候选弱点生成是系统必需模块，但不作为独立核心创新。MARG、ReviewAgents、AgentReview 已使用多角色或多 Agent 生成评审意见。仅增加 Method Reviewer、Experiment Reviewer 和 Clarity Reviewer，创新性不足。

本项目将其定位为：

- 高召回候选池生成器；
- 证据校验模块的上游输入；
- 验证后续过滤和排序是否有效的生成 baseline。

只实现三种生成方法：

1. Direct LLM Weakness；
2. Structured Prompt Weakness；
3. MARG-lite。

不做 Full MARG 严格复现，不做 Novelty Reviewer，不做动态多 Agent 讨论。

## 4. 数据源选择

### 4.1 必做数据源

| 数据源 | 获取位置 | 用途 | 人工标注需求 |
| --- | --- | --- | --- |
| CLAIMCHECK | `https://github.com/JHU-CLSP/CLAIMCHECK` | weakness 验证、证据关联、标签预测 | 不需要 |
| PeerQA-XT | `https://huggingface.co/datasets/UKPLab/PeerQA-XT` | Paper-RAG 检索实验 | 不需要 |
| OpenReview ICLR 小样本 | `https://docs.openreview.net/getting-started/using-the-api` | 候选生成与端到端报告案例 | 少量抽样复核 |

### 4.2 推荐辅助数据源

| 数据源 | 获取位置 | 用途 | 优先级 |
| --- | --- | --- | --- |
| PeerReview Bench | `https://huggingface.co/datasets/nlile/peerreview-bench` | correctness、significance、evidence 辅助评价 | 中 |
| SubstanReview | `https://github.com/YanzhuGuo/SubstanReview` | review claim-evidence substantiation | 中 |
| PeerRead | `https://github.com/allenai/PeerRead` | 可选分类实验 | 低 |
| MARG 代码 | `https://github.com/allenai/marg-reviewer` | MARG-lite 流程参考 | 中 |

### 4.3 不进入主线的数据

- PRISM：若缺少稳定公开数据入口，只作为相关工作；
- DeepReview-13K：仅在确定公开数据和字段后用于辅助分类；
- RottenReviews：与论文内证据校验主线距离较远；
- 大规模 OpenReview Raw：清洗和解析成本过高；
- Literature-RAG 外部语料：容易扩大范围并引入检索评估困难。

### 4.4 推荐数据规模

| 实验 | 推荐规模 |
| --- | ---: |
| PeerQA-XT 检索调试 | 50 条 |
| PeerQA-XT 正式检索 | 500–1000 条或固定 test split |
| CLAIMCHECK 主验证 | 官方 main split |
| OpenReview 候选生成 | 30–50 篇论文 |
| 人工抽样复核 | 50–100 条 weakness |
| 辅助分类 | PeerRead 官方 split |

不建议重新人工标注 300–500 条 weakness。现成标签足以支撑主实验，人工工作只用于系统特定案例复核。

## 5. 精简 Baseline

### 5.1 候选生成 Baseline

| 编号 | 方法 | 目的 |
| --- | --- | --- |
| G0 | Direct LLM Weakness | 最低生成基线 |
| G1 | Structured Prompt Weakness | 控制结构化 prompt 贡献 |
| G2 | MARG-lite | 控制轻量多 Agent 生成贡献 |

最终选择 Recall 较高且成本可接受的方法，固定作为后续验证实验输入。

### 5.2 检索 Baseline

| 编号 | 方法 | 目的 |
| --- | --- | --- |
| R0 | BM25 | 稀疏检索基础线 |
| R1 | Dense Retrieval | 语义检索基础线 |
| R2 | Hybrid RRF | 验证融合是否有效 |
| R3 | Hybrid RRF + Section-aware Rerank | 本文方法 |

邻近块扩展作为 R3 的消融，不单列主 baseline。

### 5.3 Evidence Verifier Baseline

| 编号 | 方法 | 目的 |
| --- | --- | --- |
| V0 | No Verification | 证明验证模块必要性 |
| V1 | LLM-only Judge | 证明检索证据是否必要 |
| V2 | BM25-RAG + Evidence Judge | 基础 RAG verifier |
| V3 | Section-aware Hybrid RAG + Evidence Judge | 本文方法 |

不增加 Support、Refutation 和 Adjudicator，避免偏离指定开题报告并扩大工作量。

### 5.4 Ranker Baseline

| 编号 | 方法 | 目的 |
| --- | --- | --- |
| K0 | Original Order | 不排序基线 |
| K1 | Severity-only | 控制严重性贡献 |
| K2 | Evidence-only | 控制证据强度贡献 |
| K3 | Evidence-aware Ranker | 本文方法 |

### 5.5 可选分类 Baseline

| 编号 | 方法 |
| --- | --- |
| C0 | Text TF-IDF + Logistic Regression |
| C1 | Evidence Features + Logistic Regression |
| C2 | Text + Evidence Features + Logistic Regression |

不做 SVM、Random Forest、大模型分类器和多种 embedding 网格比较。

## 6. 主实验矩阵

### 实验一：候选生成诊断

目的：选择稳定的候选生成器，为后续实验固定输入。

比较：G0、G1、G2。

指标：Weakness Recall、Generic Rate、Redundancy Rate、Average Weakness Count、Token/Cost。

该实验不是核心贡献实验。

### 实验二：结构感知 Paper-RAG

目的：验证章节先验是否提高论文内证据检索。

比较：R0、R1、R2、R3。

数据：PeerQA-XT + CLAIMCHECK。

指标：Recall@K、MRR、nDCG@K、Section Match、延迟。

消融：去掉 section-aware rerank；去掉邻近块扩展。

### 实验三：Weakness Evidence Verification

目的：验证 Paper-RAG 是否能提高 weakness 标签判断和证据归因。

比较：V0、V1、V2、V3。

数据：CLAIMCHECK 为主，PeerReview Bench/SubstanReview 为辅助。

指标：Macro-F1、Supported Precision、Unsupported/Contradicted Recall、Evidence Attribution Accuracy、Evidence Coverage。

消融：BM25 替代 Hybrid；去掉 section-aware rerank；不提供 evidence 给 Judge。

### 实验四：Evidence-aware Top-K Ranking

目的：验证过滤和证据感知排序能否输出更少、更准的核心问题。

比较：K0、K1、K2、K3。

数据：CLAIMCHECK + 少量 OpenReview 抽样复核。

指标：Top-3/5 Precision、Major Weakness Coverage、Redundancy Rate、Evidence Coverage、Actionability 抽样评分。

### 可选实验五：辅助分类

只有主实验完成且时间充足时开展。比较 C0、C1、C2，报告 Macro-F1、AUC 和特征重要性。分类结果只作为证据化中间特征的下游分析。

## 7. 工作量控制

### 必做工作

1. 解析并结构化论文；
2. 实现三种候选生成方法；
3. 实现 BM25、Dense、Hybrid 和 Section-aware Rerank；
4. 实现 Evidence Judge 和六类标签；
5. 实现四种排序方法；
6. 接入三个主数据源；
7. 完成四组实验、三组核心消融和失败分析；
8. 输出端到端带证据评审报告。

以上已经具有足够的硕士论文工作量。

### 明确删除

1. Full MARG 严格复现；
2. Support、Refutation、Adjudicator 多 Agent 审计；
3. Literature-RAG 主实验；
4. Novelty Reviewer；
5. 多模态审稿；
6. 代码执行验证；
7. 大规模人工标注；
8. 多种分类器和 embedding 网格比较。

## 8. 推荐完成顺序

| 周期 | 工作 | 验收产物 |
| --- | --- | --- |
| 第 1–2 周 | 数据接入、论文结构化、统一 schema | 数据 manifest、解析样例 |
| 第 3–4 周 | BM25、Dense、Hybrid、Section-aware RAG | 实验二检索主表 |
| 第 5 周 | G0/G1/G2 候选生成 | 实验一诊断表 |
| 第 6–8 周 | Evidence Judge、V0–V3 | 实验三验证主表 |
| 第 9–10 周 | 去重、K0–K3、Top-K 报告 | 实验四排序主表 |
| 第 11 周 | 消融、失败案例、OpenReview 抽样复核 | 消融与案例分析 |
| 第 12 周 | 端到端复跑、结果表生成 | 可复现实验产物 |
| 第 13–14 周 | 论文实验章节和系统章节 | 论文初稿 |
| 时间充足 | 辅助分类 | 可选分类附表 |

## 9. 最终推荐方案

最稳妥的论文贡献组合：

> **Weakness-level Evidence Verification + Section-aware Hybrid Paper-RAG + Evidence-aware Top-K Ranking**

候选弱点生成保留为必要上游模块，分类保留为可选辅助实验。

该组合有明确的生成、检索、验证和排序链路；每个创新点均有公开数据、baseline 和指标；不依赖大规模人工标注；工作量足够，但不需要实现过多 Agent 或外部检索系统。
