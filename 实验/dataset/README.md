# EviReview-Lite 数据方案与当前快照

## 目录约束

```text
dataset/
├── README.md
├── processed/                  # 当前实验生成的可再生中间数据
└── raw/
    ├── primary/               # 完整论文与人类评审主数据
    ├── evaluation/            # 带 Gold 标注的严格评价数据
    ├── literature/            # Literature-RAG 固定语料
    ├── demo/                  # 不参与调参的未见论文
    └── restricted/            # 尚需申请、不得伪装为已下载的数据
```

数据目录不保存第三方仓库源码、嵌套 `.git`、重复压缩包或历史实验数据。

## 验收结论

自动论文评审系统需要同时具备四层数据，任何单一数据集都不能独立证明系统有效：

| 数据层 | 数据源 | 作用 | 当前状态 |
| --- | --- | --- | --- |
| 原始完整论文主数据 | NLPeer / OpenReview | 实际运行论文解析、候选生成与端到端评审 | OpenReview seed 已下载；NLPEERv2 待申请 |
| 严格评价数据 | PeerQA / CLAIMCHECK / ReviewCritique | 分别验证检索、证据审计和评审质量 | 已下载 |
| 外部文献库 | 本地 PDF/Markdown 成对论文库 | 支撑受控 Literature-RAG | 已挂载固定快照 |
| 未见论文测试集 | arXiv 最新论文 | 演示系统处理训练与调试阶段未使用的新论文 | 已冻结 20 篇扩展快照 |

## 当前可复现实物

| 数据源 | 已获得内容 | 用途边界 |
| --- | --- | --- |
| OpenReview ICLR 2025 seed | 30 篇完整 PDF、投稿元数据、122 条 Official Review | 当前完整可复现主数据 seed |
| OpenReview ICLR 2025 expanded-100 | 100 篇投稿元数据、229 条 Official Review、35 篇有效 PDF | 主数据扩展快照；受 OpenReview 429 限流影响，暂不替代 30 篇完整 seed |
| PeerQA | 579 条标注 QA、24,265 条论文段落记录、未标注问题 | E2 Paper-RAG 严格检索评价 |
| PeerQA-XT | README、test、validation 与两个 train parquet shard 已落地 | E2 辅助扩展检索/QA 数据；合成 QA，不作为严格 Gold |
| ResearchArcade OpenReview | README 与 HF converted train parquet 已落地 | OpenReview paper-review metadata 扩容候选；正式入主实验前需做 schema inspection 与抽样核验 |
| OpenReview Raw HF shard0 | README 与第 1 个 parquet 分片已落地 | OpenReview review/meta-review/decision 文本扩容候选；当前只下载 6 个分片中的 1 个 |
| NeurIPS 2023 partial | README 与 2023 JSONL 已落地 | 完整论文文本与 reviews 端到端样本候选；存在公开拒稿不足导致的接受样本偏置 |
| CLAIMCHECK | 55 个 main source paper-review 对、43 个 related-work 对的文本标注 | E4 双向文本证据审计严格评价；当前不做多模态图表审计 |
| ReviewCritique | 100 篇人类评审论文、20 篇 LLM 评审论文及专家 deficiency 标注 | E1/E5/E6 辅助严格评价；禁止用于训练 |
| SubstanReview | 550 条专家标注评审，包含 claim-evidence 配对 span | E4 证据充分性与 E5 排序辅助评价 |
| PeerCheck | README 与 100 行 JSONL 已落地 | evidence-style review 格式与 attribution 诊断；不替代严格 Gold |
| ReviewRebuttal test | README、1,000 篇 test reviews JSON 与 test parquet 已落地 | 全阶段评审文本、meta-review、decision 诊断候选；暂不下载 13GB 论文包 |
| 本地外部文献库 | 65 个 PDF/Markdown 文件 | E3 受控 Literature-RAG |
| arXiv unseen | 2026-06-17 冻结的 20 篇最新 `cs.CL` PDF | 只作最终未见论文演示，不作 Gold 指标 |
| NLPeer | 受限数据说明 | 完整 NLPEERv2 需申请，当前不能计为已下载 |

## 可用性结论

