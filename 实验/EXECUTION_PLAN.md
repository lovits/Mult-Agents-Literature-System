# EviReview-Lite 具体实验执行方案

日期：2026-06-13
研究范围：多 Agent、双 RAG、双向证据审计自动论文评审后端实验

## 1. 执行原则

1. 每个实验先定义研究问题、数据、Baseline、指标和通过标准，再实现代码。
2. 所有新功能使用 TDD；每个阶段必须生成 Autoresearch 验收结果。
3. Gold、辅助评价、原始论文和未见演示数据分开报告。
4. 不因指标未达目标删除失败结果，失败样本和运行配置必须保留。
5. 论文借鉴只做能够单独消融的小幅优化，不新增不必要 Agent。

## 2. 数据准备顺序

| 顺序 | 数据源 | 状态 | 用途 |
| --- | --- | --- | --- |
| 1 | PeerQA | 已就绪 | E2 Paper-RAG Gold 检索评价 |
| 2 | SubstanReview | 本轮下载 | E4 claim-evidence 充分性与 E5 证据感知排序辅助评价 |
| 3 | CLAIMCHECK | 已就绪 | E4 支持/反驳双向审计主评价 |
| 4 | ReviewCritique | 已就绪 | E1/E5 报告质量辅助评价 |
| 5 | OpenReview seed | 已就绪，后续扩大 | 完整论文处理与端到端运行 |
| 6 | 本地文献库 | 已就绪 | E3 Literature-RAG |
| 7 | arXiv unseen | 已冻结 | E6 未见论文演示 |
| 8 | NLPEERv2 | 待申请 | 扩大端到端主数据 |

## 3. 论文借鉴与有限优化

### 3.1 SubstanReview

借鉴 claim-evidence pair 与 substantiation 的定义，将“评审意见是否有证据”从主观打分转为可计算的配对评价。

- 融入位置：E4 Evidence Adjudicator、E5 Meta-Reviewer。
- 新增指标：Claim Evidence Coverage、Substantiated Claim Rate。
- 边界：只作为辅助评价，不用于证明候选弱点本身正确。

来源：
- <https://aclanthology.org/2023.findings-emnlp.684/>
- <https://github.com/YanzhuGuo/SubstanReview>

### 3.2 FactReview

借鉴“外部证据必须附带可核验来源”的设计，为 Literature-RAG 输出保留标题、年份、文献 ID、链接和证据片段。

- 融入位置：E3 Literature-RAG。
- 新增指标：Citation Validity Rate。
- 边界：当前不加入代码执行与 artifact repair，避免工作量失控。

来源：<https://arxiv.org/abs/2604.04074>

### 3.3 Critical-problem review benchmark

借鉴“将严重错误识别作为独立子任务”的思路，在 E5 中分别报告 major weakness coverage，不只报告总体 Top-K Precision。

- 融入位置：E5 Meta-Reviewer。
- 新增切片：major / minor、method / experiment / reproducibility。
- 边界：不增加新的 Critical Reviewer Agent。

来源：<https://arxiv.org/abs/2505.23824>

### 3.4 RAGChecker

借鉴模块级诊断而非只报告单一总体分数的原则，在 E2 同时报告 Recall 与 Context Precision，区分“没有召回证据”和“召回了过多噪声”。

- 融入位置：E2 Paper-RAG。
- 新增指标：Precision@K，作为 Context Precision 的可复现近似。
- 边界：不引入新的 LLM Judge 或额外人工标注。

来源：<https://arxiv.org/abs/2408.08067>

## 4. 分阶段执行计划

### 阶段 A：数据冻结与协议验收

1. 下载 SubstanReview 官方 `train.jsonl` 和 `test.jsonl`。
2. 记录来源、许可、SHA256、样本数和字段。
3. 更新数据注册表和数据验收器。
4. 输出 Autoresearch 数据结果。

通过标准：

- 550 条记录可解析；
- train/test 分别为 440/110；
- 每条记录包含 `review` 和 `label`；
- 数据目录无第三方仓库源码或嵌套 Git。

