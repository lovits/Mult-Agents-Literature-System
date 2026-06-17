# EviReview-Lite 实验进度

更新时间：2026-06-17

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
- 下载并扩展 OpenReview ICLR 2025 seed：30 篇完整 PDF、122 条 Official Review；
- 下载 PeerQA：579 条标注 QA、24,265 条论文段落记录；
- 下载 CLAIMCHECK：55 个 main source paper-review 对及相关工作数据；
- 下载 ReviewCritique：100 篇人类评审论文、20 篇 LLM 评审论文；
- 下载 SubstanReview：550 条 claim-evidence 配对评审标注；
- 挂载本地 Literature-RAG 固定语料：65 个 PDF/Markdown 文件；
- 冻结 arXiv 未见集：5 篇最新 `cs.CL` PDF；
- 记录 NLPEERv2 受限状态，完整数据仍需申请；
- 建立 E0 审计脚本与 Autoresearch 数据验收器。

### Task 3-D：数据扩展与授权限制处理

- 保留 OpenReview ICLR 2025 seed 30 篇完整 PDF、122 条 Official Review 作为当前完整主数据；
- 新增 OpenReview ICLR 2025 expanded-100 快照：100 篇投稿元数据、229 条 Official Review、35 篇有效 PDF；
- expanded-100 记录 42 个 forum 抓取失败和 65 个 PDF 失败，主要受 OpenReview 429 限流影响，暂不替代 30 篇完整 seed；
- 将 arXiv unseen 从 5 篇扩展到 20 篇最新 `cs.CL`，20 个 PDF 均有效；
- 新增 PeerQA-XT complete 快照：README、test、validation 与两个 train parquet shard 已落地；
- PeerQA-XT 为非 gated、CC BY-NC-SA 4.0、合成 QA 数据，只作为 E2 辅助扩展，不作为严格人工 Gold；
- ResearchArcade OpenReview 数据经 HF metadata 核验为非 gated；原始 parquet 下载遇到远端断连/SSL EOF，已改用 HF converted parquet 落地为扩容候选；
- Review-5K 经 HF metadata 核验为 auto-gated，已记录授权步骤；
- NLPEERv2 仍为 TUdataLib restricted file access，已记录授权路径和落地目录纪律；
- 新增 `scripts/validate_data_expansion_2026_06_17.py`，输出 `.omx/specs/autoresearch-data-expansion-2026-06-17/result.json`。

### Task 3-E：新增数据 Schema Inspection

- 使用 Hugging Face Dataset Viewer API 核验 PeerQA-XT 与 ResearchArcade 的 split、size、parquet URL 和 first rows；
- PeerQA-XT 确认为 12,628 行，字段为 `pid/qid/question/answer/paper/domain`；
- PeerQA-XT train/validation/test 分别为 10,128 / 1,248 / 1,252 行；
- ResearchArcade converted parquet 确认为 737,577 行，字段为 `venue/paper_openreview_id/review_openreview_id/title/time`；
- 明确 ResearchArcade converted 只提供 OpenReview thread metadata，不含完整 review text，不能直接替代评审正文数据；
- 新增 `reports/dataset_schema_inspection_2026-06-17.md` 和 `scripts/validate_dataset_schema_inspection_2026_06_17.py`；
- 本阶段提升的是数据准备度，不是模型指标；未复跑 E2/E6，不能声称相对 baseline 的性能提升。

### Task 3-F：候选数据源扩展与下载核验

- 使用 Hugging Face Dataset Viewer 与 `hf download --dry-run` 核验多组 peer-review 数据候选；
- 新增 OpenReview Raw HF shard0：`Jasonpicky/openreview_raw` 的 README 与首个 parquet 分片已落地，文件约 148MB，parquet 首尾 magic 均为 `PAR1`；
- 新增 NeurIPS 2023 partial：`djroytburg/NeurIPS-2023-2025` 的 README 与 2023 JSONL 已落地，包含 3,395 篇记录，字段含 `paper_text/reviews/accepted`；
- 新增 PeerCheck：`TrustAIRLab/PeerCheck` 的 README 与 100 行 JSONL 已落地，字段为 `file/answer`，适合 evidence-style review attribution 诊断；
- 新增 ReviewRebuttal test：`xxxxxsss/ReviewRebuttal` 的 README、1,000 篇 test reviews JSON 和 test parquet 已落地，字段含 reviews、metareview 与 decision；
- 明确 ReviewRebuttal 总存储约 13.7GB，本轮只下载 test reviews，不盲目下载 `papers.zip`；
- 明确 Review-5K 与 DeepReview-13K 当前仍需授权或登录访问，不能计为已下载数据；
- 下载后删除 HF 生成的本地 `.cache` 目录，只保留 README 与实验数据文件；
- 新增 `reports/dataset_candidate_expansion_2026-06-17.md` 与 `scripts/validate_dataset_candidate_expansion_2026_06_17.py`；
- 本阶段只提升数据准备度，没有复跑 E2/E4/E5/E6，不能声称相对 baseline 的模型性能提升。

