# 开题用论文清单

本文件夹整理了开题报告和文献综述中实际用到的核心论文，按阅读优先级编号。

## A. 必读：支撑 baseline、创新点和指标

| 编号 | 文件 | 作用 | 重点阅读 |
|---|---|---|---|
| 01 | `01_MARG_Multi_Agent_Review_Generation.pdf` | 主 baseline | 多 Agent 架构、ARIES、Recall/Precision/Jaccard、generic comments |
| 02 | `02_PeerRead_Dataset_of_Peer_Reviews.pdf` | 分类任务数据基础 | accept/reject 标签、论文草稿、专家评审数据 |
| 03 | `03_FactReview_Evidence_Grounded_Reviews.pdf` | 证据验证理论支撑 | claim extraction、evidence report、Supported/In conflict/Inconclusive 标签 |
| 04 | `04_OpenNovelty_Verifiable_Scholarly_Novelty_Assessment.pdf` | 可验证新颖性评估 | contribution claim、evidence verification as hard constraint |
| 05 | `05_NoveltyAgent_Pointwise_Novelty_Analysis.pdf` | point-wise RAG 分析参考 | novelty point decomposition、self-validation、checklist evaluation |
| 06 | `06_ReviewGrounder_Rubric_Guided_Tool_Integrated_Agents.pdf` | 评审质量评估参考 | ReviewBench、8 维 rubric、Evidence-Based Critique、meta-reviewer 局限 |
| 07 | `07_RottenReviews_Review_Quality_Benchmark.pdf` | 辅助质量评估 | Factuality、Vagueness、Actionability、Overall Quality |
| 08 | `08_DeepReview_DeepReview13K.pdf` | 分类/评分扩展数据 | DeepReview-13K、Decision Accuracy、F1、MSE/MAE、Spearman |

## B. 补充阅读：相关工作和动机

| 编号 | 文件 | 作用 | 重点阅读 |
|---|---|---|---|
| 09 | `09_ReviewAgents_Review_CoT.pdf` | 结构化审稿流程 | Review-CoT、Summarization/Analysis/Conclusion |
| 10 | `10_ScholarPeer_Context_Aware_Multi_Agent_Framework.pdf` | 强相关竞品 | historian agent、baseline scout、Q&A agent、动态检索 |
| 11 | `11_AgentReview_EMNLP2024.pdf` | 多智能体审稿模拟 | reviewer/author/AC 角色建模 |
| 12 | `12_Can_LLMs_Provide_Useful_Feedback_on_Research_Papers.pdf` | 研究动机 | LLM 反馈有用性与局限 |
| 13 | `13_Is_LLM_a_Reliable_Reviewer.pdf` | 可靠性动机 | LLM 直接评审的不稳定性 |
| 14 | `14_SubstanReview_Automatic_Analysis_of_Substantiation.pdf` | 评审意见证据支撑 | substantiation、评论是否有论据支持 |
| 15 | `15_Can_We_Automate_Scientific_Reviewing.pdf` | 早期自动评审工作 | ASAP-Review、自动评审生成早期路线 |

## 建议阅读顺序

1. 先读 `01_MARG`，明确本课题 baseline 和要改进的问题。
2. 再读 `03_FactReview`、`04_OpenNovelty`、`05_NoveltyAgent`，理解证据验证和 point-wise RAG 的理论来源。
3. 接着读 `06_ReviewGrounder`、`07_RottenReviews`，补充评估指标。
4. 最后读 `02_PeerRead`、`08_DeepReview`，确定分类扩展实验的数据和指标。