### 阶段 B：E2 Paper-RAG 正式实验

1. 实现 PeerQA 批量运行器。
2. 实现 P0 BM25、P1 Dense、P2 Hybrid、P3 Structure-aware、P4 Evidence-type-aware。
3. 固定同一查询集、索引、top-k 和随机种子。
4. 输出样本级结果、聚合指标、错误日志和 manifest。
5. 运行 P0-P4 及三个消融。

主指标：Recall@5、MRR、nDCG@5、Evidence-Type Match、延迟。
通过标准：P4 相对最强 P0-P2 的 Recall@5 提高至少 5 个百分点，或记录为 `failed_with_metrics` 并进行错误分析。

执行结果：已完成，状态为 `failed_with_metrics`。高置信度先验门控使 P4
Recall@5 从 0.2532 恢复至 0.2863，但仅与最强 P2 持平；Evidence-Type
Match@5 未达到增益要求。为避免测试集过拟合，不继续调权重，进入 E4。

### 阶段 C：E4 双向证据审计

1. 使用 CLAIMCHECK 构造支持、反驳和已覆盖样本。
2. 加入 SubstanReview claim-evidence 充分性辅助评价。
3. 比较 Direct Judge、Support-only、Support+Refutation、完整 Adjudicator。
4. 输出 keep/rewrite/reject/uncertain 混淆矩阵与失败样本。

主指标：Valid-Issue Precision、Covered/Refuted Recall、False-Keep Rate、Evidence Attribution Accuracy。
辅助指标：Claim Evidence Coverage、Substantiated Claim Rate。

数据边界更新：CLAIMCHECK 可严格评价 claim association、groundedness、
agreement、subjectivity 和 weakness type，但公开文本标注没有逐条
`covered/refuted` Gold。Covered/Refuted Recall 不得直接从 CLAIMCHECK 宣称，
必须使用具有相应标签的数据源或明确标记为 proxy。

E4 基线执行结果：已完成。严格评价 91 条可映射 weakness，并保留 64 条排除
样本及原因。C1 BM25 Recall@5 为 0.7656，优于 C2 Dense 的 0.5458 和 C3
Hybrid RRF 的 0.6520，因此 A1-A4 首轮证据检索使用 BM25，后续优化必须通过
独立消融证明。W0 Pilot Prior 的 Weakness Type Macro-F1 为 0.1216，表明标签
预测需要实质模型能力。以上结果仅是证据审计前的 C/W 基线，不等同于完整
双向证据审计系统。

E4 协议 smoke 执行结果：已完成 Task 10/11 的固定 Support、Refutation 与
Adjudicator 数据链路，并在全部 155 条 main weakness 上生成双向审计轨迹。
所有引用约束与自动裁决完整性检查通过，但启发式 A4 agreement-proxy
Macro-F1 为 0.1164，低于 A3 的 0.2674。该结果证明简单覆盖词启发式会使
Refutation 过度触发，因此只作为工程 smoke 与错误分析，不作为正式 A0-A4
主结果。下一步必须使用 provider-backed 独立论证运行正式实验。

MiniMax-M2.7 provider 接入结果：已完成 A0-A4 runner、结构化输出解析、调用
成本和失败追踪。当前 Key 在中国区端点认证与模型发现通过，但首条校准样本的
6 次实际推理全部返回 HTTP 429 / MiniMax 2056（Token Plan 用量上限）。因此
状态为 `pending_quota`，当前 uncertain 回退不得作为正式模型结果。额度恢复后
先复跑 5 条校准，校准零失败后再扩大样本规模。