| 数据源 | 可用性 | 当前实验结论 |
| --- | --- | --- |
| OpenReview seed | 可用但规模不足 | 可打通完整论文处理和候选生成；正式端到端实验前必须扩大并冻结划分 |
| OpenReview expanded-100 | 部分可用 | 可用于论文元数据和评审文本扩容；因 PDF 与 forum 抓取受限，不能替代完整主数据 |
| PeerQA | 可直接使用 | 具有映射到论文段落的 Gold evidence，是 E2 Paper-RAG 主评价集 |
| PeerQA-XT | 可用，限辅助 | 非 gated、CC BY-NC-SA 4.0，可用于辅助扩大 QA 检索样本；因是合成 QA，不替代 PeerQA 严格 Gold |
| ResearchArcade OpenReview | 可用，待 schema inspection | 非 gated，已落地 HF converted parquet；可作为 OpenReview paper-review metadata 扩容候选 |
| OpenReview Raw HF shard0 | 可用，限候选 | 非 gated，ODC-BY；字段含 `note_type/note_text/forum_pdf_url`，适合作 review 文本扩容，当前只下载首分片 |
| NeurIPS 2023 partial | 可用，限候选 | 非 gated，CC BY 4.0；3,395 篇含 `paper_text/reviews/accepted`，但接受样本比例偏置，分类实验需谨慎 |
| CLAIMCHECK | 可直接使用，限文本任务 | source 与 related-work 文本对适合 E4 支持/反驳证据审计；不能据此宣称多模态能力 |
| ReviewCritique | 可直接使用，限评价 | 可评价评审缺陷和报告质量；按数据说明不得作为训练集 |
| SubstanReview | 可直接使用，限辅助评价 | 可评价评审 claim 是否被 evidence substantiated；不能独立证明 weakness 正确 |
| PeerCheck | 可用，限诊断 | 100 行 evidence-style review，可用于 citation/attribution 格式检查，不作为主评价集 |
| ReviewRebuttal test | 可用，限诊断 | 1,000 篇 test reviews，含 metareview 和 decision；可做 full-stage review 诊断，不盲目下载 `papers.zip` |
| 本地文献库 | 可用 | 可作为固定 Literature-RAG 语料；不同来源许可需分别遵守 |
| arXiv unseen | 可用，禁止调参 | 只证明系统能处理未见论文，不提供 Gold 质量结论 |
| NLPEERv2 | 当前不可用 | 完成申请前只保留受限状态，不计入已下载数据 |

## 新增候选数据与授权状态（2026-06-17）

| 数据源 | 状态 | 本项目建议用途 |
| --- | --- | --- |
| `UKPLab/PeerQA-XT` | Hugging Face 非 gated；license 为 CC BY-NC-SA 4.0；本地已下载 4/4 个 parquet 文件 | 辅助扩大 E2 QA 检索实验；不得替代 PeerQA 人工标注 Gold |
| `ulab-ai/ResearchArcade-openreview-papers-reviews` | Hugging Face 非 gated；原始 data parquet 下载遇到 SSL/远端断连，HF converted parquet 已落地 | 下一轮做 schema inspection 后补主数据规模，用于 OpenReview paper-review metadata 扩容 |
| `WestlakeNLP/Review-5K` | Hugging Face `gated: auto`；需登录后申请/同意数据条款 | 只作 peer review analysis 辅助评价，不用于宣称替代人工审稿 |
| `JerMa88/ICLR_Peer_Reviews` | Hugging Face 非 gated；MIT；体量约 799MB | 可作为轻量文本评审辅助数据，优先级低于 OpenReview/NLPEERv2 |
| `Jasonpicky/openreview_raw` | Hugging Face 非 gated；ODC-BY；已下载首个 parquet 分片 | 优先作为 OpenReview 评审文本扩容候选，正式使用前需 event filter |
| `djroytburg/NeurIPS-2023-2025` | Hugging Face 非 gated；CC BY 4.0；已下载 2023 JSONL | 优先作为完整论文+评审端到端扩容候选，需标记接受样本偏置 |
| `TrustAIRLab/PeerCheck` | Hugging Face 非 gated；Apache-2.0；已下载 100 行 JSONL | evidence-style review attribution 小型诊断 |
| `xxxxxsss/ReviewRebuttal` | Hugging Face 非 gated；Apache-2.0；已下载 test reviews，不下载 `papers.zip` | full-stage peer-review 诊断候选，后续按需扩展 |
| `WestlakeNLP/DeepReview-13K` | Hugging Face 当前访问返回 401 | 需申请或登录后再判断是否适合本实验 |

