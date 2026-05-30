## 一、拟定题目

**基于证据验证的多智能体 RAG 学术论文自动评审与接收倾向分类研究**

也可以根据导师偏好简化为：

**基于多智能体与检索增强生成的学术论文自动评审系统研究**

本文建议使用第一个题目，因为它明确突出“证据验证”这一创新点，避免题目听起来只是普通的 Multi-Agent + RAG 拼接。

## 二、研究背景与意义

随着人工智能、机器学习和自然语言处理领域论文数量快速增长，顶级会议和期刊面临越来越大的审稿压力。传统同行评审依赖人工专家阅读论文、判断创新性、检查实验充分性并给出建设性意见，但该过程存在以下问题：

1. **审稿负担重**：高水平会议投稿量持续增长，审稿人需要在有限时间内处理大量论文。
2. **评审质量不稳定**：不同审稿人背景、经验和认真程度不同，导致评审意见存在较大差异。
3. **评审意见缺少证据约束**：部分评论可能过于泛化，例如“实验不充分”“新颖性不足”，但没有指出具体段落、实验表格或相关文献依据。
4. **自动评审系统仍不可靠**：大语言模型可以生成看似合理的评审意见，但容易出现幻觉、泛化批评、误判论文内容等问题。

因此，自动化论文评审系统的现实目标不应是替代人类审稿人，而应是作为辅助工具，帮助审稿人更快发现潜在问题、提高评审意见的证据性、具体性和可操作性。

近年来，MARG、ReviewAgents、DeepReview、ReviewGrounder、ScholarPeer 等工作尝试使用大语言模型或多智能体系统生成论文评审意见；FactReview、OpenNovelty、NoveltyAgent 等工作强调将论文判断与证据检索、声明验证和相关文献比较结合起来。这些研究说明：自动评审系统不能只追求“生成一段流畅评论”，还需要关注每条评审意见是否有证据支撑、是否可追溯、是否真正帮助作者改进论文。

本课题拟在 MARG 多智能体评审生成框架基础上，设计一个**评审意见级 RAG 证据验证模块**和**证据感知元评审排序模块**，将 MARG 生成的高召回候选评审意见转化为更准确、更具体、更可解释的最终评审报告，并进一步探索证据化评审特征在论文接收倾向分类任务中的作用。

## 三、国内外研究现状与文献综述

### 3.1 早期自动评审数据集与任务定义

早期相关工作主要关注同行评审数据集构建、论文接收预测和评审文本生成。

**PeerRead** 是自动论文评审研究中最经典的数据集之一。该数据集包含约 14.7K 篇论文草稿、对应的 accept/reject 决策，以及其中约 10.7K 条专家评审文本。PeerRead 支持多种任务，包括论文接收预测、评分预测、评审文本生成和评审意见分析。它的价值在于降低了同行评审研究的数据门槛，使研究者可以基于真实评审数据研究自动评审和论文分类问题。其局限在于数据年份较早，与当前 LLM 驱动的自动评审系统存在一定差距。

**Can We Automate Scientific Reviewing?** 将自动论文评审视为长文本到评审文本的生成任务，并提出 ASAP-Review 数据集。该类研究证明了自动生成评审意见的可行性，但早期方法主要依赖摘要式生成模型，难以进行深入的实验检查、新颖性判断和证据定位。

这类研究为本课题提供了两个基础：第一，论文评审可以被形式化为可计算任务；第二，accept/reject 分类和评审生成可以共享论文、评审和决策数据。

### 3.2 LLM 直接评审与可靠性研究

随着大语言模型能力提升，研究者开始探索 LLM 是否能够直接生成有用的论文反馈。

**Can LLMs Provide Useful Feedback on Research Papers?** 对 LLM 生成研究论文反馈进行了大规模实证研究，发现 LLM 在某些情况下能够提供有用建议，但也存在重复、泛化、缺乏专业深度等问题。

