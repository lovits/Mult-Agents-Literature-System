### [2026-05-30] SoundnessBench: Can Your AI Scientist Really Tell Good Research Ideas from Bad Ones?
- **Authors**: Sy-Tuyen Ho, Minghui Liu, Huy Nghiem, Furong Huang
- **Link**: https://arxiv.org/abs/2605.30329
- **Summary**: Introduces a 1,099-item benchmark for proposal-stage methodological soundness using ICLR-derived research proposals and reviewer soundness sub-scores. Relevance: supports adding a separate soundness/verifier layer to EviReview-Lite instead of treating accept/reject prediction as the primary target.

### [2026-05-30] PRISM: A Multi-Dimensional Benchmark for Evaluating LLM Peer Reviewers
- **Authors**: Ngoc Phan Phuoc Loc, Toan Huynh La Viet, Thanh Tran Khanh, Duy A Nguyen, Tuan Anh Nguyen Pham, Thanh Nguyen, Nitesh V. Chawla, Wray Buntine, Kok-Seng Wong, Khoa D. Doan, Binh T. Nguyen
- **Link**: https://arxiv.org/abs/2605.26730
- **Summary**: Proposes a multi-dimensional benchmark for LLM peer reviewers covering depth, novelty, flaw identification, prioritization, and constructiveness, with argument mining and retrieval-augmented verification. Relevance: aligns EviReview-Lite with modular evaluation rather than a single review-quality score.

### [2026-05-30] LLM-as-a-Reviewer: Benchmarking Their Ability, Divergence, and Prompt Injection Resistance as Paper Reviewers
- **Authors**: Lingyao Li, Junjie Xiong, Changjia Zhu, Runlong Yu, Chen Chen, Junyu Wang, Renkai Ma, Zhicong Lu
- **Link**: https://arxiv.org/abs/2605.25415
- **Summary**: Benchmarks LLM peer reviewers on 898 NeurIPS/ICLR papers across rating calibration, divergence from human reviewers, and prompt-injection resistance. Relevance: motivates adding robustness and source-grounding checks before trusting generated review comments.

### [2026-05-30] CLAIMCHECK: How Grounded are LLM Critiques of Scientific Papers?
- **Authors**: Jiefu Ou, William Gantt Walden, Kate Sanders, Zhengping Jiang, Kaiser Sun, Jeffrey Cheng, William Jurayj, and collaborators
- **Link**: https://arxiv.org/abs/2503.21717
- **Summary**: Introduces a claim-centric benchmark for evaluating whether paper critiques are grounded in scientific claims, including weakness-to-claim association and grounded verification tasks. Relevance: this is the closest external benchmark for the current EviReview-Lite verifier and retrieval experiments.

### [2026-05-30] Automatic Analysis of Substantiation in Scientific Peer Reviews
- **Authors**: Yanzhu Guo, Guokan Shang, Virgile Rennard, Michalis Vazirgiannis, Chloé Clavel
- **Link**: https://aclanthology.org/2023.findings-emnlp.684/
- **Summary**: Defines peer-review substantiation as claim-evidence support and releases SubstanReview, a domain-expert annotated dataset of 550 peer reviews. Relevance: provides the supervised floor for evaluating substantiation before building the full paper-grounded verifier.

### [2026-05-30] Evaluating Judges as Evaluators: The JETTS Benchmark of LLM-as-Judges as Test-Time Scaling Evaluators
- **Authors**: Yilun Zhou, Austin Xu, Peifeng Wang, Caiming Xiong, Shafiq Joty
- **Link**: https://proceedings.mlr.press/v267/zhou25af.html
- **Summary**: Evaluates judge models in reranking, step-level search, and critique-based refinement settings. Relevance: supports treating OpenRouter chat reranking as an optional verifier/reranker experiment with explicit judge reliability caveats, not as an unquestioned ground truth.

### [2026-05-31] NLPeer: A Unified Resource for the Computational Study of Peer Review
- **Authors**: Nils Dycke, Ilia Kuznetsov, Iryna Gurevych
- **Link**: https://arxiv.org/abs/2211.06651
- **Summary**: Introduces a multidomain peer-review corpus with more than 5k papers and 11k review reports, structured metadata, versioning, and reviewing-assistance tasks. Relevance: strong B-version generalization dataset after the A-version verifier/ranker pipeline is stable.

### [2026-05-31] A Dataset of Peer Reviews (PeerRead): Collection, Insights and NLP Applications
- **Authors**: Dongyeop Kang, Waleed Ammar, Bhavana Dalvi, Madeleine van Zuylen, Sebastian Kohlmeier, Eduard Hovy, Roy Schwartz
- **Link**: https://arxiv.org/abs/1804.09635
- **Summary**: Provides over 14k paper drafts with accept/reject decisions and over 10k expert peer reviews for a subset of papers. Relevance: suitable auxiliary dataset for accept/reject and review-score baselines, but not the main evidence-grounded verifier benchmark.

