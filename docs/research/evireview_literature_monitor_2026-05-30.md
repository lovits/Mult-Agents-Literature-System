# EviReview-Lite Literature Monitor: 2026-05-30

本轮目标：继续跟踪近两年 automated peer review、evidence-grounded review、Agentic RAG evaluation 论文，并把文献结论转成 A 版实验改动。

## 本轮新增/确认论文

| Paper | Status | Key Evidence | Impact on EviReview-Lite A |
| --- | --- | --- | --- |
| RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation | arXiv 2024, code available | 论文提出对 RAG retrieval 与 generation 模块做细粒度诊断，并声称与人工判断相关性优于其他指标。Source: https://arxiv.org/abs/2408.08067 | A 版增加 retrieval proxy diagnostics，不只看“是否检索到文本”，还看 query coverage、section alignment、top-k diversity。 |
| RAGCap-Bench: Benchmarking Capabilities of LLMs in Agentic Retrieval Augmented Generation Systems | arXiv 2025/2026 | 论文关注 agentic RAG 中间任务能力与错误类型，而不是只看 end-to-end answer。Source: https://arxiv.org/abs/2510.13910 | A 版把系统拆成 weakness extraction、evidence retrieval、verification、ranking 四个可独立评估环节。 |
| ReviewGrounder: Improving Review Substantiveness with Rubric-Guided, Tool-Integrated Agents | arXiv 2026 | 论文指出 LLM review 常见问题是 superficial/formulaic comments，并用 rubric-guided、tool-integrated grounding 改善 review substantiveness。Source: https://arxiv.org/abs/2604.14261 | A 版保持“先生成 weakness，再 evidence grounding，再排序”的两阶段架构；后续可把 category -> expected evidence section 视作轻量 rubric。 |
| FactReview: Evidence-Grounded Peer Review with Execution-Based Claim Verification | arXiv 2026 | 论文主张 LLM reviewer 应 audit empirical claims，而不是直接做 accept/reject decision。Source: https://arxiv.org/abs/2604.04074 | A 版弱化“自动判收拒”的表述，把分类实验写成 exploratory auxiliary signal；主贡献放在 evidence-grounded weakness audit。 |
| Stop Automating Peer Review Without Rigorous Evaluation | ICML 2026 Spotlight position paper | 论文指出 AI reviewer 可能出现 excessive agreement 与 paper laundering gameability，强调非严谨评估下不应自动化 peer review。Source: https://arxiv.org/abs/2605.03202 | A 版增加失败分析：generic weakness rate、unsupported support rate、ranking diversity；系统定位为 reviewer assistance。 |
| MMReview: A Multidisciplinary and Multimodal Benchmark for LLM-Based Peer Review Automation | arXiv 2025, work in progress | 论文提出 240 篇、17 个领域、多模态、13 个任务的 benchmark。Source: https://arxiv.org/abs/2508.14146 | A 版暂不扩展多模态，但在论文局限性中说明当前只处理文本 Markdown，图表证据需要后续多模态扩展。 |
| DeepReview: Improving LLM-based Paper Review with Human-like Deep Thinking Process | ACL 2025 | 论文构建 DeepReview-13K，并强调结构化中间 review reasoning、novelty assessment、reliability verification。Source: https://aclanthology.org/2025.acl-long.1420.pdf | A 版可借鉴“结构化中间过程”，但不复现其训练；当前以真实 OpenReview 样本和小规模 weakness-evidence gold set 做轻量可解释实验。 |

## 本轮架构调整

1. 检索实验从单一 BM25 baseline 扩展为四组：
   - BM25
   - TF-IDF cosine
   - BM25 + TF-IDF Hybrid
   - Section-aware Hybrid
2. 在人工 gold label 完成前，先增加 proxy diagnostics：
   - non-empty rate
   - average top-k score
   - category-section alignment
   - top-k section diversity
   - top-1 reference-section rate
3. 论文表述上避免“自动替代评审”，改为“证据审计与评审辅助”。

## 下一步实验

实现并运行：

```bash
python3 code/experiments/evireview_a/src/retrieve_tfidf.py
python3 code/experiments/evireview_a/src/retrieve_hybrid_section.py
python3 code/experiments/evireview_a/src/evaluate_retrieval_proxy.py
```

验收标准：

1. 三个脚本能从现有 `human_weaknesses.jsonl` 和 `evidence_blocks.jsonl` 复现生成结果。
2. 输出 BM25、TF-IDF、Hybrid、Section-aware Hybrid 的对比表。
3. 不引入新依赖。
4. 结果和代码提交并推送到远端仓库。

