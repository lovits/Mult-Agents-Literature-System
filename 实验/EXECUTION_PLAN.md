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

### 阶段 C：E4 双向证据审计

1. 使用 CLAIMCHECK 构造支持、反驳和已覆盖样本。
2. 加入 SubstanReview claim-evidence 充分性辅助评价。
3. 比较 Direct Judge、Support-only、Support+Refutation、完整 Adjudicator。
4. 输出 keep/rewrite/reject/uncertain 混淆矩阵与失败样本。

主指标：Valid-Issue Precision、Covered/Refuted Recall、False-Keep Rate、Evidence Attribution Accuracy。
辅助指标：Claim Evidence Coverage、Substantiated Claim Rate。

### 阶段 D：E3 Literature-RAG

1. 固定本地文献快照与时间过滤规则。
2. 实现元数据与引用字段校验。
3. 比较无外部检索、BM25、Hybrid、Hybrid+metadata filter。
4. 输出无效引用与未来文献泄漏日志。

主指标：Recall@10、Literature Relevance@10、Citation Validity Rate。

### 阶段 E：E5 Meta-Reviewer

1. 实现证据感知去重和排序。
2. 分别报告 major/minor 和三个 reviewer aspect。
3. 比较 severity-only、semantic dedup、evidence-aware ranker。

主指标：Top-5 Precision、Major Weakness Coverage、Redundancy Rate、Confidence Calibration。

### 阶段 F：E1/E6 端到端评审

1. 扩大 OpenReview 完整论文快照并冻结划分。
2. 运行三个 Reviewer 候选生成实验。
3. 串联 E2/E3/E4/E5，生成自动 Top-K 评审。
4. 在 arXiv unseen 上仅做演示，不报告 Gold 指标。

## 5. 当前立即执行项

1. 下载并验收 SubstanReview。
2. 实现 E2 正式批量运行器的最小可运行版本。
3. 使用确定性本地 embedding 先完成 smoke 与数据链路验收。
4. 配置正式 embedding 后运行可写入论文的 P0-P4 实验。

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
