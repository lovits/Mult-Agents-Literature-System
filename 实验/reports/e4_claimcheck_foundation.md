# E4 CLAIMCHECK 数据边界与执行方案

日期：2026-06-13

## 1. 数据验收

| 项目 | 数量 |
| --- | ---: |
| Paper-review 对 | 60 |
| 弱点总数 | 168 |
| Main 弱点 | 155 |
| Pilot 弱点 | 13 |
| 带 Target Claim 的弱点 | 120 |

每条弱点保留：

- weakness span；
- groundedness confidence，1-5；
- target claims；
- subjectivity，1-5；
- agreement，1-5；
- 多标签 weakness type。

## 2. 严格评价边界

CLAIMCHECK 官方论文将任务定义为 Claim Association、Weakness Labeling and
Editing、Claim Verification。当前公开文本数据能够直接支持：

1. Target Claim Association；
2. Groundedness Confidence 预测；
3. Agreement、Subjectivity 与 Weakness Type 预测；
4. 基于 target claim 的 evidence attribution。

当前数据没有逐条 `covered/refuted` Gold，因此不能直接将其用于报告
Covered/Refuted Recall。双向审计中的 support/refutation/adjudication 可以在
CLAIMCHECK 上运行，但严格指标必须限制为 claim association、agreement、
groundedness 和 weakness type；Covered/Refuted 只能使用另一个具有相应标签的
数据源，或明确标记为 proxy。

## 3. 下一步 E4 Baseline

按工作量和标签可用性，先实现：

- A0：Weakness-only 规则/多数类 baseline；
- A1：Weakness + Target Claim lexical baseline；
- A2：Weakness + Target Claim embedding baseline；
- A3：Paper-RAG evidence attribution；
- A4：Support + Refutation + Adjudicator，作为完整系统。

首轮严格指标：

- Target Claim Recall@K / MRR；
- Grounded Weakness 二分类 F1；
- Agreement MAE；
- Weakness Type Macro-F1；
- Evidence Attribution Accuracy。

## 4. 文献依据

- CLAIMCHECK 官方数据说明：
  <https://github.com/JHU-CLSP/CLAIMCHECK>
- CLAIMCHECK 论文：
  <https://arxiv.org/abs/2503.21717>
- FactReview 进一步支持“审计 claim 而不是自动录用决策”的定位：
  <https://arxiv.org/abs/2604.04074>

## 5. 风险

1. Target claims 是 claim-level Gold，不等同于完整 paragraph evidence Gold；
2. Agreement 是弱点成立程度的 ordinal 标签，不应直接改名为 accept/reject；
3. Subjectivity 的方向和阈值必须遵循论文定义，不自行二值化；
4. Covered/Refuted 指标当前缺少直接 Gold，必须保持边界声明。
