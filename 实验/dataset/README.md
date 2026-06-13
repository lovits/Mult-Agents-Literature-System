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
| 未见论文测试集 | arXiv 最新论文 | 演示系统处理训练与调试阶段未使用的新论文 | 已冻结 5 篇 |

## 当前可复现实物

| 数据源 | 已获得内容 | 用途边界 |
| --- | --- | --- |
| OpenReview ICLR 2025 seed | 10 篇完整 PDF、投稿元数据、41 条 Official Review | 当前原始主数据 seed；后续按相同协议扩大 |
| PeerQA | 579 条标注 QA、24,265 条论文段落记录、未标注问题 | E2 Paper-RAG 严格检索评价 |
| CLAIMCHECK | 55 个 main source paper-review 对、43 个 related-work 对的文本标注 | E4 双向文本证据审计严格评价；当前不做多模态图表审计 |
| ReviewCritique | 100 篇人类评审论文、20 篇 LLM 评审论文及专家 deficiency 标注 | E1/E5/E6 辅助严格评价；禁止用于训练 |
| SubstanReview | 550 条专家标注评审，包含 claim-evidence 配对 span | E4 证据充分性与 E5 排序辅助评价 |
| 本地外部文献库 | 65 个 PDF/Markdown 文件 | E3 受控 Literature-RAG |
| arXiv unseen | 2026-06-13 冻结的 5 篇最新 `cs.CL` PDF | 只作最终未见论文演示，不作 Gold 指标 |
| NLPeer | 受限数据说明 | 完整 NLPEERv2 需申请，当前不能计为已下载 |

## 可用性结论

| 数据源 | 可用性 | 当前实验结论 |
| --- | --- | --- |
| OpenReview seed | 可用但规模不足 | 可打通完整论文处理和候选生成；正式端到端实验前必须扩大并冻结划分 |
| PeerQA | 可直接使用 | 具有映射到论文段落的 Gold evidence，是 E2 Paper-RAG 主评价集 |
| CLAIMCHECK | 可直接使用，限文本任务 | source 与 related-work 文本对适合 E4 支持/反驳证据审计；不能据此宣称多模态能力 |
| ReviewCritique | 可直接使用，限评价 | 可评价评审缺陷和报告质量；按数据说明不得作为训练集 |
| SubstanReview | 可直接使用，限辅助评价 | 可评价评审 claim 是否被 evidence substantiated；不能独立证明 weakness 正确 |
| 本地文献库 | 可用 | 可作为固定 Literature-RAG 语料；不同来源许可需分别遵守 |
| arXiv unseen | 可用，禁止调参 | 只证明系统能处理未见论文，不提供 Gold 质量结论 |
| NLPEERv2 | 当前不可用 | 完成申请前只保留受限状态，不计入已下载数据 |

## 数据源核验

- NLPeer 官方代码与用途说明：<https://github.com/UKPLab/nlpeer>
- NLPEERv2 官方数据页：<https://tudatalib.ulb.tu-darmstadt.de/items/d4a4061b-e4e3-4b1e-a90d-d48a3d69e3c0>
- OpenReview API 2 文档：<https://docs.openreview.net/getting-started/using-the-api>
- PeerQA Hugging Face：<https://huggingface.co/datasets/UKPLab/PeerQA>
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