### [2026-05-31] OpenReview Raw Dataset
- **Authors**: Prior Computers dataset compilation
- **Link**: https://huggingface.co/datasets/priorcomputers/openreview_raw
- **Summary**: Hugging Face dataset card reports OpenReview-derived peer-review data across major ML/AI venues, with paper metadata, note types, review text, venues, years, and OpenReview URLs. Relevance: useful expansion source for later scaling, but A-version should continue using curated local samples and licensed/annotated verifier datasets.

### [2026-05-31] ReviewGrounder: Improving Review Substantiveness with Rubric-Guided, Tool-Integrated Agents
- **Authors**: Zhuofeng Li, Yi Lu, Dongfu Jiang, Haoxiang Zhang, Yuyang Bai, Chuan Li, Yu Wang, Shuiwang Ji, Jianwen Xie, Yu Zhang
- **Link**: https://arxiv.org/abs/2604.14261
- **Summary**: Proposes rubric-guided, tool-integrated review agents to improve review substantiveness and reduce superficial comments. Relevance: supports the current deterministic rubric-agent baseline as a cheap, inspectable lower bound before OpenRouter LLM reviewer experiments.

### [2026-05-31] FactReview: Evidence-Grounded Peer Review with Execution-Based Claim Verification
- **Authors**: Ling Yue, Chaoqian Ouyang, Hang Xu, Ruijun Huang, Yuchen Liu, Libin Zheng, Wei Liu, Shaowu Pan, Shimin Di, Min-Ling Zhang
- **Link**: https://arxiv.org/abs/2604.04074
- **Summary**: Frames scientific peer review around evidence-grounded claim auditing rather than direct verdict generation. Relevance: reinforces EviReview-Lite's decomposition into weakness generation, Paper-RAG retrieval, evidence verification, ranker, and only auxiliary accept/reject classification.

### [2026-05-31] DeepReview: Improving LLM-based Paper Review with Human-like Deep Thinking Process
- **Authors**: WestlakeNLP and collaborators
- **Link**: https://aclanthology.org/2025.acl-long.1420/
- **Summary**: Builds a structured LLM-based paper review process with intermediate reasoning and review-quality objectives. Relevance: useful related work for structured reviewer generation, but current A-version should keep generation small and focus evaluation on grounded weakness coverage.

### [2026-05-31] Physics Is All You Need? A Case Study in Physicist-Supervised AI Development of Scientific Software
- **Authors**: Nhat-Minh Nguyen
- **Link**: https://arxiv.org/abs/2605.30353
- **Summary**: Presents a scientist-supervised AI-agent software development case study and reports that standard oracle tests can miss domain-specific scientific errors. Relevance: supports keeping EviReview-Lite under evidence retrieval, verifier diagnostics, and human gold-label supervision instead of trusting reviewer-agent output directly.

### [2026-05-31] RAGCap-Bench: Benchmarking Capabilities of LLMs in Agentic Retrieval Augmented Generation Systems
- **Authors**: Jingru Lin, Chen Zhang, Stephen Y. Liu, Haizhou Li
- **Link**: https://arxiv.org/abs/2510.13910
- **Summary**: Proposes a capability-oriented benchmark for intermediate tasks in agentic RAG workflows and analyzes typical error categories. Relevance: supports evaluating EviReview-Lite by module-level capabilities such as query/weakness planning, evidence retrieval, verifier judgment, and ranking rather than only final review text.

### [2026-05-31] InfoDeepSeek: Benchmarking Agentic Information Seeking for Retrieval-Augmented Generation
- **Authors**: Yunjia Xi, Jianghao Lin, Menghui Zhu, Yongzhao Xiao, Zhuoying Ou, Jiaqi Liu, Tong Wan, Bo Chen, Weiwen Liu, Yasheng Wang, Ruiming Tang, Weinan Zhang, Yong Yu
- **Link**: https://arxiv.org/abs/2505.15872
- **Summary**: Introduces a benchmark and evaluation framework for dynamic agentic information seeking with fine-grained metrics for accuracy, utility, and compactness. Relevance: supports adding compactness and evidence-use efficiency diagnostics to EviReview-Lite's Paper-RAG workflow.