**Is LLM a Reliable Reviewer?** 进一步讨论 LLM 作为自动审稿人的可靠性问题。相关研究普遍表明，LLM 能够辅助审稿，但不能简单替代专家判断，尤其在新颖性、事实性、实验结论有效性等方面仍需要外部证据和人工把关。

这类文献支撑本课题的研究动机：单纯让 LLM 直接写 review 不够可靠，需要通过多智能体分工、RAG 检索和证据验证提升输出质量。

### 3.3 多智能体自动评审系统

多智能体方法试图模拟真实审稿流程：不同审稿人从不同角度阅读论文，最后由元评审者整合意见。

#### 3.3.1 MARG：本课题主 baseline

**MARG: Multi-Agent Review Generation for Scientific Papers** 是本课题最适合作为主 baseline 的工作。MARG 使用多个 LLM agent 分别关注实验、清晰度、新颖性/影响力等方面，并通过 refinement 阶段汇总评论。其优势是架构相对简单、代码公开、实验指标明确，适合在硕士课题中复现和改进。

MARG 的关键实验结果如下：

| 方法 | Recall | Precision | Jaccard | 平均评论数 |
|---|---:|---:|---:|---:|
| SARG-B | 7.43 | 1.40 | 1.25 | 19.7 |
| SARG-TP | 10.62 | 4.61 | 3.46 | 11.6 |
| MARG-TP | 8.49 | 5.34 | 3.52 | 8.5 |
| LiZCa | 9.67 | 9.96 | 5.58 | 4.0 |
| **MARG-S** | **15.84** | **4.41** | **3.53** | **19.8** |
| Human | 9.42 | 12.00 | 5.45 | 4.7 |

从结果可以看出，MARG-S 具有最高 Recall，说明它能够发现更多潜在问题；但 Precision 和 Jaccard 不高，且平均生成 19.8 条评论，说明候选意见中存在较多不够准确、重复或泛化的内容。MARG-S 约 71% 评论被评为 specific/very specific，但仍有约 29% 评论属于 generic/very generic。

这正好构成本课题的创新切入点：**保留 MARG 高召回的候选意见生成能力，在其输出端增加 RAG 证据验证和元评审排序模块，提高 Precision、降低 Invalid Rate 和 Generic Rate。**

#### 3.3.2 AgentReview 与 ReviewAgents

**AgentReview** 通过模拟 reviewer、author、area chair 等角色研究 peer review dynamics，更适合用来分析多智能体机制对评审过程的影响。它说明多智能体可以用于模拟复杂审稿互动，但不如 MARG 适合作为本课题主 baseline。

**ReviewAgents** 构建 Review-CoT 数据集，将人类审稿过程拆解为 Summarization、Analysis、Conclusion 等阶段，强调结构化推理过程对评审质量的重要性。它为本课题的结构化评审报告设计提供了参考，但其训练和数据构建成本较高，不建议作为主复现对象。

#### 3.3.3 ReviewGrounder 与 ScholarPeer

**ReviewGrounder** 提出 rubric-guided、tool-integrated 的多智能体评审框架，并构建 ReviewBench，从 Core Contribution Accuracy、Results Interpretation、Comparative Analysis、Evidence-Based Critique、Critique Clarity、Completeness Coverage、Constructive Tone、False or Contradictory Claims 等维度评价评审质量。ReviewGrounder 的评估体系很有参考价值，同时其局限性部分提到尚未探索 LLM-based meta-reviewers 和 iterative feedback loops，这与本课题的 Meta-Reviewer Ranker 思路相符。

**ScholarPeer** 是一个 search-enabled multi-agent framework，包含 historian agent、baseline scout agent、Q&A agent，试图解决自动评审中的“真空评审”问题，即模型不了解最新领域发展和遗漏 baseline。ScholarPeer 与本课题方向接近，但工程依赖更重，评估也更依赖搜索增强 judge 和较新模型。因此本课题将其作为强相关工作，而不是主 baseline。

### 3.4 RAG、证据验证与新颖性评估

