# EviReview-Lite 实验进度

更新时间：2026-06-16

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

### E4 Provider：Agnes-2.0-Flash 分层 Pilot20

- 确认 Agnes OpenAI-compatible API 与 `agnes-2.0-flash` 可用；
- 将 Provider 请求参数按供应商配置，避免携带 MiniMax 专属字段；
- 使用 agreement validity proxy 固定分层抽样 20 条；
- 加入只针对瞬时网络错误的最多两次有限重试；
- 复跑后 Evidence Attribution Accuracy 为 1.0000，网络失败为 0；
- 剩余 1 次 Refutation JSON 解析失败，按协议回退为空案例；
- A1 Macro-F1 为 0.3439，A2 为 0.2635，A3 为 0.2480，A4 为 0.1739；
- A4 相对 A2/A3 均未提升，且 token 成本为 A2 的 3.1516 倍；
- Pilot20 verdict 为 `failed_with_metrics`，暂不扩大到 155 条。

### E4 Provider：Agnes 一次有界优化

- 冻结相同 20 条分层样本、BM25 Top-5、agreement validity proxy 和 A1/A2；
- 为 A3/A4 增加严格 Support/Refutation 角色约束；
- Adjudicator 只接收 case 已引用证据，不再重复接收全部 Top-5 evidence；
- A4 Macro-F1 从 0.1739 提升到 0.2910，超过本轮 A2 的 0.2333 与 A3 的
  0.1889；
- A4/A2 token 比从 3.1516 降到 2.4829，A4 token 降低 21.16%；
- Evidence Attribution Accuracy 为 0.8750，但仍有 13 次越界引用；
- 出现 1 次 A3 结构化解析失败和 1 次 A4 Refutation 连接失败；
- 零失败成功标准未通过，verdict 为 `failed_with_metrics`；
- 按冻结协议停止扩大至 155 条，不进行第二轮 Prompt 调参。

### SubstanReview：证据充分性辅助评价

- 实现 SubstanReview JSONL 适配器，保留官方 `train=440/test=110` 切分；
- 将 `Eval_*` 映射为 review claim，将对应 `Jus_*` 映射为 evidence span；
- 明确 `Major_claim` 无直接 evidence relation；
- 建立 S0 Proximity、S1 Lexical 和 S2 Hybrid 三个 evidence-linkage baseline；
- 仅在 train split 上选择 threshold，在 test split 上报告指标；
- Test split 含 580 个 claim、241 个 supported claim 和 106 条 claim-bearing
  review；
- Claim Evidence Coverage 为 0.4155，Substantiated Claim Rate 为 0.4251；
- 最强系统为 S0 Proximity，Supported F1 为 0.5925，Evidence Hit@1 为
  0.6680，Evidence Token-F1 为 0.5030；
- 该结果只作为 E4/E6 辅助 substantiation 证据，不作为 weakness validity 或
  covered/refuted Gold。

### E3：Controlled Literature-RAG 基线

- 将 `实验/dataset/raw/literature/local_corpus/source` 作为冻结本地文献快照；
- 实现 Literature-RAG 文献 DAO，解析 Markdown 正文、标题、年份和来源路径；
- 对缺失显式年份的本地冻结文献加入少量题名级年份补全规则，用于 citation metadata
  有效性检查；
- 固定 7 条与开题报告一致的查询：多智能体评审、证据化评审、DeepReview、
  ReviewAgents、SubstanReview、RAGChecker 和 novelty assessment；
- 比较 L0 无外部文献、L1 Keyword、L2 Hybrid 和 L3 Hybrid+metadata filter；
- L0 Recall@10 为 0.0000，L1/L2/L3 Recall@10 均为 1.0000；
- L3 MRR 为 0.9048，高于 L2 的 0.8929；
- L3 Citation Validity Rate 为 1.0000；
- L3 Future Leakage Count 为 0，低于 L2 的 20；
- E3 Autoresearch 验收通过，后续 Literature-RAG 只用于 novelty、related work
  和 missing-baseline 类型候选意见，不扩展为开放网络检索。

### E5：Meta-Reviewer Ranker 基线

- 实现 Meta-Reviewer Top-K 排序实验，输入为 CLAIMCHECK main 的 155 条候选弱点；
- 严格避免读取 E4 smoke trace 中由 gold agreement 派生的 severity 字段；
- 使用非标注文本特征、E4 audit trace、SubstanReview substantiation prior 和 E3
  Literature-RAG 边界作为排序信号；
- 比较 R0 Input Order、R1 Text Severity、R2 Text Dedup 和 R3 Evidence-aware；
- Top-K Agreement Precision：R0/R1/R2/R3 均为 0.6543，R3 未带来排序精度提升；
- Keep Coverage@K：四个系统均为 0.8298；
- Redundancy Rate：四个系统均为 0.0000，当前 CLAIMCHECK main 同论文候选重复度较低；
- Confidence Brier：R0 为 0.6003，R3 为 0.2515，说明证据感知特征改善了置信度分层，
  但略弱于 R1/R2 的 0.2400；
- E5 Autoresearch 验收通过，结论是 ranker 工程链路和边界成立，但 evidence-aware
  排序暂未证明优于文本启发式排序。

### E6：端到端结构化评审报告组装

- 实现 E6 结构化报告组装器，串联已冻结的 E2、E3、E4、E5 输出状态；
- 使用 OpenReview ICLR 2025 seed 的 10 篇论文和 41 条 Official Review 作为报告组装输入；
- 从官方评审 weakness 字段抽取候选弱点，按非标注文本特征生成 Top-K 结构化报告；
- 每条 Top-K 弱点保留 `candidate_id`、`source_review_id` 和 evidence id；
- 与 B0 Unstructured Review Dump 对比，B1 Structured Evidence Report 的 Trace Coverage
  从 0.0000 提升到 1.0000；
- B1 Top-K Compliance 为 1.0000，Paper Report Coverage 为 1.0000；
- Accept/Reject Decision 数量为 0，保持辅助评审定位；
- arXiv unseen 5 篇论文仅生成 demo manifest，不报告 Gold 指标；
- E6 Autoresearch 验收通过。该阶段证明端到端报告组装、追踪和边界控制成立，但候选弱点仍来自
  Official Review，不宣称模型候选生成质量。

## 当前验证

```text
pytest:                         88 passed after E6
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
Autoresearch E4 Agnes calibration: passed
Autoresearch E4 Agnes pilot20:    passed (experiment verdict: failed_with_metrics)
Autoresearch E4 bounded optimization: passed (experiment verdict: failed_with_metrics)
Autoresearch SubstanReview baselines: passed
Autoresearch E3 Literature-RAG:       passed
Autoresearch E5 Meta-Reviewer:       passed
Autoresearch E6 End-to-End Report:   passed
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

1. 扩大 OpenReview seed 或接入稳定 provider 生成候选弱点；
2. 将 E6 当前 review-derived candidates 替换为 system-generated candidates；
3. 保留 E6 的报告追踪、Top-K 和 unseen demo 验收边界；
4. 对候选生成质量单独设置 baseline，不用官方评审弱点冒充模型生成结果；
5. MiniMax 额度恢复后可复跑 provider-backed A0-A4，否则继续使用 Agnes/本地启发式做工程验证。
