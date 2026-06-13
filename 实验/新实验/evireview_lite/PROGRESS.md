# EviReview-Lite 新实验进度

更新时间：2026-06-13

## 已完成

### Task 1：实验项目骨架

- 创建独立的 `evireview_lite` Python 实验项目；
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
- 下载 NLPeer loader，并明确完整 NLPEERv2 仍需申请；
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

## 当前验证

```text
pytest:                         17 passed
E0 registered datasets:         7
Downloaded datasets:            5
Restricted datasets:            1 (NLPEERv2)
Local snapshots:                1
OpenReview valid PDFs:          10 / 10
arXiv unseen valid PDFs:         5 / 5
Autoresearch dataset bootstrap: passed
pip check:                      no broken requirements
```

## 当前限制

1. NLPEERv2 完整数据尚未获得访问授权，当前使用 OpenReview seed 作为原始完整论文主数据；
2. OpenReview seed 当前只有 10 篇，用于打通流程；E1/E6 正式实验前需要按固定协议扩大；
3. arXiv 未见集只用于最终演示，不能用于调参或 Gold 评价；
4. 当前尚未实现结构感知 P3/P4 Paper-RAG 与正式 PeerQA E2 运行器。

## 下一步

按照关键路径继续：

1. Task 6：实现 Section Prior、Evidence-Type Prior、Neighbor Expansion；
2. 在 PeerQA 上运行首个 E2 Paper-RAG 检索实验；
3. E2 稳定后再进入双向证据审计 E4。