Agnes-2.0-Flash provider 结果：已完成 5 条校准与 20 条 agreement-proxy
分层 Pilot。有限网络重试消除了瞬时连接失败，Evidence Attribution Accuracy
达到 1.0000，但 A4 Macro-F1 为 0.1739，低于 A2 的 0.2635 与 A3 的
0.2480；A4 token 成本为 A2 的 3.1516 倍，也超过 2.5 倍目标。因此 Pilot
verdict 为 `failed_with_metrics`，不直接扩大至 155 条。下一轮只进行一次
Prompt 证据角色约束与 Adjudicator 输入压缩优化，再在同一分层 Pilot 复跑。

Agnes 一次有界优化结果：已在相同分层 Pilot20 上完成。严格证据角色约束与
紧凑 Adjudicator 输入使 A4 Macro-F1 从 0.1739 提升到 0.2910，超过本轮 A2
和 A3；A4/A2 token 比从 3.1516 降到 2.4829。但运行仍出现 2 次 Provider/
解析失败，Evidence Attribution Accuracy 为 0.8750。零失败门槛未通过，
因此状态为 `failed_with_metrics`，按冻结协议停止扩大，不进行第二轮调参。

SubstanReview 辅助评价结果：已完成 official train/test split 的
claim-evidence substantiation baseline。Test split 有 580 个 claim、241 个
supported claim；Claim Evidence Coverage 为 0.4155，Substantiated Claim
Rate 为 0.4251。最强 baseline 为 S0 Proximity，Supported F1 为 0.5925，
Evidence Hit@1 为 0.6680。该结果只作为 E4/E6 的辅助证据充分性指标，不证明
weakness validity，也不提供 covered/refuted Gold。

### 阶段 D：E3 Literature-RAG

1. 固定本地文献快照与时间过滤规则。
2. 实现元数据与引用字段校验。
3. 比较无外部检索、BM25、Hybrid、Hybrid+metadata filter。
4. 输出无效引用与未来文献泄漏日志。

主指标：Recall@10、Literature Relevance@10、Citation Validity Rate。

执行结果：已完成。冻结本地文献库包含 33 篇 Markdown，32 篇具备完整 citation
metadata。L0 无外部文献 Recall@10 为 0.0000；L1 Keyword、L2 Hybrid 和 L3
Hybrid+metadata filter 的 Recall@10 均为 1.0000。L3 MRR 为 0.9048，高于
L2 的 0.8929；Citation Validity Rate 为 1.0000；Future Leakage Count 从
L2 的 20 降至 0。结论是：受控 Literature-RAG 在不调用在线检索的前提下能够
为 novelty、related work 和 missing-baseline 类意见提供可复现外部证据，并
通过 as-of-year 过滤避免未来文献泄漏。该阶段 Autoresearch 验收通过。

### 阶段 E：E5 Meta-Reviewer

1. 实现证据感知去重和排序。
2. 分别报告 major/minor 和三个 reviewer aspect。
3. 比较 severity-only、semantic dedup、evidence-aware ranker。

主指标：Top-5 Precision、Major Weakness Coverage、Redundancy Rate、Confidence Calibration。

执行结果：已完成。E5 使用 CLAIMCHECK main 的 155 条候选弱点和 54 个
paper-review group，比较 R0 Input Order、R1 Text Severity、R2 Text Dedup
和 R3 Evidence-aware。为避免泄漏，ranker 不读取 E4 smoke trace 中由 gold
agreement 派生的 severity 字段；gold 仅用于计算 agreement proxy 指标。
R3 Evidence-aware 的 Top-K Agreement Precision 为 0.6543，与 R0/R1/R2 持平，
Keep Coverage@K 也均为 0.8298，说明当前 E4 heuristic audit trace 没有带来
可观察排序精度提升。R3 的 Confidence Brier 为 0.2515，相比 R0 的 0.6003 有
明显改善，但略弱于文本启发式 R1/R2 的 0.2400。该阶段结论为：Meta-Reviewer
工程链路、非泄漏特征边界和置信度评价成立，但 evidence-aware 排序尚不能宣称
优于文本启发式 baseline。Autoresearch 验收通过。

### 阶段 F：E1/E6 端到端评审

