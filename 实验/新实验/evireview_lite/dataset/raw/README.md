# EviReview-Lite 数据快照

本目录包含新实验使用的数据快照。大体积原始数据不进入 Git；来源、用途、监督等级和状态由
`conf/experiments/e0_data.yaml` 管理。

## 四层数据方案

1. `raw_primary`：NLPeer / OpenReview，用于让系统实际处理完整论文与评审；
2. `strict_evaluation`：PeerQA / CLAIMCHECK / ReviewCritique，用于严格组件评价；
3. `literature_corpus`：本地固定论文库，用于受控 Literature-RAG；
4. `unseen_demo`：下载日期之后冻结的 arXiv 新论文，用于最终未见论文演示，不作为 Gold 指标。

## 当前快照

- `openreview/iclr2025_seed/`：10 篇 ICLR 2025 投稿 PDF、元数据和 41 条 Official Review；
- `peerqa/data/`：579 条带答案 QA、24,265 个论文段落记录及未标注问题；
- `claimcheck/repository/`：官方仓库完整浅克隆，包含主标注和证据图像；
- `reviewcritique/repository/`：100 条专家 ReviewCritique 与 20 条 LLM ReviewCritique；
- `arxiv_unseen/2026-06-13/`：5 篇最新 `cs.CL` 论文 PDF，仅用于未见论文演示；
- `local_literature/source`：指向项目已有固定外部文献库；
- `nlpeer/loader/`：仅含官方 loader。NLPEERv2 完整数据必须单独申请，当前不得标记为已下载。