### [2026-05-31] RAGCHECKER: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation
- **Authors**: Dongyu Ru, Lin Qiu, Xiangkun Hu, Tianhang Zhang, Peng Shi, Shuaichen Chang, Cheng Jiayang, Cunxiang Wang, Shichao Sun, Huanyu Li, Zizhao Zhang, Binjie Wang, Jiarong Jiang, Tong He, Zhiguo Wang, Pengfei Liu, Yue Zhang, Zheng Zhang
- **Link**: https://arxiv.org/abs/2408.08067
- **Summary**: Presents fine-grained RAG diagnostics for retrieval and generation, using claim-level entailment checks and meta-evaluation against human judgments. Relevance: supports the current claim/weakness-level verifier design and argues for separating retrieval quality from generation faithfulness.

### [2026-05-31] SoK: Agentic Retrieval-Augmented Generation (RAG): Taxonomy, Architectures, Evaluation, and Research Directions
- **Authors**: Saroj Mishra, Suman Niroula, Umesh Yadav, Dilip Thakur, Srijan Gyawali, Shiva Gaire
- **Link**: https://arxiv.org/abs/2603.07379
- **Summary**: Systematizes Agentic RAG as sequential decision-making with planning, retrieval orchestration, memory, and tool-use components, and highlights reliability risks such as compounding hallucination and retrieval misalignment. Relevance: supports writing EviReview-Lite as a stateful reviewer-agent workflow with explicit oversight and trajectory diagnostics.

### [2026-05-31] A-RAG: Scaling Agentic Retrieval-Augmented Generation via Hierarchical Retrieval Interfaces
- **Authors**: Mingxuan Du, Benfeng Xu, Chiwei Zhu, Shaohan Wang, Pengyu Wang, Xiaorui Wang, Zhendong Mao
- **Link**: https://arxiv.org/abs/2602.03442
- **Summary**: Proposes hierarchical retrieval interfaces, including keyword search, semantic search, and chunk read, so an agent can adaptively choose retrieval granularity. Relevance: motivates upgrading EviReview-Lite from section-aware reranking toward explicit Paper-RAG tools for reviewer agents.

### [2026-05-31] Beyond Correctness: Rewarding Faithful Reasoning in Retrieval-Augmented Generation
- **Authors**: Zhichao Xu, Zongyu Wu, Yun Zhou, Aosong Feng, Kang Zhou, Sangmin Woo, Kiran Ramnath, Yijun Tian, Xuan Qi, Weikang Qiu, Lin Lee Cheong, Haibo Ding
- **Link**: https://arxiv.org/abs/2510.13272
- **Summary**: Introduces faithfulness metrics for RL-based search agents and VERITAS, a reward framework for intermediate traceability in agentic search. Relevance: supports treating EviReview-Lite's weakness-evidence-verifier trace as a primary evaluation artifact, not just final review correctness.

### [2026-05-31] Retrieval Augmented Generation (RAG) for Fintech: Agentic Design and Evaluation
- **Authors**: Thomas Cook, Richard Osuagwu, Liman Tsatiashvili, Vrynsia Vrynsia, Koustav Ghosal, Maraim Masoud, Riccardo Mattivi
- **Link**: https://arxiv.org/abs/2510.25518
- **Summary**: Designs a modular agentic RAG pipeline for a domain with dense terminology, using query reformulation, sub-query decomposition, acronym resolution, and cross-encoder reranking. Relevance: supports using domain-specific retrieval orchestration in EviReview-Lite, while noting that quality gains may trade off against latency.

### [2026-05-31] AgenticRAG: Agentic Retrieval for Enterprise Knowledge Bases
- **Authors**: Susheel Suresh, Hazel Mak, Shangpo Chou, Fred Kroon, Sahil Bhatnagar
- **Link**: https://arxiv.org/abs/2605.05538
- **Summary**: Presents a lightweight agentic retrieval harness over enterprise knowledge bases with search, find, open, and summarize tools. Its ablations report that moving from single-shot retrieval to agentic tool use is the largest quality driver. Relevance: reinforces the current EviReview-Lite upgrade from one-pass section-aware retrieval toward auditable Paper-RAG tools and in-document navigation.

### [2026-05-31] Patho-AgenticRAG: Towards Multimodal Agentic Retrieval-Augmented Generation for Pathology VLMs via Reinforcement Learning
- **Authors**: Wenchuan Zhang, Jingru Guo, Hengzhe Zhang, Penghao Zhang, Jie Chen, Shuwan Zhang, Zhang Zhang, Yuhao Yi, Hong Bu
- **Link**: https://arxiv.org/abs/2508.02258
- **Summary**: Applies multimodal agentic retrieval to pathology VLMs, combining text-image retrieval, task decomposition, and multi-turn search to reduce hallucination in a high-stakes evidence-grounded domain. Relevance: useful as related work showing agentic RAG's broader grounding motivation, but not an A-version dependency because EviReview-Lite is text-only paper-review retrieval.