1. 扩大 OpenReview 完整论文快照并冻结划分。
2. 运行三个 Reviewer 候选生成实验。
3. 串联 E2/E3/E4/E5，生成自动 Top-K 评审。
4. 在 arXiv unseen 上仅做演示，不报告 Gold 指标。

执行结果：E6 报告组装阶段已完成三步。第一步使用 OpenReview seed 的 10 篇论文
和 41 条 Official Review 作为 report assembly 输入，从官方评审 weakness 字段
抽取候选弱点并生成 B1 review-derived Top-K 结构化报告，用作可追踪报告上界。
第二步新增 B2 system-generated deterministic baseline，只读取论文标题、摘要、
关键词和领域元数据，不读取 Official Review。相对 B0 Unstructured Review Dump，
B2 的 Trace Coverage 从 0.0000 提升到 1.0000，Top-K Compliance 为 1.0000，
Paper Report Coverage 为 1.0000，Review Leakage Free 为 true，Accept/Reject
Decision 数量为 0。B2 与 Official Review weakness 的弱文本重叠 proxy 为
0.0531，说明本地启发式候选生成可以打通自动评审链路，但候选质量仍较弱，
不能宣称已经达到高质量自动评审。第三步新增 B3 cue-aware deterministic
baseline，在相同无泄漏输入边界下根据 title/abstract/keywords 中的任务线索选择
候选模板。B3 的 Trace Coverage、Top-K Compliance、Paper Report Coverage 均为
1.0000，Review Leakage Free 为 true，Accept/Reject Decision 数量为 0；
Official Weakness Proxy Overlap@K 从 B2 的 0.0531 提升至 0.0610，delta 为
0.0079，Aspect Diversity@K 为 1.0000，Redundancy Rate@K 为 0.0000。该优化
方向正确但幅度有限，只能说明 cue-aware 模板带来小幅改进。arXiv unseen 5 篇
论文只生成 demo manifest，不报告 Gold 指标。

## 5. 当前立即执行项

1. 扩大 OpenReview seed，降低 10 篇样本带来的偶然性。
2. 将 B3 cue-aware deterministic candidates 与 Agnes/provider-generated candidates 做同协议对照。
3. 为候选生成继续报告 Official Weakness Proxy Overlap@K、aspect 分布和重复率。
4. 保持 E6 validator 要求 trace coverage、Top-K compliance、zero accept/reject 和 unseen no-Gold。

## 6. 正式实验环境要求

最低要求：

- Python 3.11+；
- 8GB 内存；
- 可访问 OpenReview、arXiv 和模型服务；
- API Key 仅通过环境变量传入。

正式 E2 Dense/Hybrid 实验还需要：

- 推荐 embedding：`BAAI/bge-base-en-v1.5` 或同级英文科学文本 embedding；
- 安装 `sentence-transformers`；
- 首次下载模型需要网络，之后固定模型版本与缓存；
- CPU 可运行，GPU 可显著缩短全量实验时间。

当前机器为 Apple M1 Pro、32GB 内存，能够在 CPU/MPS 上运行正式 E2；但现有
`.venv` 使用 Python 3.14.3，且未安装 `torch`、`sentence-transformers`、
`numpy`、`scipy` 和 `pandas`。为避免实验依赖与现有环境相互污染，正式实验应
使用独立 Python 3.12 环境：

```bash
cd /Users/qianye/Downloads/毕业设计/实验
uv venv --python 3.12 .venv-formal
uv pip install --python .venv-formal/bin/python -e '.[dev]'
uv pip install --python .venv-formal/bin/python sentence-transformers
```

正式 E2 runner 必须显式注入固定版本 embedding callable；传入正式模型名称但
未加载模型时会直接失败，不允许静默回退到 hashing embedding。

LLM Agent 阶段还需要：

```bash
# 在当前 shell 中设置以下变量，值不得写入仓库：
EVIREVIEW_LLM_BASE_URL
EVIREVIEW_LLM_MODEL
EVIREVIEW_LLM_API_KEY
```

不得将 Key 写入仓库。
