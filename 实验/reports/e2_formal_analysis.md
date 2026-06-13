# E2 Paper-RAG 正式实验分析

日期：2026-06-13

## 1. 实验目的

验证结构与证据类型感知 Paper-RAG 是否优于 BM25、Dense 和普通 Hybrid
RAG。该实验对应开题报告 RQ1。

## 2. 固定协议

- 数据：PeerQA 中 136 条可映射 Gold evidence 样本；
- P0：BM25；
- P1：Dense Retrieval；
- P2：BM25 + Dense + RRF；
- P3：P2 + Section Prior；
- P4：P3 + Evidence-Type Prior + Neighbor Expansion；
- Embedding：`BAAI/bge-base-en-v1.5`；
- Revision：`a5beb1e3e68b9ab74eb54cfd186867f64f240e1a`；
- 设备：CPU；
- Top-K：5；
- Gold 只用于评价，不进入检索或排序；
- Query embedding 在计时前统一预热，延迟只统计检索阶段。

## 3. 正式结果

| 系统 | Recall@5 | Precision@5 | MRR | nDCG@5 | Evidence-Type Match@5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| P0 BM25 | 0.2193 | 0.0824 | 0.2385 | 0.1921 | 0.9059 |
| P1 Dense | 0.2848 | 0.1044 | 0.3143 | 0.2527 | 0.9000 |
| P2 Hybrid | **0.2863** | **0.1059** | **0.3290** | **0.2640** | 0.9000 |
| P3 Structure | **0.2863** | **0.1059** | **0.3290** | **0.2640** | 0.9044 |
| P4 Structure + Type | **0.2863** | **0.1059** | 0.3254 | 0.2631 | 0.8838 |

## 4. 小幅优化与消融结论

初始 Query Planner 将所有问题默认路由到 Experiments、Results、Ablation 和
Appendix，导致 P4 Recall@5 只有 0.2532。改为仅在问题包含明确章节或证据类型
线索时使用先验后，P4 Recall@5 提升 0.0331，恢复到 P2 水平。

该修复说明结构先验必须由 Query Planner 的高置信度声明约束，不能无条件应用。
但 P4 仍未超过 P2，且 Evidence-Type Match@5 下降。因此 E2 的结论是：

```text
experiment_verdict = failed_with_metrics
```

不继续在同一 PeerQA 测试集调整权重，避免测试集过拟合。

## 5. 文献复核与系统借鉴

- RAGChecker 强调分别诊断检索器的召回和精度，而不是只报告端到端分数。本实验
  因此同时保留 Recall@K、Precision@K、MRR 与 nDCG。
- MA-RAG 强调 Planner 的任务感知分解。本实验的高置信度先验门控属于固定、
  可消融的 Planner 约束，不增加新 Agent。
- Agentic RAG Survey 将 adaptive retrieval 和模块化工作流列为 Agentic RAG
  的关键设计模式；本项目只借鉴任务感知路由，不采用自由动态编排。

来源：

- <https://arxiv.org/abs/2408.08067>
- <https://arxiv.org/abs/2505.20096>
- <https://arxiv.org/abs/2501.09136>

## 6. 对后续实验的影响

1. E4 双向证据审计使用 P2 作为稳定检索 baseline；
2. P4 保留为结构感知消融，但不能宣称已提升检索效果；
3. 最终论文将 E2 作为失败保留型实验和误差分析；
4. 后续不在 PeerQA 测试集继续调结构或类型先验权重。
