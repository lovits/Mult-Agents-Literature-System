# E6 End-to-End Structured Review Report

## Protocol

- Accept/reject decision: disabled
- arXiv unseen Gold metrics: disabled
- Component outputs: E2, E3, E4, E5

## Dataset

- OpenReview papers: 10
- OpenReview official reviews: 41
- arXiv unseen demo papers: 5

## System Metrics

| System | Paper Report Coverage | Trace Coverage | Top-K Compliance | Accept/Reject Decisions | Review Leakage Free | Official Weakness Proxy Overlap@K |
|---|---:|---:|---:|---:|---:|---:|
| B0_unstructured_review_dump | 1.0000 | 0.0000 | 0.0000 | 0 | n/a | 0.0000 |
| B1_structured_evidence_report | 1.0000 | 1.0000 | 1.0000 | 0 | n/a | 0.0000 |
| B2_system_generated_structured_report | 1.0000 | 1.0000 | 1.0000 | 0 | True | 0.0531 |
| B3_cue_aware_structured_report | 1.0000 | 1.0000 | 1.0000 | 0 | True | 0.0610 |

## Sample OpenReview Reports

### PwxYoMvmvy: Beyond Random Masking: When Dropout meets Graph Convolutional Networks

- `PwxYoMvmvy:Pvt0OjNSp2:0` score=1.4800, evidence=PwxYoMvmvy:Pvt0OjNSp2:weaknesses: The authors provide generalization bounds for graph neural networks with dropout. However, further clarification is needed on how this finding offers insights into understanding and designing graph neural networks, or any specific guidance on selecting dropout rates. With this theory, is it possible to get the best dropout rate with a specific graph structure and GNN? This would help demonstrate the practical relevance of the theory. Additionally, can the experiments provide corresponding analyses regarding this theory? For example, whether the change in performance at different dropout rates is consistent with the change in generalization bounds can be analyzed from the theory.
- `PwxYoMvmvy:wumckDPIQ3:2` score=1.4800, evidence=PwxYoMvmvy:wumckDPIQ3:weaknesses: The major concern is with the conclusions drawn from the experiments. It is already established in deep learning that dropout and batch normalization enhance performance through regularization. Therefore, only comparing the performance in Tables 1, 2, and 3 does not provide sufficient evidence that the observed improvements are specifically due to the additional effects of dropout in graph neural networks, as analyzed in the theorems. The authors need to design experiments that can directly validate their theoretical analysis.
- `PwxYoMvmvy:Pvt0OjNSp2:1` score=1.0200, evidence=PwxYoMvmvy:Pvt0OjNSp2:weaknesses: The use of dropout or similar strategies designed specifically for graphs is also widely applied in GNNs, like DropNode, DropEdge, DropMeassge, etc [1, 2, 3]. The authors may need to discuss its relevance to this study, including whether the proposed theory can analyze these methods and the essential difference and connection between dropout and these methods. Compared to traditional dropout, does dropout on the graph structure more directly enhance the performance of graph neural networks?

### ONfWFluZBI: Self-supervised contrastive learning performs non-linear system identification

- `ONfWFluZBI:ap4NehPA7i:2` score=2.3200, evidence=ONfWFluZBI:ap4NehPA7i:weaknesses: Regarding the polish of the paper, there are various typos and lacking definitions that make the paper hard to parse at times. The minor ones that I have caught are listed below. A particularly confusing point is the role of the control input $u_t$. The paper presents the control input as entering the latent dynamics directly. However, it is typically the case that the control input enters the state through a (possibly state-dependent) actuation matrix $\mathbf B(x_t) u_t$. In any case, how the control input enters the dynamics should be dependent on the parameterization of the dynamics, e.g. the affine ambiguity in $\mathbf L$ in the paper, which is not reflected in the authors' method as far as I can tell. Furthermore, it is unclear if the control input is available to the learner (which is usually the case in sysID), or if it is playing the role of stochastic noise, which eq (9) seems to suggest compared to eq (1). In either case, what role is the control input playing here: in the authors' set-up, there is no need to learn the actuation matrix, and the experiments involve learning a low-noise, nearly deterministic Lorenz system, which rules out some persistency of excitation effect (Tsiamis and Pappas, 2019).
- `ONfWFluZBI:ap4NehPA7i:1` score=1.1200, evidence=ONfWFluZBI:ap4NehPA7i:weaknesses: The paper claims to perform latent nonlinear system identification. This is a key desideratum in various fields such as reinforcement learning and continuous control, and thus has a rich history and literature. However, the assumptions in this paper--and notably how these inductive biases propagate to the algorithm design--severely restrict the applicability of the method without further evidence. Notably, a design assumption in this paper is that the observer function (i.e."mixing function") is invertible. This is a very strong assumption in the context of *non-linear system identification*, where even the foundational theory of linear system identification does not presume: in the Linear-Quadratic Gaussian (LQG) model, where the underlying state evolves linearly $x_{t+1} = Ax_t + Bu_t + w_t$, and observations are a linear function of state $y_t = Cx_t + v_t$ (ignoring the control input term for simplicity), the classical set-up has $d_y < d_x$, such that the observations are per-timestep a low-dimensional measurement of the underlying state. This immediately rules out the mixing function $g(x) = Cx$ being invertible, and this is precisely the motivation for notions such as observability/detectability. Partial observability presents the key challenge in non-linear sysID or reinforcement learning. In particular, it is well-known in controls and RL that ignoring partial observability and imposing a Markovian model (which this paper does implicitly by enforcing the state estimate as a function solely of the current observation) can lead to very undesirable outcomes. In the contrastive learning literature, partial observability is usually not a central issue, often because it is irrelevant for the motivating application (e.g. in computer vision), but one must address this problem for time-series data. In fact, the cited Time-Contrastive Learning method (Hyvarinen and Tomioka, 2016), despite making the same assumption in theory, actually propose a method that is more amenable to partial observability, since they predict categorical labels to *chunks* of observed data.
- `ONfWFluZBI:9ujmKw351K:3` score=0.9800, evidence=ONfWFluZBI:9ujmKw351K:weaknesses: If the above is too challenging to achieve, you should at least try to discuss more in detail what each of you theoretical assumptions means in practice, and what you expect to happen if they are not met in real-world experiments. For example, the fact that $p(u_t)$ is a normal distribution seems quite strict in many applications.

