# E4 CLAIMCHECK Claim Association 与 Weakness Labeling 基线

日期：2026-06-14

## 实验目的

本阶段在实现双向证据审计 Agent 前，先建立可复现且无标签泄漏的检索与标注基线。`pilot` 仅用于开发和校准，`main` 仅用于严格评价。CLAIMCHECK 公开文本数据不包含逐条 `covered/refuted` Gold，因此本阶段不报告 Covered/Refuted Recall。

## 数据与协议

- `main` 共 155 条 weakness；
- 91 条 weakness 的 Target Claim 能够映射到原文段落，用于 Claim Association；
- 17 条因 Target Claim 无法映射而排除；
- 47 条因没有 Target Claim 而排除；
- 所有排除样本均保留 ID 与原因；
- Weakness Labeling 使用全部 155 条 `main` weakness；
- BGE 固定为 `BAAI/bge-base-en-v1.5` revision `a5beb1e3e68b9ab74eb54cfd186867f64f240e1a`。

## Claim Association 结果

| 系统 | Recall@1 | Recall@3 | Recall@5 | MRR | nDCG@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| C0 Position | - | - | 0.3516 | 0.3358 | - |
| C1 BM25 | 0.3370 | 0.6190 | **0.7656** | **0.5392** | **0.5727** |
| C2 Dense | - | - | 0.5458 | 0.3708 | - |
| C3 Hybrid RRF | - | - | 0.6520 | 0.5065 | - |

`C1 BM25` 是当前最强 Claim Association 基线。通用 Dense 与简单 RRF Hybrid 均未超过 BM25，说明 CLAIMCHECK 的 weakness 与源段落之间存在较强词汇线索，未经任务适配的语义检索会稀释该信号。该负结果必须保留；后续 A1-A4 先使用 BM25 作为证据检索基线，再单独验证结构感知或任务适配检索是否真正增加收益。

## Weakness Labeling 零成本基线

`W0_pilot_prior` 仅使用 `pilot` 的中位数与多数类，在 `main` 上获得：

| 指标 | 结果 |
| --- | ---: |
| Groundedness MAE | 1.2903 |
| Agreement MAE | 1.3871 |
| Subjectivity MAE | 1.2129 |
| Weakness Type Macro-F1 | 0.1216 |
| 单候选成本 | 0 |

该结果表明 weakness 标签预测不是仅靠先验即可解决的任务，也为后续 Agent Judge 提供最低参照。

## 结论与边界

1. E4 检索与标注基线已完成，逐样本排名、Gold ID 和排除原因均已保存。
2. C1 BM25 是后续证据审计的初始检索基线；不得预设 Hybrid 必然更强。
3. C/W 基线不是 A0-A4 双向证据审计系统，不能据此宣称自动判断意见成立或已被论文覆盖。
4. 下一阶段比较 A1 Direct Judge、A2 Support-only、A3 Support+Refutation 和 A4 Adjudicator，并使用 CLAIMCHECK 的 groundedness/agreement 评价可验证能力。

## 文献依据

- CLAIMCHECK 官方数据与任务定义：<https://github.com/JHU-CLSP/CLAIMCHECK>
- CLAIMCHECK 论文：<https://arxiv.org/abs/2503.21717>
- RAGChecker 的模块级检索诊断：<https://arxiv.org/abs/2408.08067>
- FactReview 的 claim-level evidence audit 思路：<https://arxiv.org/abs/2604.04074>
