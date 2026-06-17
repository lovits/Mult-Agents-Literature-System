# 数据扩展与授权限制处理报告（2026-06-17）

## 本轮目标

本轮只处理数据规模与数据授权问题，不做模型、Prompt 或实验优化。目标是缓解 `PROGRESS.md` 中的主数据规模不足、未见论文规模较小、PeerQA 评价数据单一、NLPEERv2 未授权等限制。

## 已落地数据

| 数据 | 本地路径 | 状态 | 用途边界 |
| --- | --- | --- | --- |
| OpenReview ICLR 2025 expanded-100 | `dataset/raw/primary/openreview_iclr2025_expanded_100/` | 100 篇投稿元数据、229 条 Official Review、35 篇有效 PDF | 可作为主数据扩展诊断；因 429 限流导致 42 个 forum 抓取失败、65 个 PDF 失败，暂不替代 30 篇完整 seed |
| arXiv unseen 2026-06-17 | `dataset/raw/demo/arxiv_unseen_2026-06-17/` | 20 篇最新 `cs.CL`，20 个有效 PDF | 仅用于最终未见论文演示，不参与调参或 Gold 指标 |
| PeerQA-XT complete | `dataset/raw/evaluation/peerqa_xt/` | README、test、validation、两个 train parquet shard 已下载 | 辅助扩大 E2 QA/RAG 检索样本；由于数据由合成流程构造，不作为严格人工 Gold |
| ResearchArcade OpenReview converted | `dataset/raw/primary/researcharcade_openreview_papers_reviews/` | README 与 HF converted train parquet 已下载 | OpenReview paper-review metadata 扩容候选；进入主实验前需要 schema inspection 和抽样核验 |

## 已修复的下载稳定性问题

- `download_openreview.py` 增加有限重试，单篇 forum/PDF 下载失败不再中断整个快照；
- `download_arxiv_unseen.py` 增加有限重试，单篇 PDF 下载失败会写入 manifest，而不是导致整批失败；
- OpenReview expanded-100 的失败被显式记录到 manifest，可复盘 429 限流影响；
- arXiv unseen 20 篇扩展快照已完整下载，解决 5 篇 demo 规模过小的问题。

## 仍未完全解决的限制

1. **NLPEERv2 未授权**：官方 TUdataLib 页面显示 file access restricted。当前只能记录授权路径，不能把它计入已下载数据。
2. **OpenReview expanded-100 不完整**：OpenReview API 对 forum notes 和 PDF 下载出现 429，当前只作为扩展诊断快照。
3. **ResearchArcade 原始 data parquet 未落地**：HF metadata 已确认非 gated，原始 `data/train-00000-of-00001.parquet` 下载多次遇到远端断连/SSL EOF；当前使用 HF converted parquet 作为可验证候选快照。
5. **Review-5K 需要 Hugging Face 授权**：数据是 auto-gated，需登录并同意条款后下载。

## 数据源分工

| 任务 | 主用数据 | 辅助数据 | 禁止越界 |
| --- | --- | --- | --- |
| 完整论文处理与端到端评审 | OpenReview seed 30；后续 NLPEERv2 或 OpenReview complete expansion | OpenReview expanded-100 metadata/reviews；ResearchArcade converted metadata | 不用不完整 PDF 快照替代正式主数据 |
| Paper-RAG 检索评价 | PeerQA | PeerQA-XT complete | 不把合成 PeerQA-XT 当人工 Gold |
| 双向证据审计 | CLAIMCHECK、SubstanReview | ReviewCritique | 不宣称 CLAIMCHECK 有 covered/refuted 全量 Gold |
| Literature-RAG | 本地冻结文献库 | 后续可加入严格筛选论文 | 不把在线搜索混入主实验语料 |
| 未见论文演示 | arXiv unseen 2026-06-17 | 旧 2026-06-13 快照 | 不做调参、不报告 Gold 指标 |

## 授权和环境建议

### Hugging Face

建议先配置 HF 登录，否则大文件会受到未认证下载速率与稳定性限制：

```bash
实验/.venv-formal/bin/hf auth login
# 或设置环境变量，不要写入仓库：
export HF_TOKEN=...
```

PeerQA-XT 已补齐。如需重建快照：

```bash
实验/.venv-formal/bin/hf download UKPLab/PeerQA-XT \
  --type dataset \
  --local-dir 实验/dataset/raw/evaluation/peerqa_xt \
  --include 'data/train-00001-of-00002.parquet' \
  --max-workers 1
```

ResearchArcade 当前使用 HF converted parquet。如需重试原始 parquet：

```bash
实验/.venv-formal/bin/hf download ulab-ai/ResearchArcade-openreview-papers-reviews \
  --type dataset \
  --local-dir 实验/dataset/raw/primary/researcharcade_openreview_papers_reviews \
  --include 'README.md' \
  --include 'data/*.parquet' \
  --max-workers 1
```

### NLPEERv2

NLPEERv2 应作为最优主数据目标，但必须先获授权：

1. 访问 TUdataLib NLPEERv2 官方页面；
2. 登录 TUdataLib；
3. 申请受限文件访问，说明用途为非商业硕士毕业设计研究；
4. 获批后下载原始文件到 `dataset/raw/restricted/nlpeer/`；
5. 解析后再登记为 `primary/nlpeer_v2`，并保留 license 与版本记录。

### Review-5K

Review-5K 是 Hugging Face auto-gated 数据。登录 HF 后在数据页同意条款或申请访问，获批后再下载。该数据的数据卡明确其用途是 peer review process analysis，不应写成真实场景替代人工审稿数据。

## 对 progress 限制的处理结论

| 原限制 | 本轮处理 | 当前状态 |
| --- | --- | --- |
| NLPEERv2 未授权 | 写明授权路径与落地目录纪律 | 未解决但已可执行 |
| OpenReview 只有 30 篇 seed | 新增 expanded-100 快照 | 部分缓解；仍需完整 PDF/review 重试 |
| arXiv unseen 只有 5 篇 | 扩到 20 篇且 PDF 全部有效 | 已解决 demo 规模限制 |
| E2 PeerQA 数据单一 | 增加 PeerQA-XT complete | 已缓解数据规模限制；仍不能替代人工 Gold |
| evidence-type prior 证据不足 | 记录 PeerQA-XT 合成属性和边界 | 未解决；仍需 NLPEERv2/结构化论文解析支撑 |

## 下一步

1. 对 PeerQA-XT 与 ResearchArcade converted parquet 做 schema inspection，生成字段表、样本计数和可用任务映射；
2. 在 OpenReview API 限流恢复后复跑 expanded-100，目标是 `valid_pdfs >= 80` 且 `review_fetch_failures == 0`；
3. 申请 NLPEERv2，并将获批文件纳入 `restricted -> primary` 的受控解析流程；
4. 数据补齐后再启动下一轮实验优化，避免在 seed 规模上继续过度调参。
