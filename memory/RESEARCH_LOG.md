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