### Task 3-G：候选数据处理适配

- 新增 `evireview.dao.candidate_datasets`，处理 NeurIPS 2023、ReviewRebuttal test 与 PeerCheck；
- 新增 `scripts/process_candidate_datasets_2026_06_17.py`，把可直接读取的 JSON/JSONL 数据生成本地 processed 快照；
- NeurIPS 2023 抽样 50 篇论文，生成 5,974 个 EvidenceBlock 和 230 条 review；
- ReviewRebuttal test 统计 1,000 篇论文、3,681 条 reviews、1,000 条 metareview、6,335 条 rating 记录；
- PeerCheck 统计 100 行 review、856 个引用标记、90 条 Weaknesses section、77 条 Overall Score；
- OpenReview Raw shard0 只做 parquet 文件边界检查，因当前依赖不含 `pyarrow/pandas`，event filter 暂缓；
- 处理后的正文与 review pool 保持本地化，不提交第三方正文和 review 文本；
- 新增 `reports/candidate_dataset_processing_2026-06-17.md` 与 `scripts/validate_candidate_dataset_processing_2026_06_17.py`；
- 本阶段提升的是数据处理能力，没有复跑 E2/E4/E5/E6，不能声称相对 baseline 的模型性能提升。

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
- 使用 OpenReview ICLR 2025 seed 的 30 篇论文和 122 条 Official Review 作为报告组装输入；
- 保留 B1 review-derived Top-K 结构化报告作为可追踪报告上界；
- 新增 B2 system-generated deterministic baseline，只读取论文标题、摘要、关键词和领域元数据；
- B2 每条 Top-K 弱点保留 `candidate_id`、aspect、suggestion 和 paper content evidence id；
- 与 B0 Unstructured Review Dump 对比，B2 System-Generated Structured Report 的 Trace Coverage
  从 0.0000 提升到 1.0000；
- B2 Top-K Compliance 为 1.0000，Paper Report Coverage 为 1.0000；
- B2 Review Leakage Free 为 true，没有读取 Official Review 生成候选弱点；
- B2 Official Weakness Proxy Overlap@K 为 0.0504，说明本地启发式候选生成质量仍弱；
- 新增 B3 cue-aware deterministic baseline，根据 title/abstract/keywords 中的任务线索选择候选模板；
- B3 Trace Coverage、Top-K Compliance、Paper Report Coverage 均为 1.0000；
- B3 Review Leakage Free 为 true，没有读取 Official Review 生成候选弱点；
- B3 Official Weakness Proxy Overlap@K 为 0.0549，相对 B2 提升 0.0044；
- B3 Aspect Diversity@K 为 1.0000，Redundancy Rate@K 为 0.0000；
- 新增 B4 Agent-RAG Pipeline Report，复用 `evireview.system.AgentRAGReviewPipeline` 完成候选生成、
  Query Planner、Paper-RAG、support/refutation 双向审计、Adjudication 和 Meta-Reviewer Top-K；
- B4 Paper Report Coverage、Trace Coverage、Top-K Compliance、Pipeline Stage Coverage 和
  Support/Refutation Trace Coverage 均为 1.0000；
- B4 Official Weakness Proxy Overlap@K 为 0.0559，相对 B3 提升 0.0010；
- B4 Aspect Diversity@K 为 0.9111，低于 B3 的 1.0000，说明完整审计排序会牺牲少量 aspect 多样性；
- 新增 B5 Balanced Agent-RAG Pipeline Report，只在 Top-K 选择层加入 aspect-balanced selection
  和 `0.03` 候选先验权重，不改候选生成、检索、Support/Refutation 或 Adjudicator；
- B5 Official Weakness Proxy Overlap@K 为 0.0570，相对 B4 提升 0.0011，相对 B3 提升 0.0021；
- B5 Aspect Diversity@K 为 1.0000，相对 B4 提升 0.0889，Redundancy Rate@K 保持 0.0000；
- 新增 E6-B5 诊断实验，不改变系统输出，只分析 B3/B4/B5 Top-K 的 paper-level delta、
  aspect bottleneck、support/refutation 分布和失败样本；
- B5 相对 B4 为 7 篇提升、21 篇持平、2 篇退化；相对 B3 为 17 篇提升、2 篇持平、
  11 篇退化；
- B5 最弱 aspect 为 related_work，但样本数只有 1；更有代表性的瓶颈是 experiment，
  26 条候选的 Proxy Overlap@K 为 0.0510；
- B5 zero-overlap rate 为 0.0333，低 overlap cases 主要集中在 experiment、
  reproducibility 和 missing_baseline 组合；
