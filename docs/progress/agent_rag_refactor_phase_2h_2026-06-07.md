# Agent-RAG 重构 Phase 2H-A 进度：统一实验指标聚合与导出

日期：2026-06-07

## 阶段定位

按照重构计划对齐结论，前端 Phase 3/4 继续冻结。当前先完成 Phase 2H-A：建立统一实验指标契约，将后端 experiment manifest runs 与历史实验 JSON 汇入同一导出链路。

Phase 2H-A 只建立稳定聚合基线；实验复跑和算法优化进入 Phase 2H-B。

## 已完成内容

1. 统一指标契约
   - 新增 `MetricRecord`。
   - 每条记录强制包含 dataset、task、module、method、metric、value、metric boundary 和 source artifact。
   - metric boundary 仅允许 `gold`、`silver`、`proxy`、`diagnostic`。

2. 稳定导出器
   - 支持确定性 JSON、CSV 和 Markdown。
   - 所有格式使用同一排序规则。
   - 不包含原始 weakness、evidence 正文、内部 artifact path 或 provider key。

3. 历史实验 adapter registry
   - 覆盖 Local OpenReview/PRISM、PeerQA-XT、PeerReview Bench、SubstanReview、CLAIMCHECK、rubric-agent、GLM 和 MiniMax。
   - 从既有 metrics/summary JSON 读取数值，不修改源文件。
   - provider coverage threshold 被编码进 metric name，不把 threshold 本身误当评估结果。

4. 后端 manifest 指标聚合
   - 新增 `GET /api/experiments/{manifest_id}/metrics`。
   - 聚合 run count、状态、成功率、weakness 数、ranked finding 数和 mean support。
   - 后端运行统一标记为 `silver`。

5. 统一可复跑 CLI
   - `python3 code/experiments/evireview_a/src/export_unified_metrics.py`
   - 输出：
     - `data/unified_metrics.json`
     - `data/unified_metrics.csv`
     - `reports/unified_metrics.md`

## 当前聚合结果

| 项目 | 数量 |
| --- | ---: |
| Unified metric records | 1636 |
| Datasets / manifest datasets | 7 |
| Gold records | 479 |
| Silver records | 48 |
| Proxy records | 218 |
| Diagnostic records | 891 |
| Missing required fields | 0 |

## 边界与解释

- `gold` 表示指标直接使用外部 ready-label 数据集的人类标签，不代表模型已达到可靠人工评审水平。
- `silver` 表示来自当前后端审计流程或银标 verifier。
- `proxy` 表示 section alignment、answer-token support 等间接指标。
- `diagnostic` 表示 provider、小样本、ranker 或辅助分类诊断。
- Phase 2H-A 不重新运行和优化算法，因此保留历史指标事实。

## 下一阶段：Phase 2H-B

1. 建立 validator-gated 实验优化任务。
2. 优先完成 MiniMax / GLM / rubric-agent 同论文集合 paired comparison。
3. 复跑 verifier minority-class、ranker ablation 和 retrieval query-planner/hybrid 实验。
4. 所有新结果必须重新通过统一聚合 CLI 进入论文表格。

## Phase 2H-B 已完成任务 1：Provider Paired Comparison

在 MiniMax、GLM 和 rubric-agent 的共同 5 篇论文上完成公平 paired diagnostic：

| Generator | Weaknesses | Recall@0.18 | Mean support | Partial+ |
| --- | ---: | ---: | ---: | ---: |
| Rubric-agent | 20 | 0.4437 | 0.2061 | 0.0000 |
| GLM-4.6V | 12 | 0.5232 | 0.3751 | 0.3333 |
| MiniMax-M2.7 | 15 | 0.5232 | 0.4670 | 0.4667 |

结果已通过独立 validator，并重新进入统一指标导出和论文实验表格。该结果仍是 5-paper diagnostic，不是最终 provider 排名。
