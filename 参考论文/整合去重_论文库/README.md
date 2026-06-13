# 整合去重版论文库

本目录是从 `paper/` 下所有论文资料整理出来的去重版本。原始目录没有删除，方便回溯。

## 目录结构

| 目录 | 内容 |
|---|---|
| `PDF/` | 去重后的论文 PDF，共 32 篇。 |
| `Markdown_解析与笔记/` | 去重后的 MinerU Markdown、精读笔记和已有说明文档，共 19 份。 |
| `解析结果_MD/` | 已统一整理的 32 篇论文 Markdown，可直接用于 RAG 入库、论文分析和后续笔记。 |
| `解析状态.csv` | 每篇 PDF 的解析来源、状态和字符数。 |
| `MinerU_API_结果/` | 本次 MinerU API 返回的原始 zip、解压结果和批量任务记录。 |

## 解析状态

- 32 篇 PDF 已全部解析为 Markdown。
- 其中 15 篇复用了已有 MinerU 解析结果。
- 其中 17 篇通过 MinerU API 新解析补齐。
- 当前 `解析状态.csv` 中 32 条记录均为 `ok`。

## 去重规则

1. 先按文件 SHA-256 去除完全相同的 PDF。
2. 再手动处理同一论文的不同命名/旧副本：
   - `DeepReview` 保留可正常解析的 `08_DeepReview_DeepReview13K_2503.08569.pdf`。
   - `ReviewAgents` 保留 arXiv 元数据完整的 `09_ReviewAgents_Bridging_the_Gap_Between_Human_and_AI_2503.08506.pdf`。
3. 原始目录中的文件全部保留，没有被删除。
4. 所有保留 PDF 均已通过 `pdfinfo` 基础完整性检查。

## 当前 PDF 清单

### 核心自动评审系统

- `01_MARG_Multi_Agent_Review_Generation.pdf`
- `03_FactReview_Evidence_Grounded_Reviews.pdf`
- `06_ReviewGrounder_Rubric_Guided_Tool_Integrated_Agents.pdf`
- `08_DeepReview_DeepReview13K_2503.08569.pdf`
- `09_ReviewAgents_Bridging_the_Gap_Between_Human_and_AI_2503.08506.pdf`
- `10_ScholarPeer_Context_Aware_Multi_Agent_Framework.pdf`
- `11_AgentReview_EMNLP2024.pdf`
- `13_Can_LLMs_Be_Trusted_Paper_Reviewers_2025.pdf`
- `REMOR_Automated_Peer_Review_Generation_with_LLM_Reasoning_2505.11718.pdf`
- `REM_CTX_Automated_Peer_Review_via_Reinforcement_Learning_2604.00248.pdf`
- `ReviewRL_Towards_Automated_Scientific_Review_with_RL_2508.10308.pdf`
- `Navigating_Through_Paper_Flood_Advancing_LLM_based_Paper_Evaluation_2508.05129.pdf`

### 数据集、评估与可靠性

- `02_PeerRead_Dataset_of_Peer_Reviews.pdf`
- `07_RottenReviews_Review_Quality_Benchmark.pdf`
- `12_Can_LLMs_Provide_Useful_Feedback_on_Research_Papers.pdf`
- `13_Is_LLM_a_Reliable_Reviewer.pdf`
- `14_RAGChecker_Fine_grained_RAG_Evaluation_2024.pdf`
- `14_SubstanReview_Automatic_Analysis_of_Substantiation.pdf`
- `15_Can_We_Automate_Scientific_Reviewing.pdf`
- `15_RefChecker_Fine_grained_Hallucination_Checker_2024.pdf`
- `Unveiling_LLM_Evaluation_Focused_on_Metrics_2404.09135.pdf`

### Agentic RAG、论文分析与新颖性评估

- `04_OpenNovelty_Verifiable_Scholarly_Novelty_Assessment.pdf`
- `05_NoveltyAgent_Pointwise_Novelty_Analysis.pdf`
- `16_MA_RAG_Multi_Agent_RAG_2025.pdf`
- `Paper_Circle_Open_source_Multi_agent_Research_Discovery_2604.06170.pdf`
- `AstroReview_LLM_driven_Multi_Agent_Framework_for_Telescope_Proposal_Review_2512.24754.pdf`

### 多智能体与 Agent 综述

- `A_Survey_on_Evaluation_of_Large_Language_Models_2307.03109.pdf`
- `Evaluation_and_Benchmarking_of_LLM_Agents_A_Survey_2507.21504.pdf`
- `Large_Language_Model_based_Multi_Agents_A_Survey_2402.01680.pdf`
- `Multi_Agent_Collaboration_Mechanisms_A_Survey_of_LLMs_2501.06322.pdf`
- `Reimagining_Peer_Review_Process_Through_Multi_Agent_Mechanism_Design_2601.19778.pdf`
- `Towards_Reasoning_in_LLMs_via_Multi_Agent_Peer_Review_2311.08152.pdf`

## 建议下一步

如果后续要写文献综述，建议基于这个目录继续做三件事：

1. 给每篇论文补充“研究问题、方法、数据集、指标、与本课题关系”。
2. 按课题主线重排为“自动评审生成、证据验证、审稿质量评估、论文分类、多智能体 RAG”五类。
3. 形成一张可直接放进开题/毕业论文的文献对比表。