自动评审系统的关键问题不是“能否生成评论”，而是“评论是否成立”。因此，RAG 和证据验证成为自动评审的重要发展方向。

**FactReview** 将自动评审转化为 evidence-grounded claim assessment。它首先抽取论文中的主要 claim、实验结果、数据集、baseline 和指标，然后检索相关文献，并在有代码时执行仓库验证实验结果。FactReview 为每个 claim 输出 Supported、Supported by the paper、Partially supported、In conflict、Inconclusive 等标签，并生成带证据链接的评审报告。它证明了自动评审应当从“文本生成”走向“声明级证据验证”。

**OpenNovelty** 和 **NoveltyAgent** 关注论文新颖性评估。它们将论文贡献拆解为多个 novelty point 或 contribution claim，再检索相关工作进行逐点比较，并要求新颖性判断带有真实论文引用和证据片段。这对本课题的启发是：RAG 应该围绕具体评审意见或贡献点进行细粒度检索，而不是简单检索一批相关论文作为上下文。

因此，本课题提出的 RAG 模块并不是普通的“检索增强生成”，而是**评审意见级证据验证**：以 MARG 输出的每条候选评论为单位，检索论文内部证据和外部文献证据，判断该评论是否有效、是否已被论文解决、是否存在幻觉或泛化。

### 3.5 评审质量评估与分类预测

自动评审系统需要可量化的评估指标。

MARG 提供了 Recall、Precision、Jaccard、评论数和 Specificity 等指标，适合作为主实验指标。

**RottenReviews** 提供超过 15,000 个投稿/评审数据，以及 700 多个人工标注 paper-review pairs，覆盖 13 个评审质量维度，包括 Factuality、Vagueness、Actionability、Overall Quality 等。它适合作为本课题的辅助评估数据集，用于验证系统是否提升评论事实性、具体性和可操作性。

**DeepReview-13K** 包含 ICLR 2024/2025 论文、评分、接收决策和结构化 reasoning，支持 Decision Accuracy、Decision F1、Rating MSE/MAE、Spearman 等指标。它适合用于接收倾向分类和评分预测扩展实验。

综上，现有研究已经证明 LLM 和多智能体能够生成评审意见，RAG 和证据验证能够提升判断可信度，但仍缺少一个简单、可复现、可量化的框架，将多智能体生成的候选评审意见进行逐条证据验证和元评审排序。本课题正是针对这一空白展开。

## 四、研究问题与研究目标

### 4.1 研究问题

本课题关注以下研究问题：

1. 如何在 MARG 高召回多智能体评审生成框架基础上，提高自动评审意见的精准率和证据性？
2. 如何利用 RAG 对每条评审意见进行论文内证据和外部文献证据验证？
3. 如何设计元评审排序机制，将候选评论整合为少量高质量、可追溯、可操作的核心问题？
4. 证据化评审特征是否能够辅助论文 Accept/Reject 分类，提高分类可解释性？

### 4.2 研究目标

本课题拟实现以下目标：

1. 复现或对齐 MARG-S baseline，在 ARIES 数据集上获得候选评审意见。
2. 设计评审意见级 RAG Evidence Verifier，对每条候选评论输出有效性标签、证据和置信度。
3. 设计 Meta-Reviewer Ranker，对有效评论进行去重、排序和结构化组织。
4. 在 ARIES 上比较改进前后 Precision、Recall、Jaccard、Generic Rate、Evidence Coverage、Top-K Precision 等指标。
5. 在 PeerRead 或 DeepReview-13K 上探索证据化评审特征对 Accept/Reject 分类的作用。

## 五、Baseline 与改进思路

### 5.1 主 baseline：MARG-S

本课题的主 baseline 是 MARG-S。

选择 MARG-S 的原因：

| 维度 | 说明 |
|---|---|
| 架构简单 | 多 agent prompt 流程，不需要训练大模型 |
| 代码与数据较可复现 | MARG 有公开代码，使用 ARIES 数据评估 |
| 指标明确 | Recall、Precision、Jaccard、评论数、Specificity |
| 缺陷明确 | Recall 高但 Precision 低，评论数多，仍有泛化评论 |
| 改进自然 | 在输出端加入 RAG Verifier 和 Meta-Ranker，不破坏原系统 |

