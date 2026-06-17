# 候选数据处理适配报告（2026-06-17）

## 本轮目标

本轮在已下载候选数据的基础上做第一步处理适配，不做模型、Prompt 或排序优化。目标是把可直接读取的 JSON/JSONL 数据转成后续 Agent-RAG 实验可以使用的本地 processed 快照，并明确哪些数据还不能进入正式指标。

首次处理阶段没有复跑 E2/E4/E5/E6，因此不能声称相对 baseline 的模型性能提升。后续已补充一次
section detector 校准，并在 E6-N 中复跑端到端稳定性诊断；该复跑只证明结构切分对
Agent-RAG proxy overlap 有小幅正向影响，仍不能证明 B5 排序策略优于 B4。

## 处理结果

| 数据源 | 处理动作 | 本轮结果 | 后续用途 |
| --- | --- | --- | --- |
| NeurIPS 2023 | 从 `paper_text` 切分 `EvidenceBlock`，并抽取 review pool；补充 numbered / LaTeX / common aliases section detection | 抽样 50 篇论文，生成 5,974 个 EvidenceBlock 和 230 条 review | E6-N 小规模稳定性复跑，验证 Agent-RAG 在更大论文池上的输出边界 |
| ReviewRebuttal test | 汇总 reviews、metareview、decision 与 rating 记录 | 1,000 篇论文、3,681 条 reviews、1,000 条 metareview、6,335 条 rating 记录 | E4/E5/E6 的 full-stage review 诊断，不直接作为 weakness evidence Gold |
| PeerCheck | 统计 evidence-style citation markers、weakness section 与 score mention | 100 行 review，856 个引用标记，90 条包含 Weaknesses section，77 条含 Overall Score | 用于证据引用格式和 attribution 诊断 |
| OpenReview Raw shard0 | 只做 parquet 文件边界检查 | 首分片存在，155,450,613 bytes，首尾 magic 为 `PAR1` | 暂不解析；缺少已批准的 parquet reader，event filter 推迟 |

## NeurIPS 2023 EvidenceBlock 分布

| 维度 | 统计 |
| --- | --- |
| section 分布 | abstract 95；conclusion 58；discussion 23；experiments 602；front_matter 48；introduction 2,281；method 1,496；related_work 1,371 |
| evidence type 分布 | algorithm 473；figure_caption 69；implementation_detail 26；paragraph 5,336；table_caption 70 |

该分布说明：NeurIPS 2023 的 `paper_text` 足以支撑后续 Paper-RAG 切块与结构化检索实验。
section detector 校准后，introduction 从 3,422 降到 2,281，method 从 298 升到
1,496，experiments 从 522 升到 602。校准覆盖 numbered headings、Markdown headings、
LaTeX section headings、`Technical Overview`、`Preliminary`、`Experimental Evaluation`
和 `Related works` 等常见格式。

## ReviewRebuttal decision 分布

| decision | 数量 |
| --- | ---: |
| accept | 181 |
| accept (oral) | 9 |
| accept (poster) | 250 |
| accept (spotlight) | 36 |
| accept (talk) | 2 |
| accept: notable-top-25% | 9 |
| accept: notable-top-5% | 8 |
| accept: poster | 54 |
| reject | 451 |

ReviewRebuttal test 的 decision 分布比 NeurIPS 2023 更适合做评审流程诊断，但本轮只下载了 reviews/metareview/decision，没有下载大体量 `papers.zip`，所以暂不能作为完整论文解析主数据。

## 本地 artifacts

处理脚本生成的正文与 review pool 位于：

```text
dataset/processed/candidate_expansion_2026_06_17/
```

该目录下的 JSON/JSONL 文件由 `.gitignore` 保持本地化，不提交第三方正文与 review 文本。提交到仓库的是处理代码、validator、报告和进度记录。

## 对 baseline 的影响

本轮主要提升的是数据处理能力：

- 已经能把 NeurIPS 2023 的论文正文转成 `PaperDocument/EvidenceBlock`；
- 已经能把 NeurIPS review pool、ReviewRebuttal full-stage review 记录和 PeerCheck evidence-style review 记录纳入诊断；
- E6-N 复跑后，B4 Agent-RAG Proxy Overlap@K 从 0.0504 提升到 0.0510；
- B5 Balanced Agent-RAG Proxy Overlap@K 从 0.0499 提升到 0.0502；
- 但 B5 仍低于 B4，B5 相对 B4 的 delta 为 -0.000759；
- 因此只能说 section detector 校准对 Agent-RAG 证据链有小幅正向影响，不能声称最终 B5 相对 baseline 已提升。

## 下一步

1. 检查 E6-N 低 overlap 切片，区分候选生成、证据检索和 ranker 选择三类错误；
2. 为 ReviewRebuttal test 建立 review/metareview/decision 诊断表，先评价报告结构与 decision 辅助特征，不把它写成自动录用决策能力；
3. 如果允许增加 parquet reader，再对 OpenReview Raw shard0 做 event filter，统计 review/meta-review/decision 比例；
4. 继续保持 no human-check、no paper-level accept/reject decision 的系统边界。
