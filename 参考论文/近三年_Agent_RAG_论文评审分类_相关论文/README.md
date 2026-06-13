# 近三年 Agent + RAG 论文评审/评估/分类相关论文

这个目录是按当前课题主线整理的论文包：

> 论文结构化分析 -> 证据检索/验证 -> 审稿意见质量评估 -> 论文质量或接收倾向分类。

## 推荐阅读顺序

| 顺序 | 文件 | 作用 |
|---:|---|---|
| 1 | `01_MARG_Multi_Agent_Review_Generation_2024.pdf` | 原始自动评审生成 baseline，可作为候选评论生成器。 |
| 2 | `02_FactReview_Evidence_Grounded_Reviews_2026.pdf` | 最贴近“证据验证”的论文，适合支撑核心创新点。 |
| 3 | `17_ReviewGrounder_arXiv_2026.pdf` | rubric + tool + grounding 的强相关框架，可参考评估维度和系统流程。 |
| 4 | `04_ScholarPeer_Context_Aware_Multi_Agent_Framework_2026.pdf` | search-enabled multi-agent 审稿系统，适合对比“外部文献上下文”的价值。 |
| 5 | `03_DeepReview_DeepReview13K_2025.pdf` | 结构化深度审稿与 DeepReview-13K 数据集，可用于分类/评分实验参考。 |
| 6 | `06_RottenReviews_Review_Quality_Benchmark_2025.pdf` | 审稿质量评估 benchmark，适合支撑“评论质量评估”任务。 |
| 7 | `10_SubstanReview_Review_Substantiation_2023.pdf` | 审稿意见中的 claim-evidence substantiation 分析，适合支撑“评论是否有证据”。 |
| 8 | `14_RAGChecker_Fine_grained_RAG_Evaluation_2024.pdf` | 通用 RAG 细粒度评估，可参考 Evidence Coverage、retrieval/generation 分解指标。 |
| 9 | `15_RefChecker_Fine_grained_Hallucination_Checker_2024.pdf` | claim-triplet 级幻觉检测，可参考你的评论级证据判断标签。 |
| 10 | `16_MA_RAG_Multi_Agent_RAG_2025.pdf` | 通用多智能体 RAG 架构，可参考 planner/extractor/QA agent 拆分。 |

## 按课题模块分类

### A. 自动审稿与多智能体评审

| 文件 | 建议用途 |
|---|---|
| `01_MARG_Multi_Agent_Review_Generation_2024.pdf` | baseline 或候选评论生成器。 |
| `07_ReviewAgents_Review_CoT_2025.pdf` | 结构化审稿推理过程与 Review-CoT 数据集参考。 |
| `08_AgentReview_EMNLP2024.pdf` | 多智能体模拟 peer review dynamics，适合放相关工作。 |
| `09_Can_LLMs_Provide_Useful_Feedback_2024.pdf` | 证明 LLM feedback 有用但不能替代人类审稿。 |
| `13_Can_LLMs_Be_Trusted_Paper_Reviewers_2025.pdf` | RAG + AutoGen + CoT 自动审稿可行性研究，可作为系统型对比。 |

### B. 证据验证、grounding、评论质量评估

| 文件 | 建议用途 |
|---|---|
| `02_FactReview_Evidence_Grounded_Reviews_2026.pdf` | claim extraction + literature positioning + execution verification，核心参考。 |
| `17_ReviewGrounder_arXiv_2026.pdf` | rubric-guided + tool-integrated + grounding，强相关。 |
| `06_RottenReviews_Review_Quality_Benchmark_2025.pdf` | Factuality、Vagueness、Actionability 等质量维度。 |
| `10_SubstanReview_Review_Substantiation_2023.pdf` | claim-evidence pair extraction，适合你的“评论证据性”任务。 |
| `15_RefChecker_Fine_grained_Hallucination_Checker_2024.pdf` | 细粒度幻觉检测方法，可迁移到评论验证。 |

### C. 论文分析、分类与外部文献上下文

| 文件 | 建议用途 |
|---|---|
| `03_DeepReview_DeepReview13K_2025.pdf` | DeepReview-13K 可支撑评分/接收倾向分类。 |
| `04_ScholarPeer_Context_Aware_Multi_Agent_Framework_2026.pdf` | 外部文献上下文、多 agent audit。 |
| `11_OpenNovelty_Verifiable_Novelty_Assessment.pdf` | 贡献点/新颖性验证。 |
| `12_NoveltyAgent_Pointwise_Novelty_Analysis.pdf` | point-wise novelty analysis，可用于论文创新点评估模块。 |

### D. 通用 Agentic RAG 方法

| 文件 | 建议用途 |
|---|---|
| `14_RAGChecker_Fine_grained_RAG_Evaluation_2024.pdf` | RAG 系统诊断指标。 |
| `16_MA_RAG_Multi_Agent_RAG_2025.pdf` | 多智能体 RAG 流程设计参考。 |

## 对开题报告的建议

建议把 MARG 从“唯一主 baseline”调整为“候选评论生成 baseline 之一”。新的主线可以写成：

> 本课题面向自动审稿中评论泛化、证据不足和分类解释性弱的问题，设计一个基于多智能体 RAG 的论文证据化分析、审稿意见评估与质量分类系统。系统通过论文解析、证据检索、评论验证、元评审排序和分类决策多个 Agent 协作，实现对论文内容的结构化理解、对审稿意见的证据一致性判断，以及对论文质量风险或接收倾向的可解释分类。

最建议作为核心对比的系统：

1. LLM Direct Review
2. MARG
3. MARG + LLM-only Filter
4. MARG + Paper-RAG Verifier
5. Ours: Agentic RAG Verifier + Meta-Reviewer Ranker + Classification

