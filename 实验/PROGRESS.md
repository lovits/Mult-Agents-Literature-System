# EviReview-Lite 实验进度

更新时间：2026-06-13

## 已完成

### 目录与设计基线收敛

- 全部有效实验代码直接位于 `实验/`，不再使用 `新实验` 或 `evireview_lite` 包装目录；
- 删除历史辅助数据、第三方仓库源码、重复压缩包与缓存；
- 数据按 `primary/evaluation/literature/demo/restricted` 实验角色分层；
- `设计方案/` 仅保留最新开题报告、设计方案和实验方案三份权威文档。

### Task 1：实验项目骨架

- 创建独立的 Python 实验项目；
- 建立环境变量配置，API Key 不进入代码和配置文件；
- 安装最小运行与测试依赖；
- 配置测试、数据、输出和源码目录边界。

### Task 2：统一领域协议

- 定义 `PaperDocument`、`EvidenceBlock`、`CandidateWeakness`、`QueryPlan`；
- 定义 `EvidenceBundle`、`AuditCase`、`AdjudicationResult`；
- 定义 `RankedWeakness` 与 `ReviewReport`；
- 在模型层强制 Literature-RAG 只用于四类外部比较意见。

### Task 3 / E0：四层数据启动

- 建立 `raw_primary`、`strict_evaluation`、`literature_corpus`、`unseen_demo` 四层数据注册表；
- 下载 OpenReview ICLR 2025 seed：10 篇完整 PDF、41 条 Official Review；
- 下载 PeerQA：579 条标注 QA、24,265 条论文段落记录；
- 下载 CLAIMCHECK：55 个 main source paper-review 对及相关工作数据；
- 下载 ReviewCritique：100 篇人类评审论文、20 篇 LLM 评审论文；
- 挂载本地 Literature-RAG 固定语料：65 个 PDF/Markdown 文件；
- 冻结 arXiv 未见集：5 篇最新 `cs.CL` PDF；
- 记录 NLPEERv2 受限状态，完整数据仍需申请；
- 建立 E0 审计脚本与 Autoresearch 数据验收器。

### Task 4：论文结构解析

- 实现 Markdown 论文解析主路径；
- 统一章节名称；
- 构造稳定 `EvidenceBlock` ID；
- 保留 paragraph、table caption、algorithm 和 appendix 证据类型。

### Task 5：基础检索与公平索引缓存

- 实现 P0 BM25 检索；
- 实现可注入 embedding provider 的 P1 Dense Retriever；
- 实现 P2 Reciprocal Rank Fusion；
- 实现包含 paper、parser、embedding model 和 block hash 的索引缓存身份；
- 使用统一 `EvidenceItem` 输出，供后续 P0-P4 公平比较。

### Task 6：结构与证据类型感知 Paper-RAG

- 实现 Section Prior 与 Evidence-Type Prior；
- 实现不跨章节的 Neighbor Expansion；
- 实现 P2、P3、P4 可控消融配置；
- 建立目录收敛与 Task 6 Autoresearch 验收器。

### E2 基础：PeerQA 适配与检索指标

- 将 PeerQA 论文段落映射为统一 `EvidenceBlock`；
- 将 `answer_evidence_mapped.idx` 映射为可评价的 Gold evidence ID；
- 实现 Recall@K、MRR 和 nDCG@K；
- 建立真实 PeerQA 数据映射 Autoresearch 验收器。

## 当前验证

```text
pytest:                         23 passed
E0 registered datasets:         7
Downloaded datasets:            5
Restricted datasets:            1 (NLPEERv2)
Local snapshots:                1
OpenReview valid PDFs:          10 / 10
arXiv unseen valid PDFs:         5 / 5
Autoresearch dataset bootstrap: passed
Autoresearch flat layout/task6: passed
Autoresearch PeerQA E2 foundation: passed
Clean dataset layout:             passed (no nested Git/ZIP/legacy)
pip check:                      no broken requirements
```

## 当前限制

1. NLPEERv2 完整数据尚未获得访问授权，当前使用 OpenReview seed 作为原始完整论文主数据；
2. OpenReview seed 当前只有 10 篇，用于打通流程；E1/E6 正式实验前需要按固定协议扩大；
3. arXiv 未见集只用于最终演示，不能用于调参或 Gold 评价；
4. 当前尚未实现正式 PeerQA E2 P0-P4 批量运行器；检索指标和 Gold 映射已经就绪。

## 下一步

按照关键路径继续：

1. 实现在 PeerQA 上批量运行的 E2 P0-P4 Paper-RAG 入口；
2. 固定 embedding 模型后运行首个 E2 检索实验；
3. E2 稳定后再进入双向证据审计 E4。
