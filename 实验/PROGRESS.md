# EviReview-Lite 实验进度

更新时间：2026-06-14

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
- 下载 SubstanReview：550 条 claim-evidence 配对评审标注；
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

### E2 Smoke：P0-P4 批量运行

- 实现 PeerQA P0-P4 批量运行器；
- 使用确定性 hashing embedding 完成全部 136 条可映射样本链路验收；
- 增加 Precision@K，诊断召回提升与噪声引入的权衡；
- 明确 smoke 结果 `formal_result=false`，不作为论文主结果。
- Smoke 中 P0 BM25 Recall@5 为 0.2193，P4 Recall@5 为 0.1207；
- P4 Evidence-Type Match@5 为 0.9485，但当前结构与类型先验损害召回，正式实验前必须重新校准。

### E2 正式实验：固定 BGE 与高置信度先验门控

- 建立隔离 Python 3.12 正式环境，固定 `sentence-transformers==5.5.1`；
- 固定 embedding 为 `BAAI/bge-base-en-v1.5` revision `a5beb1e3...`；
- 区分 query/document 编码，并跨样本批量缓存论文块 embedding；
- 修复所有问题默认使用 Experiment 章节先验的 Planner 错误；
- 保留门控前后两份正式结果，未选择性删除失败结果；
- P2 与门控后 P4 Recall@5 均为 0.2863，P4 未超过最强 baseline；
- P4 Evidence-Type Match@5 为 0.8838，低于 P2 的 0.9000；
- E2 实验状态为 `failed_with_metrics`，已完成但未通过开题报告成功标准。

### E4 基础：CLAIMCHECK 严格评价适配

- 实现 CLAIMCHECK source text 适配器；
- 验收 60 个 paper-review 对、168 条弱点和 120 条带 Target Claim 弱点；
- 保留 groundedness、agreement、subjectivity 和多标签 weakness type；
- 明确 CLAIMCHECK 没有逐条 `covered/refuted` Gold，禁止越界宣称；
- 确定首轮 E4 为 Claim Association 与 Weakness Labeling Baseline。

### E4 基线：Claim Association 与 Weakness Labeling

- 冻结 `pilot` 仅用于开发、`main` 仅用于评价的无泄漏协议；
- 将 CLAIMCHECK Target Claim 映射到原论文段落，严格评价 91 条 weakness；
- 保留 64 条不可评价样本及排除原因；
- 比较 C0 Position、C1 BM25、C2 Dense 和 C3 Hybrid RRF；
- C1 BM25 Recall@5 为 0.7656，是最强检索基线；
- C3 Hybrid Recall@5 为 0.6520，未超过 BM25，保留为诊断性负结果；
- W0 Pilot Prior 的 Weakness Type Macro-F1 为 0.1216；
- 保存逐样本 Gold ID 与完整排名，建立 E4 Baseline Autoresearch 验收器。

### E4 协议：固定双向证据审计 Smoke

- 实现 Support Agent、Refutation Agent 与 Evidence Adjudicator；
- 每条候选固定运行双向审计，不使用争议触发升级；
- 强制 Audit Case 只能引用 EvidenceBundle 内证据；
- 固定自动裁决为 `keep/rewrite/reject/uncertain`，不加入 human-check；
- 使用版本化 agreement validity proxy，不伪造 covered/refuted Gold；
- 在全部 155 条 CLAIMCHECK main weakness 上生成完整审计轨迹；
- 越界证据引用、缺失双向案例、空案例强度违规均为 0；
- 启发式 A4 Macro-F1 为 0.1164，低于 A3 的 0.2674，确认简单 Refutation
  启发式会过度触发，不能作为正式主结果。

### E4 Provider：MiniMax-M2.7 A0-A4 校准接入

- 核实官方模型 ID 为 `MiniMax-M2.7`；
- 确认当前 Token Plan Key 属于中国区，使用 `https://api.minimaxi.com/v1`；
- 实现 OpenAI-compatible JSON Provider 与 M2.x reasoning 输出兼容；
- 实现 provider-backed A0-A4 runner；
- 记录逐系统调用数、tokens、延迟、失败原因、证据越界和逐样本轨迹；
- 首条校准样本的 6 次 provider 调用均返回 HTTP 429 / MiniMax 2056；
- 当前状态为 `pending_quota`，没有产生正式 MiniMax 模型指标。

## 当前验证

```text
pytest:                         55 passed
E0 registered datasets:         8
Downloaded datasets:            6
Restricted datasets:            1 (NLPEERv2)
Local snapshots:                1
OpenReview valid PDFs:          10 / 10
arXiv unseen valid PDFs:         5 / 5
Autoresearch dataset bootstrap: passed
Autoresearch flat layout/task6: passed
Autoresearch PeerQA E2 foundation: passed
Autoresearch execution stage A/B:   passed
Autoresearch formal E2:             passed (experiment verdict: failed_with_metrics)
Autoresearch E4 CLAIMCHECK foundation: passed
Autoresearch E4 baselines:         passed
Autoresearch E4 audit protocol:    passed (heuristic smoke, not formal A0-A4)
Autoresearch E4 MiniMax calibration: pending_quota
Clean dataset layout:             passed (no nested Git/ZIP/legacy)
pip check:                      no broken requirements
```

## 当前限制

1. NLPEERv2 完整数据尚未获得访问授权，当前使用 OpenReview seed 作为原始完整论文主数据；
2. OpenReview seed 当前只有 10 篇，用于打通流程；E1/E6 正式实验前需要按固定协议扩大；
3. arXiv 未见集只用于最终演示，不能用于调参或 Gold 评价；
4. E2 正式实验已完成，但 PeerQA 上的 P4 未达到预设 Recall 与 Evidence-Type Match 增益；
5. PeerQA 映射后的证据类型以 paragraph 为主，不足以单独证明 evidence-type prior 有效。

## 下一步

按照关键路径继续：

1. MiniMax Token Plan 额度恢复后复跑 5 条 A0-A4 校准；
2. 校准零失败后扩大 provider-backed A0-A4；
3. 使用 agreement validity proxy 评价，不伪造 covered/refuted Gold；
4. 使用 SubstanReview 作为证据充分性辅助评价；
5. 保留启发式 A4 过度触发与 provider quota blocker，不选择性删除失败。