### odjMSBSWRt: DarkBench: Benchmarking Dark Patterns in Large Language Models

- `odjMSBSWRt:MtBx6vnXOc:8` score=1.3000, evidence=odjMSBSWRt:MtBx6vnXOc:weaknesses: This is largely analogous to W2. I don't expect the authors to validate that LLM-as-a-judge aligns perfectly with human judgment, but only brief description such as "poor inter-rater agreement" is not sufficient to me that the LLM judges are performing well enough to trust this benchmark. It is also unclear to me how the different model judges (e.g., Claude versus Llama) were compared and aggregated, which is particularly concerning in a paper that (a) is focused on inevitably subjective distinctions between qualitative model output and (b) has a main empirical finding (or at least secondary) of differences between model brands/families. For example, it is well-known that Claude is heavily tuned to be "friendly" in various ways, such as modifying its behavior when nudged at all by the user. Some people like this. Some prefer ChatGPT as straightforward with less of that noise. But my point is that the benchmark may be merely picking up on tendencies like that, which would not only lack novelty as a finding but also be of little relevance to dark patterns.
- `odjMSBSWRt:WHyOKuCKRF:2` score=0.7800, evidence=odjMSBSWRt:WHyOKuCKRF:weaknesses: There is no evidence of stability for the benchmark findings across variations in prompt designs. You could test for consistency by paraphrasing prompts in Table 1 and replicate the experiments.
- `odjMSBSWRt:WHyOKuCKRF:1` score=0.7520, evidence=odjMSBSWRt:WHyOKuCKRF:weaknesses: The paper lacks detailed information on human annotations, particularly regarding the annotators' demographics or level of expertise. For instance, it would be helpful to clarify whether LimeSurvey annotators were laypeople or experts and whether they reflect a diverse demographic range (age, gender, etc.) similar to typical LLM users.


## Sample System-Generated Reports

### PwxYoMvmvy: Beyond Random Masking: When Dropout meets Graph Convolutional Networks

- Candidate source: `system_deterministic_baseline_v1`

- `PwxYoMvmvy:system:0` aspect=experiment, score=0.4500, evidence=PwxYoMvmvy:content:title, PwxYoMvmvy:content:abstract, PwxYoMvmvy:content:keywords, PwxYoMvmvy:content:primary_area: The empirical evaluation may need stronger ablation analysis to isolate which component drives the reported gains.
- `PwxYoMvmvy:system:1` aspect=missing_baseline, score=0.4500, evidence=PwxYoMvmvy:content:title, PwxYoMvmvy:content:abstract, PwxYoMvmvy:content:keywords, PwxYoMvmvy:content:primary_area: The baseline comparison may be incomplete or insufficiently justified for the claimed contribution.
- `PwxYoMvmvy:system:2` aspect=reproducibility, score=0.4500, evidence=PwxYoMvmvy:content:title, PwxYoMvmvy:content:abstract, PwxYoMvmvy:content:keywords, PwxYoMvmvy:content:primary_area: The implementation and reproduction details may not be specific enough for independent verification.

### ONfWFluZBI: Self-supervised contrastive learning performs non-linear system identification

- Candidate source: `system_deterministic_baseline_v1`

- `ONfWFluZBI:system:0` aspect=experiment, score=0.4500, evidence=ONfWFluZBI:content:title, ONfWFluZBI:content:abstract, ONfWFluZBI:content:keywords, ONfWFluZBI:content:primary_area: The empirical evaluation may need stronger ablation analysis to isolate which component drives the reported gains.
- `ONfWFluZBI:system:1` aspect=missing_baseline, score=0.4500, evidence=ONfWFluZBI:content:title, ONfWFluZBI:content:abstract, ONfWFluZBI:content:keywords, ONfWFluZBI:content:primary_area: The baseline comparison may be incomplete or insufficiently justified for the claimed contribution.
- `ONfWFluZBI:system:2` aspect=reproducibility, score=0.4500, evidence=ONfWFluZBI:content:title, ONfWFluZBI:content:abstract, ONfWFluZBI:content:keywords, ONfWFluZBI:content:primary_area: The implementation and reproduction details may not be specific enough for independent verification.