### 5.2 对比方法

实验中建议设置以下对比：

| 方法 | 说明 |
|---|---|
| GPT-4/强 LLM Direct Review | 单模型直接生成评审 |
| MARG-S | 主 baseline |
| MARG-S + LLM-only Filter | 不使用检索，只让 LLM 判断评论是否有效 |
| MARG-S + Paper-RAG Verifier | 只检索论文内部证据 |
| MARG-S + Paper-RAG + Literature-RAG | 同时检索论文内部证据和外部文献 |
| Ours Full | Evidence Verifier + Meta-Reviewer Ranker |

### 5.3 改进总体思路

MARG 负责“生成候选问题”，本文系统负责“验证、筛选、排序和解释问题”。

```text
输入论文 PDF
   ↓
Paper Parser & Indexer
   ↓
MARG-S 多 Agent 生成候选评审意见
   ↓
RAG Evidence Verifier 逐条证据验证
   ↓
Meta-Reviewer Ranker 去重、排序、置信度标注
   ↓
结构化评审报告
   ↓
可选：接收倾向分类
```

## 六、系统架构设计

### 6.1 总体架构

```text
                 ┌──────────────────────┐
                 │     输入论文 PDF      │
                 └──────────┬───────────┘
                            │
                            ▼
        ┌────────────────────────────────────┐
        │ Stage 0: Paper Parser & Indexer    │
        │ - PDF/text 解析                    │
        │ - section/paragraph/table 切分      │
        │ - 构建 BM25 + 向量索引              │
        │ - 抽取 claims/datasets/baselines    │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │ Stage 1: MARG Candidate Generation │
        │ - Experiment Reviewer Agent        │
        │ - Clarity Reviewer Agent           │
        │ - Novelty Reviewer Agent           │
        │ - Refinement Agent                 │
        │ 输出候选评论 C={c1,...,cn}          │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │ Stage 2: Evidence-aware RAG Verifier│
        │ - Query Rewriter Agent             │
        │ - Paper-RAG Retriever              │
        │ - Literature-RAG Retriever          │
        │ - Evidence Judge Agent             │
        │ 输出 label/evidence/confidence      │
        └──────────┬─────────────────────────┘
                   │
                   ▼
        ┌────────────────────────────────────┐
        │ Stage 3: Meta-Reviewer Ranker      │
        │ - 过滤无效评论                     │
        │ - 合并重复评论                     │
        │ - 排序 Top-K 核心问题              │
        │ - 标注置信度与人工复核项           │
        └──────────┬─────────────────────────┘
                   │
       ┌───────────┴────────────┐
       ▼                        ▼
┌───────────────┐       ┌────────────────────┐
│ 结构化评审报告 │       │ Accept/Reject 分类  │
└───────────────┘       └────────────────────┘
```

### 6.2 Agent 设计

#### 6.2.1 MARG 原有生成类 Agent

| Agent | 作用 |
|---|---|
| Experiment Reviewer Agent | 检查实验设计、数据集、baseline、指标、消融实验是否充分 |
| Clarity/Reproducibility Reviewer Agent | 检查方法描述、公式、训练细节、复现信息是否清楚 |
| Novelty/Impact Reviewer Agent | 检查新颖性、相关工作比较、贡献大小和潜在影响 |
| Refinement Agent | 汇总各 reviewer 的意见，生成候选评论列表 |

#### 6.2.2 本课题新增 Agent