- Accept/Reject Decision 数量为 0，保持辅助评审定位；
- arXiv unseen 5 篇论文仅生成 demo manifest，不报告 Gold 指标；
- E6 Autoresearch 验收通过。该阶段证明端到端报告组装、系统候选生成入口、cue-aware 小幅优化、
  Agent-RAG 系统编排、追踪和边界控制在 30 篇扩展 seed 上成立；B5 相对 B4 有小幅 proxy
  和多样性提升，但幅度仍小，不能宣称候选弱点已经达到高质量自动评审水平。

### E6-D：候选生成诊断与失败样本切片

- 新增 E6 candidate diagnostics，专门分析 B2/B3 的 aspect 分布、paper-level delta 和失败样本；
- 该诊断使用 Official Review weakness 只作为离线 proxy，不进入候选生成和报告组装；
- B2 Overall Proxy Overlap@K 为 0.0504，B3 为 0.0549，平均 delta 为 0.0044；
- B3 在 30 篇 OpenReview seed 中 19 篇提升、11 篇退化，failure-or-tie rate 为 0.3667；
- B3 zero-overlap rate 从 B2 的 0.0556 降至 0.0222；
- B3 aspect 分布为 experiment 20、method 23、missing_baseline 16、novelty 18、related_work 3、
  reproducibility 10；
- B3 诊断中 experiment aspect overlap 为 0.0477，仍是后续优化重点之一；
- 输出 8 个 failure cases，作为下一步 provider-generated candidates 的第一批对照切片；
- E6-D Autoresearch 验收通过。该阶段优化的是误差分析与实验可解释性，不额外宣称 B3
  候选质量提升。

### E6-P：DeepSeek Provider 候选生成失败样本对照

- 新增 E6 provider-generated candidate failure-slice runner，在 E6-D 的 8 个 failure cases 上测试
  `deepseek-v4-flash-free`；
- Prompt 输入边界为论文 title、abstract、keywords、primary_area 和候选生成任务描述，不包含 Official Review；
- Provider 输出只允许生成 weakness、aspect、severity、suggestion、confidence 和本地 metadata evidence id；
- E6-P 工程验收通过，但实验 verdict 为 `failed_with_metrics`；
- B2 failure slice Proxy Overlap@K 为 0.0639，B3 failure slice 为 0.0483；
- P1 provider Proxy Overlap@K 为 0.0000，相对 B3 delta 为 -0.0483，相对 B2 delta 为 -0.0639；
- Provider 输出覆盖率为 0.0000，provider_failures 为 8，失败类型包括 ProviderHTTPError、JSONDecodeError
  和 ValueError；
- 结论：当前 DeepSeek provider 配置不能替代 B3 cue-aware deterministic candidates，后续应先修复
  provider 稳定性、限流和 JSON 输出格式，再重新做小样本对照。

### Agent-RAG 后端系统框架

- 新增 `src/evireview/system/` 系统编排层，把已有候选生成、Paper-RAG、双向证据审计、
  Adjudicator 与 Meta-Reviewer Ranker 组合成单篇论文自动评审链路；
- 新增 Query Planner，按 weakness aspect 固定声明 expected sections 与 expected evidence types；
- 新增 Paper Adapter，将 OpenReview/arXiv-like 输入转换为 `PaperDocument` 与 `EvidenceBlock`；
- 新增 Evidence-aware Meta-Reviewer 系统层 ranker，输出 Top-K 弱点、证据 ID、rank score 与
  confidence；
- 新增 `scripts/validate_agent_rag_system_framework.py`，输出
  `.omx/specs/autoresearch-agent-rag-system-framework/result.json`；
- 验收样例完成 9 个阶段、6 条候选审计轨迹和 3 条 Top-K 弱点；
- 系统 trace 显示 `paper_decision_produced=false`、`human_check_route=false`、`frontend_included=false`；
- 该系统层已接入 E6 作为 B4，在 OpenReview 30 篇 seed 上完成完整 Agent-RAG 链路验收；
- B4 相对 B3 的 proxy overlap delta 为 `+0.0010`，属于很小的结构性提升，主要价值是链路闭合。
- B5 在 B4 基础上加入 bounded Top-K optimizer，相对 B4 的 proxy overlap delta 为 `+0.0011`，
  aspect diversity delta 为 `+0.0889`，作为当前 E6 系统输出。

## 当前验证

