# 数据集 Schema Inspection（2026-06-17）

## 目标

本报告只检查新增数据快照是否适合进入后续实验设计，不做模型调参或指标优化。检查原则是：数据能扩大实验规模，但不能越过其标注边界。

## PeerQA-XT

| 项目 | 结果 |
| --- | --- |
| 数据集 | `UKPLab/PeerQA-XT` |
| 访问状态 | Hugging Face 非 gated |
| License | CC BY-NC-SA 4.0 |
| 本地状态 | 4/4 parquet 文件已下载并通过 `PAR1` 校验 |
| 总行数 | 12,628 |
| Train | 10,128 |
| Validation | 1,248 |
| Test | 1,252 |
| 字段 | `pid`, `qid`, `question`, `answer`, `paper`, `domain` |
| 适合任务 | E2 Paper-RAG 辅助扩展；长文档 QA 检索；跨 domain 稳定性诊断 |
| 不适合任务 | 不作为严格人工 Gold；不作为 evidence-type prior 成功的唯一证据 |

### 使用边界

PeerQA-XT 能解决 PeerQA 原始 579 QA 太小的问题，但它是合成 QA 数据。论文中可以写成“辅助扩展评价/鲁棒性诊断”，不能写成替代 PeerQA 作者标注 Gold。

下一步建议：

1. 固定 `validation+test` 作为不调参扩展评估集；
2. `train` 只用于检索参数或缓存压力测试，不用于证明最终泛化；
3. 保留 `domain` 维度，报告 biomedical、NLP、social science 等 domain-level Recall@K 差异。

## ResearchArcade OpenReview Papers-Reviews

| 项目 | 结果 |
| --- | --- |
| 数据集 | `ulab-ai/ResearchArcade-openreview-papers-reviews` |
| 访问状态 | Hugging Face 非 gated |
| 本地状态 | README 与 HF converted parquet 已下载并通过 `PAR1` 校验 |
| 总行数 | 737,577 |
| Train | 737,577 |
| 字段 | `venue`, `paper_openreview_id`, `review_openreview_id`, `title`, `time` |
| 适合任务 | OpenReview thread metadata 扩容；按 venue/year/title 统计 review event；定位 official review / meta review / decision 类型 |
| 不适合任务 | 不能直接替代完整 review text；不能直接做 weakness 内容评价 |

### 使用边界

ResearchArcade converted parquet 只有 5 个字段，主要是 OpenReview review/thread metadata。它能扩大 paper-review linkage 和 event 类型覆盖，但不能直接支撑双向证据审计，因为当前 converted 快照没有完整 review 正文。

下一步建议：

1. 用它建立 OpenReview paper-review event registry；
2. 过滤 `title` 中包含 `Official Review`、`Meta Review`、`Paper Decision` 的记录；
3. 将 `paper_openreview_id` 与已有 OpenReview API/PDF 快照对齐；
4. 需要 review text 时仍以 OpenReview API 或 NLPEERv2 为主。

## 对实验计划的影响

| 实验阶段 | 影响 |
| --- | --- |
| E2 Paper-RAG | PeerQA-XT 可扩大 QA 检索样本，用于 Recall@K、MRR、domain-level robustness；相对 baseline 的提升仍需正式 rerun 后报告 |
| E4 双向证据审计 | 本轮数据不直接新增 covered/refuted Gold；仍以 CLAIMCHECK/SubstanReview 为主 |
| E5 Meta-Reviewer Ranker | ResearchArcade 可提供更多 OpenReview event metadata，但不直接提供 weakness label |
| E6 端到端报告 | OpenReview seed 仍是主数据；ResearchArcade 可用于选择更多 paper IDs 和 review event 类型 |

## 当前结论

本轮数据补齐提升的是实验数据准备度，不是模型指标。相对上一版 baseline：

- PeerQA-XT 从 partial 变成 complete，本地可用性提升；
- ResearchArcade 从未落地变成 converted metadata 可用；
- 严格评价 baseline 暂未复跑，因此不能声称模型性能提升。