| Agent                      | 作用                           |
| -------------------------- | ---------------------------- |
| Paper Parser / Indexer     | 解析论文，建立论文内部检索索引              |
| Query Rewriter Agent       | 将候选评论改写为检索 query             |
| Paper-RAG Retriever        | 检索当前论文内部相关段落、表格和实验描述         |
| Literature-RAG Retriever   | 检索外部相关文献、baseline 和已有方法      |
| Evidence Judge Agent       | 判断评论是否有效、是否有证据、是否泛化或幻觉       |
| Meta-Reviewer Ranker Agent | 去重、排序、置信度标注，生成最终结构化评审        |
| Classification Head        | 使用证据化评审特征预测 Accept/Reject，可选 |

### 6.3 RAG 设计

本课题的 RAG 分为两类。

#### 6.3.1 Paper-RAG

Paper-RAG 检索当前被评审论文内部内容，包括 Method、Experiments、Ablation、Appendix、Table caption 等。

主要作用：

1. 判断评论指出的问题是否真的存在；
2. 判断论文是否已经解决该问题；
3. 为最终评论添加 section/table/page 证据锚点；
4. 过滤 hallucinated comments。

示例：

```text
候选评论：
The paper lacks ablation studies.

Paper-RAG 检索结果：
Section 5.3 Ablation Study, Table 4:
The authors remove the Retriever, Verifier, and Ranker modules separately.

Evidence Judge 判断：
Label = Invalid-Covered
Action = Filter
Reason = 论文已经包含模块消融实验。
```

#### 6.3.2 Literature-RAG

Literature-RAG 检索外部相关论文，主要包括 Semantic Scholar/OpenAlex/arXiv、本地论文库或已下载文献。

主要作用：

1. 检查是否遗漏重要 baseline；
2. 检查新颖性 claim 是否被已有工作削弱；
3. 支撑“相关工作比较不足”等评论；
4. 给最终报告添加外部文献依据。

示例：

```text
候选评论：
The paper does not compare with recent multi-agent reviewer systems.

Literature-RAG 检索结果：
MARG, ReviewGrounder, ScholarPeer, FactReview, ReviewAgents.

Paper-RAG 检查目标论文 Related Work：
仅讨论 MARG，未讨论 ReviewGrounder 和 ScholarPeer。

Evidence Judge 判断：
Label = Valid-Literature-Supported
Action = Keep
Reason = 论文遗漏了强相关近期系统比较。
```

### 6.4 Evidence Judge 标签体系

每条评论输出结构化结果：

```json
{
  "comment_id": "c2",
  "label": "Valid-Literature-Supported",
  "action": "keep",
  "confidence": 0.86,
  "paper_evidence": ["Related Work Section"],
  "literature_evidence": ["ReviewGrounder", "ScholarPeer"],
  "reason": "The paper discusses MARG but omits recent related multi-agent reviewer systems."
}
```

建议标签如下：

| 标签 | 含义 | 处理 |
|---|---|---|
| Valid-Supported | 有论文内证据或文献证据支持 | 保留 |
| Invalid-Covered | 论文已经解决该问题 | 删除 |
| Invalid-Hallucinated | 评论提到的内容不存在或与论文矛盾 | 删除 |
| Generic | 太泛化，缺少具体指向 | 降权或改写 |
| Weak-Evidence | 可能有价值但证据不足 | 标记人工复核 |
| Needs-Human-Check | 系统不确定 | 交给人工检查 |

### 6.5 Meta-Reviewer Ranker 设计

Meta-Reviewer Ranker 不负责大段自由生成，而是做排序和整合。

排序公式可设计为：

```text
score(comment) =
  0.35 * severity
+ 0.30 * evidence_strength
+ 0.20 * actionability
+ 0.15 * decision_impact
```

输出结构：

```text
Summary
Strengths
Major Weaknesses
Minor Weaknesses
Questions for Authors
Evidence Anchors
Confidence
Recommendation / Accept-Reject tendency
```

## 七、创新点

### 创新点一：评审意见级 RAG 证据验证机制

现有 MARG 系统能够生成大量候选评审意见，但缺少对每条意见的证据审计。本文提出 comment-level RAG Evidence Verifier，以 MARG 输出的每条评论为验证对象，分别检索论文内部证据和外部文献证据，判断该评论是否有效、是否已经被论文解决、是否过于泛化或存在幻觉。