```text
pytest:                         108 passed after E6-B5 diagnostics
E0 registered datasets:         8
Downloaded datasets:            6
Restricted datasets:            1 (NLPEERv2)
Local snapshots:                1
OpenReview valid PDFs:          30 / 30 complete seed; 35 / 100 expanded snapshot
arXiv unseen valid PDFs:         20 / 20 latest 2026-06-17 snapshot
PeerQA-XT auxiliary parquet:     4 / 4 files downloaded
ResearchArcade converted parquet: downloaded, pending schema inspection
OpenReview Raw HF shard0:        downloaded, 1 / 6 parquet shards
NeurIPS 2023 JSONL:              downloaded, 3,395 paper/review records
PeerCheck JSONL:                 downloaded, 100 evidence-style review records
ReviewRebuttal test:             downloaded, 1,000 review/metareview/decision records
NeurIPS processed sample:        50 papers / 5,974 evidence blocks / 230 reviews
ReviewRebuttal processed summary: 1,000 papers / 3,681 reviews / 1,000 metareviews
PeerCheck processed summary:     100 rows / 856 citation markers
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
Autoresearch E6 End-to-End Report:   passed (B5 balanced Agent-RAG; +0.0011 vs B4 proxy)
Autoresearch E6 B5 Diagnostics:      passed (B5 vs B4: 7 improved / 21 tied / 2 regressed)
Autoresearch E6 Candidate Diagnostics: passed
Autoresearch E6 Provider Candidates: passed (experiment verdict: failed_with_metrics)
Autoresearch Agent-RAG system framework: passed
Autoresearch Data Expansion 2026-06-17: passed with documented gaps
Autoresearch Dataset Schema Inspection 2026-06-17: passed
Autoresearch Dataset Candidate Expansion 2026-06-17: passed
Autoresearch Candidate Dataset Processing 2026-06-17: passed
Clean dataset layout:             passed (no nested Git/ZIP/legacy)
pip check:                      no broken requirements
```

## 当前限制

1. NLPEERv2 完整数据尚未获得访问授权；当前已写明 TUdataLib 申请路径，但不能计为已下载；
2. OpenReview 已有 30 篇完整 seed 和 100 篇 partial expansion；expanded-100 受 429 限流影响，暂不能替代完整主数据；
3. arXiv 未见集已扩展到 20 篇，但仍只用于最终演示，不能用于调参或 Gold 评价；
4. PeerQA-XT 已完整下载，但它是合成 QA，只能作为 E2 辅助扩展，不能替代 PeerQA 严格 Gold；
5. ResearchArcade OpenReview converted parquet 已下载，但还需要字段检查、样本计数和任务映射，才能进入正式数据注册表；
6. Review-5K 为 Hugging Face auto-gated，需要登录并同意数据条款后才能下载；
7. OpenReview Raw 当前只下载首个 parquet 分片，需 event filter 后才能进入正式统计；
8. NeurIPS 2023 数据含完整论文文本与 reviews，但公开拒稿不足会导致接受样本偏置，不能直接作为严格 accept/reject 评价；
9. ReviewRebuttal 已下载 test reviews，但未下载大体量 `papers.zip`，暂不能用作完整论文解析主数据；
10. NeurIPS 2023 简单章节识别仍把较多正文归到 introduction，E6 小规模复跑前需要校准 section detector；
11. 当前依赖不含 parquet reader，OpenReview Raw event filter 暂不能本地执行；
12. E2 正式实验已完成，但 PeerQA 上的 P4 未达到预设 Recall 与 Evidence-Type Match 增益；
13. PeerQA 映射后的证据类型以 paragraph 为主，PeerQA-XT 又是合成 QA，因此仍不足以单独证明 evidence-type prior 有效。

## 下一步

按照关键路径继续：

1. 把 NeurIPS 2023 processed sample 接入 E6 小规模 runner，先比较 B3/B5/Agent-RAG 在 50 篇样本上的 coverage、trace、aspect diversity 和 proxy overlap；
2. 为 ReviewRebuttal test 建立 review/metareview/decision 诊断表，先评价报告结构与 decision 辅助特征，不写成自动录用决策能力；
3. 小幅校准 NeurIPS section detector，重点减少 introduction 过度归类；
4. 如果允许增加 parquet reader，再对 OpenReview Raw shard0 做 event filter，统计 review/meta-review/decision 比例；
5. 编写 PeerQA-XT 适配器，把 `paper` 长文本切成 `EvidenceBlock`，先跑 validation/test 检索，不动原 PeerQA 严格 Gold；
6. 编写 ResearchArcade event registry，过滤 Official Review / Meta Review / Paper Decision 事件，并与 OpenReview seed ID 对齐；
7. 在 OpenReview API 限流恢复后复跑 expanded-100，目标是 `review_fetch_failures == 0` 且 `valid_pdfs >= 80`；
8. 申请 NLPEERv2，获批后按 `restricted -> primary` 受控流程解析；
9. 数据补齐后再回到 E6-B5/候选生成优化，优先处理 experiment 切片和 zero-overlap 候选；
10. 保留 E6 的报告追踪、Top-K、zero paper-level decision 和 unseen demo 验收边界。