### 受限数据授权获取

NLPEERv2 当前在 TUdataLib 显示 `File access restricted`，license 为 CC BY-NC 4.0。获取步骤：

1. 打开 NLPEERv2 官方数据页并登录 TUdataLib；
2. 使用机构账号、ORCID 或站点支持的个人账号完成身份认证；
3. 在数据页申请受限文件访问，说明用途为非商业硕士毕业设计研究；
4. 获批后下载 `nlpeer_v2_nodata.zip` 及所需子集，例如 ARR/EMNLP/PLOS/ELIFE；
5. 将原始压缩包放入 `dataset/raw/restricted/nlpeer/`，解析后的可用快照再进入 `dataset/raw/primary/nlpeer_v2/`；
6. 未获批前，所有实验报告必须继续标记为 `requires_application`，不得把 NLPEERv2 计入已下载数据。

Review-5K 当前为 Hugging Face auto-gated。获取步骤：

1. 登录 Hugging Face；
2. 打开 `WestlakeNLP/Review-5K` 数据页；
3. 点击页面上的访问申请/同意条款按钮；
4. 获批后用 `HF_TOKEN` 登录本地 CLI，再下载到 `dataset/raw/evaluation/review_5k/`；
5. 使用时保留数据卡约束：它用于 peer review process analysis，不用于真实场景自动替代人工评审。

## 数据源核验

- NLPeer 官方代码与用途说明：<https://github.com/UKPLab/nlpeer>
- NLPEERv2 官方数据页：<https://tudatalib.ulb.tu-darmstadt.de/items/d4a4061b-e4e3-4b1e-a90d-d48a3d69e3c0>
- OpenReview API 2 文档：<https://docs.openreview.net/getting-started/using-the-api>
- PeerQA Hugging Face：<https://huggingface.co/datasets/UKPLab/PeerQA>
- PeerQA-XT Hugging Face：<https://huggingface.co/datasets/UKPLab/PeerQA-XT>
- ResearchArcade OpenReview Hugging Face：<https://huggingface.co/datasets/ulab-ai/ResearchArcade-openreview-papers-reviews>
- OpenReview Raw Hugging Face：<https://huggingface.co/datasets/Jasonpicky/openreview_raw>
- NeurIPS 2023-2025 Hugging Face：<https://huggingface.co/datasets/djroytburg/NeurIPS-2023-2025>
- PeerCheck Hugging Face：<https://huggingface.co/datasets/TrustAIRLab/PeerCheck>
- ReviewRebuttal Hugging Face：<https://huggingface.co/datasets/xxxxxsss/ReviewRebuttal>
- Review-5K Hugging Face：<https://huggingface.co/datasets/WestlakeNLP/Review-5K>
- DeepReview-13K Hugging Face：<https://huggingface.co/datasets/WestlakeNLP/DeepReview-13K>
- CLAIMCHECK 官方仓库：<https://github.com/JHU-CLSP/CLAIMCHECK>
- ReviewCritique 官方仓库：<https://github.com/jiangshdd/ReviewCritique>
- SubstanReview 官方仓库：<https://github.com/YanzhuGuo/SubstanReview>
- SubstanReview 论文：<https://aclanthology.org/2023.findings-emnlp.684/>
- arXiv API User Manual：<https://info.arxiv.org/help/api/user-manual.html>

## 实验使用纪律

1. OpenReview/NLPeer 用于完整系统运行，不直接替代组件 Gold 评价。
2. PeerQA、CLAIMCHECK、ReviewCritique 只用于其标签支持的评价任务。
3. ReviewCritique 明确禁止用于模型训练，本项目仅用于评价和分析。
4. arXiv unseen 数据不参与 Prompt、阈值或排序权重调整。
5. 本地 Literature-RAG 语料使用固定快照；在线搜索结果不能混入主实验。
6. NLPEERv2 在申请完成前保持 `requires_application`，不得伪造下载完成状态。

## 验收命令

```bash
cd 实验
../.venv/bin/python scripts/run_e0.py --config conf/experiments/e0_data.yaml
../.venv/bin/python scripts/validate_dataset_bootstrap.py
```

通过标准：四层数据检查均为 `passed`，同时 NLPeer 状态保持显式受限。
