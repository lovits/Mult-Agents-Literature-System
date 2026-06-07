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

## Phase 2H-B 已完成任务 2：Graph Registry 与无人工标注消融

后端 Agent-RAG graph 已提供 `full`、`no_dedup`、`no_verifier`、`no_ranker` 四个注册 profile，并贯通 API、持久化任务和 worker。未知 profile 返回 422，默认行为仍为 `full`。

在同一 49 篇论文、194 个 rubric-agent candidates 上，使用 full graph verifier 作为共享 silver reference：

| Profile | Selected | Mean reference support | Partial+ | Top-k overlap with full |
| --- | ---: | ---: | ---: | ---: |
| full | 141 | 0.3632 | 0.0355 | 1.0000 |
| no_verifier | 141 | 0.3569 | 0.0071 | 0.9362 |
| no_ranker | 141 | 0.3583 | 0.0142 | 0.9078 |

结果支持保留 verifier 与 evidence-aware ranker，但仍属于 silver ablation。

## Phase 2H-B 已完成任务 3：Dense / Hybrid Retrieval 与 Qdrant Adapter

核心检索层新增：

- injectable dense cosine retriever；
- BM25 + dense 的 RRF hybrid retriever；
- dependency-free Qdrant Query API adapter，使用 `prefetch + fusion=rrf`；
- Qdrant transport injection 单元测试，不要求本地 Qdrant 服务。

在 CLAIMCHECK 同一 ready-label mapped targets 上：

| Method | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR |
| --- | ---: | ---: | ---: | ---: |
| BM25 sparse | 0.1806 | 0.3611 | 0.4167 | 0.3135 |
| OpenRouter dense | 0.2222 | 0.5000 | 0.6944 | 0.4067 |
| BM25 + dense RRF hybrid | 0.2361 | 0.4306 | 0.5556 | 0.3834 |

Dense 在 Hit@3 上优于 BM25；未调参 RRF 提升 BM25 的 MRR，但没有超过 dense。后续优化应调节 fusion / rerank，而不是把 hybrid 固定为默认最佳方法。

## Phase 2H-B Validator Gate

- provider paired comparison validator：passed；
- graph ablation validator：passed；
- dense/hybrid retrieval validator：passed；
- Phase 2H-B mission validator：检查以上结果均进入统一指标导出；
- 当前 unified metric records：1736。

## Phase 2H-B 已完成任务 4：真实 Qdrant 建库与查询实验

在本地 Docker Qdrant 服务上完成真实 collection 创建、payload keyword index、批量写入和 Query API 检索。实验继续使用相同 CLAIMCHECK ready-label mapped targets，并复用缓存 dense embedding，从而将向量库执行差异与 embedding 模型差异分离。

| Method | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR |
| --- | ---: | ---: | ---: | ---: |
| Qdrant BM25 sparse | 0.1806 | 0.3611 | 0.4167 | 0.3130 |
| Qdrant OpenRouter dense | 0.2222 | 0.5000 | 0.6944 | 0.4067 |
| Qdrant native RRF hybrid | 0.2639 | 0.4306 | 0.5972 | 0.4039 |

- 实际写入 `6606` 个 claim points，同时保存 dense 与 sparse vectors。
- Dense Main Hit@3 仍为最佳，说明当前不应将未调参 Hybrid 固定为默认方法。
- Qdrant 原生 RRF 与本地完整候选集 RRF 的排序结果存在轻微差异，应作为不同执行配置分别报告。
- 为消除 Qdrant 同分候选返回顺序波动，评估取回每行完整候选集，并按 `score + claim_index` 确定性排序；连续两次复跑的 Hit@K 与 MRR 完全一致。
- 真实运行环境为本地 Docker Qdrant `1.18.2`；已加入 `row_key` keyword payload index，并在结果文件中记录单查询 mean/P50/P95 延迟。
- 当前实验验证了单机真实建库和查询；尚未评估多并发、远程网络、量化和大规模 HNSW 参数。

## Phase 2H-B 已完成任务 5：可配置 Query Planner 与 Retriever

后端 Agent-RAG 主链路新增独立 `plan_weakness_queries` 节点。API、持久化任务和 worker 现在能够分别选择：

- Query Planner：`direct`、`category_expansion`
- Retriever：`hierarchical`、`bm25`
- Graph Profile：`full`、`no_verifier`、`no_ranker`

未知组件名会在 API 请求阶段返回 422；运行结果和 agent trace 会保存实际 planner 与 retriever。

在同一 CLAIMCHECK ready-label mapped targets 上，固定 BM25 retriever：

| Query Planner | Main Hit@1 | Main Hit@3 | Main Hit@5 | Main MRR |
| --- | ---: | ---: | ---: | ---: |
| direct | 0.1806 | 0.3611 | 0.4167 | 0.3135 |
| category expansion | 0.1806 | 0.3611 | 0.4167 | 0.3135 |

类别扩展没有产生提升，因此默认 planner 保持 `direct`。该负结果说明后续 planner 应采用可验证的多步分解或模型规划，而不是简单追加类别关键词。

## Phase 2H-B 已完成任务 6：Evidence-aware Deduplication Agent

完整图现已调整为：

```text
generate -> plan -> retrieve -> verify -> deduplicate -> rank
```

去重只允许在同一论文和同一类别内执行，使用确定性词面相似度建立重复组，并优先保留 evidence-aware 分数更高的候选。运行结果保存 `duplicate_of` 映射；`no_dedup` profile 用于消融，不会静默删除候选。

在 49 篇本地 OpenReview/PRISM 论文的 194 条 rubric-agent 候选上：

| Profile | Candidates | Deduplicated | Removed | Reduction | Selected | Partial+ | Top-K overlap with full |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full | 194 | 172 | 22 | 0.1134 | 139 | 0.0360 | 1.0000 |
| no_dedup | 194 | 194 | 0 | 0.0000 | 141 | 0.0355 | 0.8652 |

去重减少 11.34% 的候选，shared silver reference 下的 Partial+ 基本保持。结果只支持“减少论文内模板重复并提高输出紧凑性”，不能解释为 human-gold review quality 提升。

## Phase 2H-B 已完成任务 7：Qdrant / Hybrid Worker 正式接入

API、持久化任务和 Worker 现已支持：

- `qdrant_sparse`：真实 Qdrant BM25 sparse vectors，不需要 embedding key；
- `qdrant_hybrid`：真实 Qdrant sparse + dense native RRF，embedding provider 只从 Worker 环境变量读取。

严格验收已覆盖：

1. 直接 Worker 到真实 Qdrant sparse；
2. SQLite persisted job 经 Redis/RQ 到 Worker，再到真实 Qdrant sparse；
3. 真实 Qdrant 与 OpenAI-compatible embedding adapter 的 hybrid Worker。

Qdrant/Hybrid 现在是正式可选择后端组件，但默认仍保持 `hierarchical`，因为当前 CLAIMCHECK gold 结果中 dense Hit@3 高于未调参 hybrid。