### odjMSBSWRt: DarkBench: Benchmarking Dark Patterns in Large Language Models

- Candidate source: `system_deterministic_baseline_v1`

- `odjMSBSWRt:system:0` aspect=experiment, score=0.4500, evidence=odjMSBSWRt:content:title, odjMSBSWRt:content:abstract, odjMSBSWRt:content:keywords, odjMSBSWRt:content:primary_area: The empirical evaluation may need stronger ablation analysis to isolate which component drives the reported gains.
- `odjMSBSWRt:system:1` aspect=missing_baseline, score=0.4500, evidence=odjMSBSWRt:content:title, odjMSBSWRt:content:abstract, odjMSBSWRt:content:keywords, odjMSBSWRt:content:primary_area: The baseline comparison may be incomplete or insufficiently justified for the claimed contribution.
- `odjMSBSWRt:system:2` aspect=reproducibility, score=0.4500, evidence=odjMSBSWRt:content:title, odjMSBSWRt:content:abstract, odjMSBSWRt:content:keywords, odjMSBSWRt:content:primary_area: The implementation and reproduction details may not be specific enough for independent verification.


## Sample Cue-Aware System Reports

### PwxYoMvmvy: Beyond Random Masking: When Dropout meets Graph Convolutional Networks

- Candidate source: `system_cue_aware_baseline_v2`

- `PwxYoMvmvy:cue:5` aspect=novelty, score=0.9000, evidence=PwxYoMvmvy:content:title, PwxYoMvmvy:content:abstract, PwxYoMvmvy:content:keywords, PwxYoMvmvy:content:primary_area: The novelty claim may need clearer positioning against existing work in the same problem setting.
- `PwxYoMvmvy:cue:0` aspect=experiment, score=0.7700, evidence=PwxYoMvmvy:content:title, PwxYoMvmvy:content:abstract, PwxYoMvmvy:content:keywords, PwxYoMvmvy:content:primary_area: The empirical evaluation may need stronger ablation analysis and direct validation of the claimed mechanism.
- `PwxYoMvmvy:cue:1` aspect=missing_baseline, score=0.7700, evidence=PwxYoMvmvy:content:title, PwxYoMvmvy:content:abstract, PwxYoMvmvy:content:keywords, PwxYoMvmvy:content:primary_area: The baseline comparison may be incomplete, especially against closely related recent or task-specific methods.

### ONfWFluZBI: Self-supervised contrastive learning performs non-linear system identification

- Candidate source: `system_cue_aware_baseline_v2`

- `ONfWFluZBI:cue:21` aspect=method, score=1.2300, evidence=ONfWFluZBI:content:title, ONfWFluZBI:content:abstract, ONfWFluZBI:content:keywords, ONfWFluZBI:content:primary_area: The method may depend on strong observability, control-input, or system-identification assumptions.
- `ONfWFluZBI:cue:4` aspect=related_work, score=0.6200, evidence=ONfWFluZBI:content:title, ONfWFluZBI:content:abstract, ONfWFluZBI:content:keywords, ONfWFluZBI:content:primary_area: The related work comparison may need a sharper discussion of overlapping prior approaches.
- `ONfWFluZBI:cue:5` aspect=novelty, score=0.4600, evidence=ONfWFluZBI:content:title, ONfWFluZBI:content:abstract, ONfWFluZBI:content:keywords, ONfWFluZBI:content:primary_area: The novelty claim may need clearer positioning against existing work in the same problem setting.

### odjMSBSWRt: DarkBench: Benchmarking Dark Patterns in Large Language Models

- Candidate source: `system_cue_aware_baseline_v2`

- `odjMSBSWRt:cue:0` aspect=experiment, score=0.6100, evidence=odjMSBSWRt:content:title, odjMSBSWRt:content:abstract, odjMSBSWRt:content:keywords, odjMSBSWRt:content:primary_area: The empirical evaluation may need stronger ablation analysis and direct validation of the claimed mechanism.
- `odjMSBSWRt:cue:1` aspect=missing_baseline, score=0.6100, evidence=odjMSBSWRt:content:title, odjMSBSWRt:content:abstract, odjMSBSWRt:content:keywords, odjMSBSWRt:content:primary_area: The baseline comparison may be incomplete, especially against closely related recent or task-specific methods.
- `odjMSBSWRt:cue:5` aspect=novelty, score=0.5000, evidence=odjMSBSWRt:content:title, odjMSBSWRt:content:abstract, odjMSBSWRt:content:keywords, odjMSBSWRt:content:primary_area: The novelty claim may need clearer positioning against existing work in the same problem setting.

## arXiv Unseen Demo Boundary

- Papers: 5
- Gold metrics reported: False

The unseen set is used only to verify that the pipeline can carry new-paper metadata and PDF paths into a report-ready manifest.
