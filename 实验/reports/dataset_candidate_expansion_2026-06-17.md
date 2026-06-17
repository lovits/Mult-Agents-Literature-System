# 候选数据源扩展与下载核验报告（2026-06-17）

## 本轮目标

本轮只扩展和核验数据源，不做 Prompt、模型或排序参数优化。目标是解决当前进度文档中的两个限制：

1. OpenReview seed 规模偏小，端到端评审需要更大的完整论文与人类评审候选库；
2. E4/E6 需要更多可复用的评审文本、meta-review、decision 或 evidence-style review 数据，避免只围绕已有小数据集调参。

因此，本轮结论只表示**数据准备度提升**。未复跑 E2/E4/E6 正式实验，不能声称模型指标相对 baseline 提升。

## 已下载数据

| 数据源 | 本地路径 | 已下载内容 | 可用性判断 |
| --- | --- | --- | --- |
| `Jasonpicky/openreview_raw` | `dataset/raw/primary/openreview_raw_hf_shard0/` | README 与第 1 个 parquet 分片，约 148MB | 主数据扩容候选。字段包含 `forum_pdf_url`、`note_type`、`note_text`，可过滤 review/meta-review/decision，但当前只是 6 个分片中的 1 个 |
| `djroytburg/NeurIPS-2023-2025` | `dataset/raw/primary/neurips_2023_2025_2023_only/` | README 与 `data/2023.jsonl`，3,395 篇记录，约 259MB | 端到端论文+评审候选。字段包含 `paper_text`、`reviews`、`accepted`，但数据卡提示拒稿公开不足，accept 分布偏置明显 |
| `TrustAIRLab/PeerCheck` | `dataset/raw/evaluation/peercheck/` | README 与 `train.jsonl`，100 行，约 191KB | 小型 evidence-style review 诊断集。答案文本含引用式 evidence 标记，可用于格式与 attribution 诊断，不替代严格 Gold |
| `xxxxxsss/ReviewRebuttal` | `dataset/raw/evaluation/reviewrebuttal_test/` | README、`REVIEWS_test.json` 与 test parquet，1,000 篇测试记录，约 24MB | 全阶段同行评审评价候选。字段包含 reviews、rating、metareview、decision，可用于评审质量/一致性诊断；暂不下载 13GB 论文包 |

## HF 元数据核验

| 数据源 | HF 状态 | 规模与字段 | 本项目角色 |
| --- | --- | --- | --- |
| `Jasonpicky/openreview_raw` | 非 gated，license 为 ODC-BY | Dataset Viewer 显示 626,430 行、16 列、约 896MB parquet；字段含 `forum_id/forum_title/forum_abstract/forum_pdf_url/note_type/note_text/venue/year` | 优先作为 OpenReview review/meta-review/decision 文本扩容源 |
| `djroytburg/NeurIPS-2023-2025` | 非 gated，license 为 CC BY 4.0 | Dataset Viewer 显示 13,171 行、10 列、约 576MB parquet；字段含 `paper_text/reviews/accepted` | 作为完整论文+评审端到端样本候选，正式分类实验需处理接受样本偏置 |
| `TrustAIRLab/PeerCheck` | 非 gated，license 为 Apache-2.0 | Dataset Viewer 显示 100 行、字段为 `file/answer` | 证据引用格式、human-vs-LLM review quality 诊断 |
| `xxxxxsss/ReviewRebuttal` | 非 gated，license 为 Apache-2.0 | HF 仓库含 reviews/rebuttals parquet、JSON 和 `papers.zip`，总存储约 13.7GB；Dataset Viewer 当前无法解析 split | 只下载 test reviews，后续按需扩展，不盲目下载 `papers.zip` |
| `WestlakeNLP/Review-5K` | auto-gated | 未授权前 Dataset Viewer 返回 401 | 需登录并同意条款后再作为评价候选 |
| `WestlakeNLP/DeepReview-13K` | 访问受限或未授权 | Dataset Viewer 返回 401 | 仅记录为可申请候选，不能计入已下载数据 |
| `JerMa88/ICLR_Peer_Reviews` | 非 gated，MIT | 15,821 行、16 列、约 796MB parquet，含 `full_text/review/overall_score/thinking_trace` | 可作低优先级补充；有 thinking trace/prompt 风格，需避免混作人类真实评审 |
| `IntelLabs/AI-Peer-Review-Detection-Benchmark` | 非 gated | 多 config/split，字段含 `label/review/rating/confidence` | AI 评审检测任务，不是本系统主评审质量 Gold |