与普通 RAG 的区别在于：普通 RAG 是“检索后生成”，本文是“生成后验证”。这使得系统能够直接针对 MARG 的 precision 低、评论过多、泛化评论仍存在的问题进行改进。

可量化目标：

- Precision 提升；
- Invalid Rate 降低；
- Generic Rate 降低；
- Evidence Coverage 提升。

### 创新点二：证据感知元评审排序机制

自动评审系统输出的评论即使有效，也可能重复、轻重不分、置信度不清。本文提出 Meta-Reviewer Ranker，根据问题严重性、证据强度、可操作性和决策影响对评论进行排序，并合并重复意见，输出 Top-K 核心问题。

该模块使系统输出更接近真实 meta-review，而不是简单堆叠多条评论。

可量化目标：

- Top-K Precision 提升；
- Redundancy Rate 降低；
- Actionability 提升；
- Confidence Calibration 改善。

### 创新点三：证据化评审特征辅助论文分类

本文进一步将证据验证后的评审结果转化为结构化特征，用于论文 Accept/Reject 分类。例如：

```text
valid_major_weakness_count
evidence_coverage
invalid_rate
novelty_risk_score
experiment_risk_score
reproducibility_risk_score
top3_concern_confidence
```

相比直接使用论文全文或原始生成评论，这些特征更具可解释性。

可量化目标：

- Accuracy 提升；
- Macro-F1 提升；
- AUC 提升；
- 分类解释性增强。

## 八、实验设计与评估指标

### 8.1 数据集

| 数据集            | 用途                                            |
| -------------- | --------------------------------------------- |
| ARIES          | 主实验，用于复现 MARG 和评估 review generation           |
| PeerRead       | Accept/Reject 分类扩展实验                          |
| DeepReview-13K | 评分预测、接收决策预测扩展实验                               |
| RottenReviews  | 评审质量辅助评估，如 factuality、actionability、vagueness |

### 8.2 主实验指标

| 指标 | 含义 | 预期方向 |
|---|---|---|
| Recall | 人工评审意见中被自动评审覆盖的比例 | 尽量保持 |
| Precision | 自动生成意见中与人工评审匹配的比例 | 提升 |
| Jaccard | 自动意见集合与人工意见集合重叠 | 提升 |
| #Comments | 平均评论数 | 降低到更合理 |
| Generic Rate | 泛化评论比例 | 降低 |
| Evidence Coverage | 带证据锚点的评论比例 | 提升 |
| Invalid Rate | 无效评论比例 | 降低 |
| Top-K Precision | Top-3/Top-5 核心评论有效率 | 提升 |
| Redundancy Rate | 重复评论比例 | 降低 |

### 8.3 分类指标

| 任务 | 指标 |
|---|---|
| Accept/Reject 分类 | Accuracy、Macro-F1、AUC |
| Rating Prediction | MSE、MAE、Spearman |
| 置信度评估 | ECE、Brier Score |

### 8.4 消融实验

| 消融设置 | 目的 |
|---|---|
| 去掉 Paper-RAG | 验证论文内部证据检索的作用 |
| 去掉 Literature-RAG | 验证外部文献证据的作用 |
| 去掉 Meta-Ranker | 验证排序和去重模块作用 |
| LLM-only Filter | 验证没有 RAG 时纯 LLM 判断是否足够 |
| BM25 vs Dense vs Hybrid | 比较不同检索策略 |
| keep/filter vs keep/filter/rewrite | 验证是否需要重写泛化评论 |

## 九、示例说明

假设 MARG 对一篇论文生成以下候选评论：

```text
c1: The paper lacks ablation studies.
c2: The paper does not compare with recent multi-agent reviewer systems.
c3: The method is not clearly described.
c4: The experiments use too few datasets.
c5: The novelty is limited because similar RAG-based review systems exist.
```

系统处理过程如下：

| 评论 | RAG 检索结果 | Evidence Judge 判断 | 处理 |
|---|---|---|---|
| c1 缺少消融 | Paper-RAG 找到 Section 5.3 Ablation 和 Table 4 | Invalid-Covered | 删除 |
| c2 缺少近期系统比较 | Literature-RAG 找到 ReviewGrounder、ScholarPeer；论文 Related Work 未比较 | Valid-Literature-Supported | 保留 |
| c3 方法不清楚 | Paper-RAG 发现整体架构有描述，但 Verifier 标签定义不清楚 | Valid-Needs-Rewrite | 改写 |
| c4 数据集太少 | Paper-RAG 找到 ARIES、PeerRead、DeepReview-13K 三个数据集 | Invalid-Covered | 删除 |
| c5 新颖性有限 | Literature-RAG 发现相关方向存在，但没有完全相同 comment-level verification | Weak-Evidence | 降权，人工复核 |

最终 Meta-Reviewer 输出：

```text
Major Weakness 1:
The paper lacks comparison with recent strong multi-agent reviewer systems such as ReviewGrounder and ScholarPeer.
Evidence: Related Work discusses MARG but omits ReviewGrounder and ScholarPeer.
Confidence: High.

Major Weakness 2:
The Evidence Verifier label schema is underspecified.
Evidence: Method section describes the module but does not define how Invalid-Covered, Generic, Weak-Evidence, and Needs-Human-Check are distinguished.
Confidence: Medium.

Minor Weakness:
The novelty claim should be stated more narrowly because related RAG-based review systems already exist.
Confidence: Medium.
```

这个例子体现了本文系统的核心价值：

> 从 MARG 的“多而杂候选评论”变成“少而准、有证据、可解释的核心评审意见”。

## 十、预期成果

1. 构建一个基于 MARG 的多智能体 RAG 自动评审原型系统。
2. 实现评审意见级 Paper-RAG 和 Literature-RAG 证据验证。
3. 实现 Meta-Reviewer Ranker，输出结构化评审报告。
4. 在 ARIES 上证明系统相比 MARG-S 提升 Precision、Evidence Coverage、Top-K Precision，降低 Generic Rate 和 Invalid Rate。
5. 在 PeerRead 或 DeepReview-13K 上验证证据化评审特征对 Accept/Reject 分类的辅助作用。

## 十一、研究计划

| 阶段 | 时间 | 内容 |
|---|---|---|
| 第一阶段 | 第 1-2 月 | 阅读核心论文，整理数据集，复现 MARG baseline |
| 第二阶段 | 第 3 月 | 实现 Paper Parser、BM25/向量检索、Paper-RAG |
| 第三阶段 | 第 4 月 | 实现 Evidence Verifier Agent 和标签体系 |
| 第四阶段 | 第 5 月 | 实现 Literature-RAG 和 Meta-Reviewer Ranker |
| 第五阶段 | 第 6 月 | 完成 ARIES 主实验与消融实验 |
| 第六阶段 | 第 7 月 | 完成 PeerRead/DeepReview-13K 分类扩展实验 |
| 第七阶段 | 第 8 月 | 整理结果，撰写论文和答辩材料 |

## 十二、需要重点阅读的论文

### 12.1 必读论文

1. **MARG: Multi-Agent Review Generation for Scientific Papers**
   - 作用：主 baseline。
   - 重点看：系统架构、agent 分工、ARIES 数据、Recall/Precision/Jaccard 指标、generic comments 分析。

2. **PeerRead: A Dataset of Peer Reviews**
   - 作用：分类任务和早期自动评审数据基础。
   - 重点看：数据规模、accept/reject 标签、评审文本结构、分类任务设置。

3. **FactReview: Evidence-Grounded Reviews with Literature Positioning and Execution-Based Claim Verification**
   - 作用：支撑“证据验证”创新点。
   - 重点看：claim extraction、claim labels、evidence report、Supported/In conflict/Inconclusive 标签体系。