## 文件完整性检查

| 文件 | 检查 |
| --- | --- |
| `openreview_raw_hf_shard0/data/train-00000-of-00006.parquet` | 首尾 magic 均为 `PAR1`，文件存在且大于 100MB |
| `reviewrebuttal_test/reviews_parquet/test/test.parquet` | 首尾 magic 均为 `PAR1`，文件存在且大于 1MB |
| `peercheck/train.jsonl` | JSONL 可读，100 行，首行字段为 `file/answer` |
| `neurips_2023_2025_2023_only/data/2023.jsonl` | JSONL 可读，3,395 行，首行字段含 `paper_id/year/conference/accepted/title/abstract/keywords/pdf_url/paper_text/reviews` |
| `reviewrebuttal_test/REVIEWS_test.json` | JSON 可读，list 长度为 1,000，首条字段含 `paper_id/conference_year_track/reviews/review_initial_ratings_unified/review_final_ratings_unified/metareview/decision` |

下载后已删除 HF 本地 `.cache` 目录，只保留实验需要的 README 与数据文件。

## 与实验流程的对应关系

| 实验阶段 | 可接入数据 | 接入方式 |
| --- | --- | --- |
| E0 数据注册 | openreview_raw shard0、NeurIPS 2023、PeerCheck、ReviewRebuttal test | 增加 registry 条目与 schema validator，保持 raw 数据不入 Git |
| E2 Paper-RAG | NeurIPS 2023 paper_text、OpenReview PDF URL | 先从 NeurIPS 2023 抽样构造 EvidenceBlock；OpenReview shard0 需另行下载 PDF 或对齐现有 seed |
| E4 双向证据审计 | PeerCheck、ReviewRebuttal test | PeerCheck 用于 evidence citation 格式诊断；ReviewRebuttal 用于 review/metareview/decision 一致性诊断 |
| E5/E6 Top-K 评审报告 | openreview_raw、NeurIPS 2023、ReviewRebuttal test | 扩大候选论文与官方评审文本池，先做抽样，不立即全量跑 provider |
| 接收倾向分类辅助实验 | NeurIPS 2023、ReviewRebuttal test | 只能作为辅助分类验证，必须说明分布偏置，不能写成自动录用决策系统 |

## 授权与获取建议

### Review-5K

Review-5K 为 Hugging Face auto-gated 数据。获取步骤：

1. 打开 `WestlakeNLP/Review-5K` 数据页；
2. 使用 Hugging Face 账号登录；
3. 点击访问申请或同意数据条款；
4. 获批后只用临时环境变量下载，不把 token 写入仓库或 git credential；
5. 下载到 `dataset/raw/evaluation/review_5k/` 后再做 schema inspection。

### DeepReview-13K

DeepReview-13K 当前访问返回 401。获取步骤与 Review-5K 类似：先在数据页确认访问条件与许可，再申请或登录下载。未获批前不得把它写成已获得数据。

### NLPEERv2

NLPEERv2 仍是最适合硕士论文主数据的目标之一，但官方 TUdataLib 文件访问受限。继续按既有流程申请，获批后先放入 `dataset/raw/restricted/nlpeer/`，通过解析和 license 检查后再进入 `dataset/raw/primary/nlpeer_v2/`。

## 对 baseline 的影响

本轮没有复跑任何模型或检索实验，所以：

- 数据规模与可选评价源增加；
- E2/E4/E5/E6 的正式指标没有变化；
- 不能声称相对 baseline 有性能提升；
- 下一步可以先把 `NeurIPS 2023` 和 `ReviewRebuttal test` 接入 E0 registry 与抽样适配器，再复跑小规模 E6 pipeline。

## 下一步

1. 为 `NeurIPS 2023` 写 `PaperDocument` 适配器，抽样 50 篇生成 EvidenceBlock；
2. 为 `ReviewRebuttal test` 写 review/metareview/decision 解析器，建立评审文本诊断表；
3. 为 `openreview_raw` shard0 写 event filter，统计 review/meta-review/decision 的比例；
4. 将 PeerCheck 作为 evidence citation 格式诊断，不并入严格 Gold；
5. 完成上述适配后，再启动 E6 小规模复跑，比较 B3/B5/Agent-RAG 在扩大样本上的稳定性。