4. **OpenNovelty: An LLM-powered Agentic System for Verifiable Scholarly Novelty Assessment**
   - 作用：支撑“贡献点级/评审意见级证据验证”。
   - 重点看：contribution claim extraction、evidence verification as hard constraint、verifiable novelty report。

5. **NoveltyAgent: Autonomous Novelty Reporting Agent with Point-wise Novelty Analysis and Self-Validation**
   - 作用：支撑 point-wise analysis 和 self-validation。
   - 重点看：novelty point decomposition、RAG 检索、self-validation、checklist-based evaluation。

6. **ReviewGrounder: Rubric-Guided, Tool-Integrated Agents**
   - 作用：评估体系和强相关工作。
   - 重点看：ReviewBench、8 维 rubric、Evidence-Based Critique、False or Contradictory Claims、局限性中的 meta-reviewer。

7. **RottenReviews: Benchmarking Review Quality with Human and LLM-Based Judgments**
   - 作用：辅助评估评审质量。
   - 重点看：Factuality、Vagueness、Actionability、Overall Quality 等维度。

8. **DeepReview: Improving LLM-based Paper Review with Human Feedback**
   - 作用：分类和评分预测扩展数据。
   - 重点看：DeepReview-13K、Decision Accuracy、Decision F1、Rating MSE/MAE、Spearman。

### 12.2 相关工作补充阅读

9. **ReviewAgents: Bridging the Gap Between Human and AI Review**
   - 作用：结构化审稿流程和 Review-CoT。

10. **ScholarPeer: A Context-Aware Multi-Agent Framework for Automated Peer Review**
   - 作用：search-enabled multi-agent 强相关竞品。

11. **AgentReview: Exploring Peer Review Dynamics with LLM Agents**
   - 作用：多智能体模拟审稿过程。

12. **Can LLMs Provide Useful Feedback on Research Papers?**
   - 作用：支撑 LLM 自动反馈的可行性与局限。

13. **Is LLM a Reliable Reviewer?**
   - 作用：支撑“LLM 直接评审不可靠，需要证据约束”。

14. **SubstanReview: Automatic Analysis of Substantiation in Scientific Peer Reviews**
   - 作用：支撑“评审意见是否有论据支撑”的评价思路。

## 十三、开题答辩核心话术

### 13.1 Baseline 是什么？

> 本课题的主 baseline 是 MARG。MARG 是一个多智能体论文评审生成系统，能够从实验、清晰度、新颖性等角度生成候选评审意见。它的优势是 Recall 高，但缺点是 Precision 不高，平均评论数多，仍有一定比例的 generic comments。因此，我的系统不是从零构建复杂平台，而是在 MARG 的输出端加入评审意见级 RAG 证据验证和元评审排序机制。

### 13.2 创新点是什么？

> 本课题的核心创新是将 RAG 用于“评审意见级后验验证”，而不是普通的检索增强生成。系统对 MARG 生成的每条候选评论检索论文内部证据和外部文献证据，判断该评论是否有效、是否已被论文解决、是否泛化或幻觉。然后通过 Meta-Reviewer Ranker 进行去重、排序和置信度标注，输出 Top-K 核心问题。

### 13.3 如何量化改进？

> 主实验使用 MARG 的 ARIES 数据和原有评估指标，比较改进前后的 Precision、Recall、Jaccard、评论数和 Generic Rate；同时新增 Evidence Coverage、Invalid Rate、Top-K Precision、Redundancy Rate 等指标。分类扩展实验使用 PeerRead 或 DeepReview-13K，比较 Accuracy、Macro-F1 和 AUC。

### 13.4 这个系统到底做了什么？

> MARG 负责多角度生成候选评审意见，我的系统负责验证这些意见是否成立。具体来说，Paper-RAG 检索论文原文，判断评论是不是误判或论文已经解决；Literature-RAG 检索相关工作，判断新颖性和 baseline 比较是否充分；Evidence Verifier 给每条评论打标签；Meta-Reviewer 最后保留最重要、最有证据的评论，输出结构化评审报告。

