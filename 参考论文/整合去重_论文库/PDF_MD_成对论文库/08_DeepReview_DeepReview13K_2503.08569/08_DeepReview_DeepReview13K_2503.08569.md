---
source: MinerU existing
pdf: 08_DeepReview_DeepReview13K_2503.08569.pdf
original_markdown: 开题用论文_08_DeepReview_DeepReview13K_MinerU_md_08_DeepReview_DeepReview13K.md
---

# 1 Introduction

Peer review is the foundation of scientific progress, ensuring that research is novel, reliable, and rigorously evaluated by experts before publication [Alberts et al., 2008]. With the increasing volume of research submissions, Large Language Models (LLMs) have become promising tools to support reviewers [Yang et al., 2024, Chris et al., 2024, Li et al., 2024b, Scherbakov et al., 2024, Si et al., 2025]. For example, the ICLR 2025 conference has introduced an LLM-based system to assist reviewers in providing feedback Blog [2024].

Recent research has explored two primary approaches to improve LLM-based review systems: (1) employing LLM-powered agents to simulate the peer review process, as exemplified by AI-Scientist [Chris et al., 2024] and AgentReview [Jin et al., 2024a]; and (2) developing open-source models trained on extensive datasets from existing peer review platforms, such as ReviewMT [Tan et al., 2024b] and CycleReviewer [Weng et al., 2025].

Despite these advancements, current systems exhibit several critical limitations: they struggle to comprehensively identify submission flaws, resulting in superficial feedback [Zhou et al., 2024a]; lack evidence-based justifications [Zhuang et al., 2025]; and fail to provide clear, actionable suggestions [Ye et al., 2024, Du et al., 2024]. Moreover, their vulnerability to prompt engineering leads to inaccurate evaluations [Ye et al., 2024]. While robust feedback is crucial for scientific advancement and peer review integrity, developing reliable evaluation frameworks faces two significant challenges: (1) The scarcity of structured paper review datasets that capture fine-grained expert evaluation processes. Most available open review datasets primarily contain aggregated reviews and decisions, limiting LLMs’ ability to learn systematic review reasoning chains and increasing their susceptibility to shortcut learning and adversarial manipulation. (2) LLMs’ inherent constraints, including restricted domain knowledge, lack of dynamic knowledge updating mechanisms, and a tendency to generate hallucinated content without adequate verification [Schintler et al., 2023, Drori and Te’eni, 2024], which significantly impair their capability to assess complex scientific content [Wang et al., 2020, Yuan et al., 2021].

To address these challenges, we introduce DeepReview, a structured multi-stage review framework that closely aligns with the expert review process by incorporating novelty assessment, multidimensional evaluation criteria, and reliability verification. We develop a comprehensive data synthesis pipeline that integrates retrieval and ranking[Asai et al., 2024], self-verification [Weng et al., 2023], and self-reflection [Ji et al., 2023], ensuring the soundness and robustness of LLM-generated suggestions. This approach enables deeper insights into the reasoning and decision-making of paper review. The resulting dataset, DeepReview-13K, consists of raw research papers, structured intermediate review steps, and final assessments. Based on that, we train DeepReviewer-14B, a model that offers three inference modes – Fast, Standard, and Best – allowing users to balance efficiency and response quality. We further construct DeepReview-Bench, a comprehensive benchmark containing 1.2K samples, which evaluates both quantitative aspects (rating prediction, quality ranking, and paper selection) and qualitative review generation through LLM-based assessment.

Extensive experiments demonstrate DeepReviewer 14B’s superior performance across multiple dimensions. Compared to existing systems like CycleReviewer-70B, GPT-o1, and Deepseek-R1, our model achieves substantial improvements in Score (Rating MSE: $4 4 . 8 0 \%$ ↑), Ranking (Rating Spearman: $6 . 0 4 \%$ ↑), and Selection (Accuracy $1 . 8 0 \%$ ↑). In LLM-as-a-judge evaluation [Wang et al., 2024b, Rewina et al., 2025], it achieves a $80 \%$ win rate against GPT-o1 and Deepseek-R1. Notably, DeepReviewer exhibits strong resilience to adversarial attacks despite no explicit robustness training. Furthermore, our Test-Time Scaling analysis reveals that DeepReviewer can enhance its performance by adjusting reasoning paths and response lengths.

Our work establishes a foundation for robust LLM-based review systems through DeepReview, a structured framework that addresses fundamental challenges in automated manuscript evaluation. We introduce DeepReview-13K, a dataset featuring fine-grained review reasoning chains, alongside DeepReview-Bench, a benchmark for automated paper review. Built upon these resources, our DeepReviewer-14B model demonstrates substantial improvements over existing approaches while maintaining strong resilience to adversarial attacks, validating the effectiveness of our structured approach to automated scientific evaluation. Our code, model, and data will be publicly available under the agreement of our usage policy.

![](images/244f90ede8cf59a516d632c3465fdec2ed9bca7a9bcc350a4aed4c5c309fbfc0.jpg)  
Figure 1: Overview of the DeepReviewer. (a) Input paper example with a real-world research paper. (b) Output example showing DeepReviewer’s multi-stage reasoning process: Novelty Verification, Multi-dimension Review, and Reliability Verification. (c) Inference modes: fast, standard, and best, highlighting different reasoning paths. We provide a more detailed case study in the appendix D.

# 2 Related Work

Reasoning in LLMs. The emergence of large language models Achiam et al. [2023], Touvron et al. [2023], Bai et al. [2023] has provided new assistance in advancing solutions to complex Science challenges Hendrycks et al. [2021]. Initially, Scratchpads and chain-of-thought Akyürek et al. [2022], Nye et al. [2021], Wei et al. [2022] encouraged LLMs to think. This technique has been employed in various reasoning tasks. Building on this, a series of works including self-consistency Wang et al. [2023], self-verification Weng et al. [2023], and self-reflection Madaan et al. [2024] prompted language models to output more thinking processes during reasoning. Later, OpenAI’s O1 model Jaech et al. [2024] and various open-source long chain-of-thought models Guo et al. [2025] achieved Scaling Test-time Compute Yao et al. [2024], Guan et al. [2025] through additional supervised training or reinforcement learning, enabling language models to select optimal solutions for improved performance Xiang et al. [2025]. While these advances have enhanced reasoning capabilities, they primarily focus on general problem-solving rather than specialized academic review tasks. Our Review-with-Thinking framework extends these reasoning approaches specifically for peer review.

Reliable Scientific Literature Assessment. Recent studies have demonstrated significant progress in automated scientific research. [Chris et al., 2024] develop an AI scientist for autonomous hypothesis generation and experimentation [Langley, 1987, Daniil et al., 2023, AI, 2025, Zonglin et al., 2023, Li et al., 2024c, Hu et al., 2024]. Multi-agent frameworks [Ghafarollahi and Buehler, 2024, Rasal and Hauer, 2024, Su et al., 2024] enable collaborative scientific reasoning, while [Weng et al., 2025] show LLM-based review systems can enhance scientific discovery through reinforcement learning. However, these systems often lack structured reasoning, resulting in unreliable feedback.

Robust LLM-based Paper Review. Recent work spans generation-focused approaches using roleplaying agents [D’Arcy et al., 2024, Gao et al., 2024, Yu et al., 2024, Weng et al., 2025], meta-review synthesis [Santu et al., 2024, Li et al., 2023, Zeng et al., 2024], and bias detection mechanisms [Liang et al., 2024, Tyser et al., 2024, Tan et al., 2024a]. Hybrid workflows [Jin et al., 2024b, Zyska et al., 2023] combine human-AI collaboration with iterative refinement. While evaluation benchmarks [Funkquist et al., 2022, Zhou et al., 2024b, Kang et al., 2018] and ethical analyses [Ye et al., 2024, Latona et al., 2024] have advanced the field, existing systems struggle with complex assessments and remain vulnerable to adversarial attacks, highlighting the need for explicit reasoning processes.

# 3 Data Collection

We present DeepReview-13K, a training dataset that captures the intermediate reasoning processes inherent in academic paper reviews, addressing the fundamental challenges in Paper Review tasks from three dimensions: the scarcity of high-quality, structured review datasets and standardized evaluation frameworks.

# 3.1 DeepReview-13K

<table><tr><td>Dataset</td><td>Number</td><td>Tokens</td><td>Rating</td><td>Accept Rate</td></tr><tr><td>ICLR 2024 Train</td><td>4131</td><td>10439</td><td>5.34</td><td>37.8%</td></tr><tr><td>ICLR 2025 Train</td><td>9247</td><td>10062</td><td>5.13</td><td>31.2%</td></tr><tr><td>DeepReview-13K</td><td>13378</td><td>10178</td><td>5.18</td><td>33.24%</td></tr><tr><td>ICLR 2024 Test</td><td>652</td><td>10681</td><td>5.47</td><td>43.7%</td></tr><tr><td>ICLR 2025 Test</td><td>634</td><td>10241</td><td>5.18</td><td>31.1%</td></tr><tr><td>DeepReview-Bench</td><td>1286</td><td>10464</td><td>5.33</td><td>37.49%</td></tr></table>

Table 1: Dataset Statistics. The table shows the average values of Tokens, Rating, and Accept Rate

The statistics of this dataset are detailed in Table 1. We initially collected raw data from the OpenReview platform arXiv repository, gathering 18,976 paper submissions spanning two ICLR conference cycles ${ ( 2 0 2 4 - 2 0 2 5 ) } ^ { 2 }$ . Using the MinerU tool [Wang et al., 2024a], we convert papers to parseable Markdown format, prioritizing $\mathrm { I A T } \mathrm { E } ^ { \mathrm { X } }$ source code when available from arXiv. For each paper, we assembled a review set $\mathbf { R }$ comprising three key components: (1) textual assessments (Strengths, Weaknesses, and Questions), (2) interactive discussions from the rebuttal phase, and (3) standardized scores, including overall ratings $( \in [ 1 , 1 0 ] )$ and fine-grained evaluations of Soundness, Presentation, and Contribution $( \in [ 1 , 4 ] )$ . Additionally, we collect meta-review texts and final ratings with acceptance decisions. The final DeepReview-13K dataset comprises 13,378 valid samples in Table 1 as the foundation for constructing our review reasoning chain.

# 3.2 DeepReview-Test

To evaluate performance, we randomly sampled $10 \%$ (1.2K) of the dataset to create DeepReview-Bench. Our evaluation framework assesses both quantitative scores and qualitative aspects of review generation through the following tasks:

Quantitative Evaluation: 1) Rating prediction: using MAE, MSE, accuracy, and F1 metrics 2) Paper quality ranking: measured by Spearman correlation 3) Pairwise paper selection $( \mathrm { n } { = } 2 )$ : assessed through accuracy

Qualitative Evaluation: While previous work [Tan et al., 2024b] relied on simple text similarity metrics (e.g., ROUGE [Lin, 2004], BLEU [Papineni et al., 2002]), these metrics fail to capture specific review capabilities. Motivated by recent findings [Li et al., 2024a], we adopt the LLM-as-a-judge paradigm using Gemini-2.0-Flash-Thinking to conduct pairwise comparative evaluations of generated reviews. Detailed evaluation metrics are provided in Appendix B.

# 4 Methodology

Drawing inspiration from recent advances in complex reasoning methods [Xiang et al., 2025, Hao et al., 2024], we propose a deep-thinking evaluation framework that decomposes the review process into three key steps in Figure 1: (1) novelty verification $z _ { 1 }$ : assessing research originality through literature review; (2) multi-dimension evaluation $z _ { 2 }$ : synthesizing insights from multiple expert perspectives; and (3) reliability verification $z _ { 3 }$ : examining internal consistency and logical coherence.

# 4.1 Task Definition

Formally, given an input paper q, our goal is to generate a review pair $( \mathbf { s } , \mathbf { a } )$ , where s represents the qualitative assessment text (meta-review), we express the reasoning process as:

$$
{ \bf q }  z _ { 1 }  z _ { 2 }  z _ { 3 }  ( { \bf s } , { \bf a } )
$$

We formulate the review score generation as a marginalization over sequential reasoning chains:

$$
p ( \mathbf { a } | \mathbf { q } ) \propto \int p ( \mathbf { a } | z _ { 1 : 3 } , \mathbf { q } ) \prod _ { t = 1 } ^ { 3 } p ( z _ { t } | z _ { < t } , \mathbf { q } ) d \mathbf { Z }
$$

Here, the chain-of-thought term $\textstyle \prod _ { t = 1 } ^ { 3 } p ( z _ { t } | z _ { < t } , \mathbf { q } )$ explicitly models the sequential dependencies between reasoning steps, $\mathbf { Z }$ represents all possible intermediate state sequences $( s _ { 1 } , \ldots , s _ { n } )$ . This structured approach aims to enhance the reliability of the evaluation process.

# 4.2 Structured Reasoning Process

We present a comprehensive automated data construction pipeline, which is specifically designed to generate high-quality supervised fine-tuning datasets that capture complete reasoning paths, shown as $( z _ { 1 } , z _ { 2 } , z _ { 3 } )$ .

Stage 1: Novelty Verification $( z _ { 1 } )$ . Our novelty verification framework consists of three key components: question generation, paper analysis, and literature review. Initially, based on the paper, we use the Qwen-2.5-72B-Instruct model [Qwen et al., 2025] to generate three key research questions, focusing on research gaps, innovative directions, and methodological breakthroughs to capture domain-specific characteristics. Additionally, to ensure thorough understanding, we employ the Gemini-2.0-Flash-thinking model to conduct systematic paper analysis with a specifically designed system prompt (Figure 6) across research motivation, core ideas, technical approaches, and experimental design. Then, literature retrieval, comparison, and summary are built on OpenScholar Asai et al. [2024] to address these research questions. Using Qwen-2.5-3B-Instruct with few-shot learning, we transform questions into search keywords to retrieve approximately 60 relevant papers via Semantic Scholar API. Subsequently, the ReRank model3 reorder retrieved papers and select the top 10 most relevant papers, and its internal QA model 4 generates comprehensive reports as novelty analysis $z _ { 1 }$ , incorporating works cited in review $R$ .

Stage 2: Multi-dimension Review $\left( z _ { 2 } \right)$ . To provide constructive review, we transform author rebuttals into instructive suggestions while synthesizing multiple review $\mathbf { R }$ into comprehensive perspectives. Specifically, using Qwen-2.5-72B-Instruct, we develop a review reconstruction pipeline that analyzes each review in R with its corresponding author response, capturing experimental results, theoretical proofs, and implementation details from rebuttals to transform criticisms into concrete technical suggestions. The reconstruction process $( z _ { 2 } )$ follow three principles: (1) maintaining technical depth; (2) ensuring actionable feedback; (3) preserving professional tone and original citations.

Stage 3: Reliability Verification $\left( z _ { 3 } \right)$ . In order to ensure assessment accuracy through systematic evidence analysis, we employ Gemini-2-Flash-thinking to conduct systematic evidence analysis through a four-stage verification chain: methodology verification, experimental verification, and comprehensive analysis. Each review comment requires supporting evidence from the paper and receives an assigned confidence level. Finally, we utilize Qwen to generate a new Meta-Review by integrating the original Meta-Review, reviewer comments, and verification outcomes. This step identifies key weaknesses while providing evidence-based analysis and constructive suggestions.

Quality Control Mechanism. To ensure the high quality of our synthetic DeepReview-13K dataset, we implemented a rigorous automated quality control process using Qwen-2.5-72B-Instruct. This process involves a multi-faceted approach to assess each generated sample for logical integrity and completeness. Specifically, Qwen-2.5-72B-Instruct was tasked with examining each sample for: (1) Logical Consistency: verifying that the reasoning chain $( z _ { 1 } , z _ { 2 } , z _ { 3 } )$ and the final evaluation $( \mathbf { s } , \mathbf { a } )$

Table 2: Performance comparison of reviewer models on DeepReview-13k datasets. Notes: Metrics are grouped into Score (Rating MSE, Rating MAE, Decision Accuracy, Decision F1), Ranking (Rating Spearman), and Selection (Pairwise Rating Accuracy). Abbreviations: R.=Rating, MSE=Mean Squared Error, MAE=Mean Absolute Error, D. Acc.=Decision Accuracy, D. $\mathrm { F } 1 =$ Decision F1 score, Pair. R. Acc. $\equiv$ Pairwise Rating Accuracy.   

<table><tr><td rowspan="3">Method</td><td rowspan="3">Model</td><td colspan="6">ICLR 2024</td><td colspan="6">ICLR 2025</td></tr><tr><td colspan="4">Score</td><td colspan="2">Selection</td><td colspan="4">Score</td><td colspan="2">Ranking</td></tr><tr><td>R. MSE↓</td><td>R. MAE↓</td><td>D. Acc.↑</td><td>D.F1↑</td><td>Ranking R. Spearman ↑</td><td>Pair. R. Acc↑</td><td>R. MSE↓</td><td>R. MAE↓</td><td>D. Acc.↑</td><td>D.F1↑</td><td>R. Spearman ↑</td><td>Selection Pair. R. Acc↑</td></tr><tr><td rowspan="4">Agent Review</td><td>Claude-3-5-sonnet Gemni0-Flash-Thinking</td><td>2.8878</td><td>1.2715</td><td>0.4333</td><td>0.3937</td><td>0.1564</td><td>0.5526</td><td>2.8406</td><td>1.2989</td><td>0.2826</td><td>0.2541</td><td>-0.0219</td><td>0.5432</td></tr><tr><td></td><td>3.1943</td><td>1.3418</td><td>0.4400</td><td>0.4318</td><td>-0.0252</td><td>0.5044</td><td>26186</td><td>1.2170</td><td>0.4242</td><td>0.4242</td><td>0.0968</td><td>0.5496</td></tr><tr><td>DeepSeek-V3</td><td>1.9479</td><td>1.0735</td><td>04105</td><td>0.3403</td><td>0.3542</td><td>0.6096</td><td>1.9951</td><td>1.1017</td><td>0..3140</td><td>0.2506</td><td>0.1197</td><td>0.5702</td></tr><tr><td>GPT-01</td><td>4.3414</td><td>1.7294</td><td>0.4500</td><td>0.4424</td><td>0.2621</td><td>0.5881</td><td>4.3072</td><td>1.7917</td><td>0.4167</td><td>0.4157</td><td>0.2991</td><td>0.6318</td></tr><tr><td rowspan="5">AI Scientist</td><td>Claude-3-5-sonnet</td><td>3.4447</td><td>1.5037</td><td>0.4787</td><td>0.4513</td><td>0.0366</td><td>0.5305</td><td>3.0992</td><td>1.3500</td><td>0.5579</td><td>0.4440</td><td>-0.0219</td><td>0.5169</td></tr><tr><td>Gemini-2.0-Flash-Thinking</td><td>4.9297</td><td>18711</td><td>0.5743</td><td>00.5197</td><td>0745</td><td>0.5343</td><td>3.9232</td><td>1.6470</td><td>0.6139</td><td>0.4808</td><td>02565</td><td>0.6040</td></tr><tr><td>DeepSeek-V3</td><td>4.7337</td><td>1.7888</td><td>0.5600</td><td>0.5484</td><td>0.2310</td><td>0.5844</td><td>4.8006</td><td>1.8403</td><td>04059</td><td>0.3988</td><td>0078</td><td>0.5473</td></tr><tr><td>DeepSeek-R1</td><td>4.1648</td><td>1.6526</td><td>05248</td><td>0.988</td><td>0.3256</td><td>0.6206</td><td>4.7719</td><td>1.8099</td><td>0.4259</td><td>0.4161</td><td>0.3237</td><td>06289</td></tr><tr><td>8B</td><td>2.8911</td><td>1.2371</td><td>0.6353</td><td>0.5528</td><td>0.2801</td><td>0.5993</td><td>2.4461</td><td>1.2063</td><td>0.6780</td><td>0.5586</td><td>0.2786</td><td>0.5960</td></tr><tr><td rowspan="2">CycleReviewer</td><td>70B</td><td>2.4870</td><td>1.2514</td><td>06304</td><td>05696</td><td>0.3356</td><td>0.6160</td><td>2.4294</td><td>1.2128</td><td>0.6782</td><td>0.5737</td><td>0.2674</td><td>.5928</td></tr><tr><td>14B</td><td>1.3137</td><td>0.9102</td><td>0.6406</td><td>0.6307</td><td>0.3559</td><td>0.6242</td><td>1.3410</td><td>0.9243</td><td>0.6878</td><td>0.6227</td><td>0.4047</td><td>0.6402</td></tr></table>

are logically coherent and non-contradictory; (2) Completeness: checking for any missing or empty fields within the structured data format, ensuring all components of the reasoning path and evaluation are present. Samples failing any of these checks, indicating logical inconsistencies, incompleteness, or failing to meet our quality standards, were automatically flagged and removed from the dataset.

# 4.3 Model Training

We train our model based on Phi-4 14B [Abdin et al., 2024] using the DeepReview-13K dataset. The training process was conducted on 8x H100 80G GPUs with DeepSpeed $+ \mathrm { Z e R O 3 }$ [Rajbhandari et al., 2020, Rasley et al., 2020] for optimization. Notably, we extended the context window to 256K using LongRoPE [Ding et al., 2024], with a 40K context window during training for full-parameter fine-tuning. Given memory constraints, samples exceeding the preset context length are randomly truncated. The model is trained for 23,500 steps with a batch size of 16 and a learning rate of 5e-6.

Inference Strategy. We divided each sample in the DeepReview-13K data into three modes using reasoning path cropping, as shown in Figure 1(c), which allows for efficiency adjustments at test time based on varying requirements. The Fast mode directly generates final evaluation results and comprehensive analysis reports (s, a), minimizing computational cost by bypassing intermediate reasoning steps. The Standard mode executes core evaluation steps including $z _ { 2 }$ and $z _ { 3 }$ , maintaining high efficiency while ensuring evaluation quality, making it appropriate for routine research assessment. The Best mode implements the complete reasoning chain $( z _ { 1 } , z _ { 2 } , z _ { 3 } )$ , encompassing novelty verification, multi-dimension assessment, reliability verification, and comprehensive analysis generation. For novelty verification during inference, as in Stage 1 (Section 4.2), we employ Semantic Scholar API and OpenScholar to ensure accurate assessment of research novelty and citation correctness through comprehensive literature review and analysis. All three modes share the same model architecture, differing only in their executed evaluation steps. This allows the trained DeepReview-14B model to execute different reasoning paths at inference time, controlled by input instructions.

# 5 Experiments

# 5.1 Experimental setting

Baselines. We consider two types of baselines: (1) Prompt-based baselines including AI Scientist [Chris et al., 2024] and AgentReview [Jin et al., 2024a] implemented with various backbone models (GPT-o1-2024-12-17, Claude-3.5-sonnet-20241022, Gemini-2.0-Flash-Thinking-01-21, DeepSeek-V3, and DeepSeek-R1); (2) Fine-tuned baselines including CycleReviewer-8B and CycleReviewer-70B, both trained on ICLR 2024 review data. For inference, we use a temperature of 0.4 with maximum input and output lengths set to 100K and 16,384 tokens respectively to ensure complete text processing.

# 5.2 Main Results

Test results are shown in Table 2. Compared with prompt-based baselines, DeepReviewer reduces Rating MSE by an average of $6 5 . 8 3 \%$ and improves Decision Accuracy by an average of $1 5 . 2 \%$ points from AI Scientist. When compared to strong finetuned baseline CycleReviewer-70B, DeepReviewer represents reductions of $4 4 . 8 0 \%$ for Rating MSE. For the critical accept/reject decision task, DeepReviewer achieves $6 4 . 0 6 \%$ decision accuracy and 0.6307 F1 score on ICLR 2024, substantially surpassing all baselines. Notably, DeepReviewer with 14B parameters outperforms significantly larger models including CycleReviewer-70B (70B parameters) and other closed-source LLMs, demonstrating that DeepReviewer provides more reliable paper assessment than other approaches.

Table 3: Performance comparison of reviewer models on fine-grained evaluation dimensions. This table presents the performance across three key assessment aspects: Soundness (S.), Presentation (P.), and Contribution (C.) on ICLR 2024 and 2025 conferences.   

<table><tr><td></td><td></td><td colspan="6"></td><td colspan="3">Ranking</td><td colspan="3">Pairwise Accuracy</td></tr><tr><td>Method</td><td>Model</td><td>| S. MSE↓</td><td>S. MAE↓</td><td>P. MSE↓</td><td>P. MAE↓</td><td>C. MSE↓</td><td>C. MAE↓</td><td>S. Spearman†</td><td>P. Spearman↑</td><td>C. Spearman†</td><td>Pair. S. Acc↑</td><td>Pair. P. Acc↑</td><td>Pair. C. Acct</td></tr><tr><td colspan="10">ICLR 2024</td><td colspan="3"></td></tr><tr><td></td><td>GPT-01</td><td>0.4589</td><td>0.5336</td><td>0.5483</td><td>0.5983</td><td>0.7550</td><td>0.7147</td><td>0.1872</td><td>0.0723</td><td>0.1103</td><td>0.5797</td><td>0.5407</td><td>0.5621</td></tr><tr><td></td><td>Claude-3-5-sonnet</td><td>0.052</td><td>0.4388</td><td>0.745</td><td>0.504</td><td>1.1420</td><td>0.8876</td><td>0.1692</td><td>.0178</td><td>00275</td><td>0.6017</td><td>0.540</td><td>05726</td></tr><tr><td>AI Scientist</td><td>Gemini-2.0Flash-Thinking</td><td>0.72 33</td><td>0.224</td><td>0.55264</td><td>0.5797</td><td>0 9036</td><td>07480</td><td>0.1050</td><td>0.156</td><td>0.0274</td><td>0.5 5853</td><td>05929</td><td>0.5471</td></tr><tr><td></td><td>DeepSeek-V3</td><td>0.8810</td><td>.7718</td><td>0.762</td><td>0.7145</td><td>1.6936</td><td>1.1400</td><td>0 2258</td><td>03189</td><td>0.1574 0.3009</td><td>06028</td><td>0.6242</td><td>05933 0.6517</td></tr><tr><td></td><td>epSeek-R1</td><td>1.0540</td><td>0.8629</td><td>05356</td><td>0.5746</td><td>1.9564</td><td>1.2967</td><td>0.164</td><td>0.2927</td><td></td><td>.6091</td><td>0.6315</td><td></td></tr><tr><td>CycleReviewer</td><td></td><td>0.2516</td><td>0.3917</td><td>0.2356</td><td>0.3686</td><td>0.2507</td><td>0.3941</td><td>0.1990</td><td>0.3324</td><td>0.2593</td><td>0.5769</td><td>0.6103</td><td>0.5923</td></tr><tr><td>7B B</td><td></td><td>0.5 0.1578</td><td>0.3897 0.3029</td><td>0..2414 0.1896</td><td>0.3737 0.3291</td><td>.2657 0.2173</td><td>0.4052 0.3680</td><td>0.2320 0.3204</td><td>0.3373 0.3784</td><td>0.2354 0.3335</td><td>0.5829</td><td>06230</td><td>0 05896 0.6208</td></tr><tr><td colspan="10">DeepReviewer 14B</td><td colspan="3">0.6175 0.6353</td></tr><tr><td>ICLR 2025</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td colspan="10"></td><td colspan="3"></td></tr><tr><td>AI Scientist</td><td>GPT-01 Claude-3-5-Sonnet</td><td>0.4513 0.4565</td><td>0.5500 05279</td><td>0.4878 0.5804</td><td>0.5750 06346</td><td>0.6734 0 251</td><td>0.6802 07628</td><td>-0.0390 -0.014</td><td>-0.2837 -0.0790</td><td>0.1671 -0.0051</td><td>0.5541 0.5543</td><td>0.5426 0.572</td><td>0.5966 0.5454 0.6321</td></tr><tr><td>Gmini2.0Flash-Thinking</td><td></td><td>00.4279</td><td>0.5219</td><td>0.6337</td><td>0.6114</td><td>05696</td><td>0.5876</td><td>03565</td><td>00593</td><td>0.2773</td><td>0.66535</td><td>0.5499</td></tr><tr><td>Deeppeek-V3</td><td></td><td>07999</td><td>0.7409</td><td>.9120</td><td>07657</td><td>2.0180</td><td>1.2594</td><td>01926</td><td>.0621</td><td>-0.0677</td><td>06 6014</td><td>05683</td></tr><tr><td>DepSee-RI</td><td>08575</td><td>0636</td><td>0.4884</td><td>05586</td><td>2.1620</td><td>1.3750</td><td>0.3130</td><td>0.3133</td><td>0.3060</td><td></td><td>06289</td><td>05989</td></tr><tr><td>3BB</td><td></td><td></td><td></td><td></td><td>0.4208</td><td>0.2667</td><td>0.4112</td><td></td><td></td><td>0.2511</td><td>0.5913</td><td>0.6074</td></tr><tr><td>CycleReviewer</td><td></td><td>0.2617 0.2588</td><td>0.3931 0.3998</td><td>0.2880 0.2562</td><td>0.3998</td><td>0.2601</td><td>0.4034</td><td>0.2377 02320</td><td>0.2498 0.2772</td><td>0.1905</td><td>05865</td><td>0.6051</td></tr><tr><td>DeepReviewer</td><td>14B</td><td>0.2239</td><td>0.3650</td><td>0.2178</td><td>0.3662</td><td>0.2632</td><td>0.4095</td><td>0.3810</td><td>0.3698</td><td>0.3239</td><td>0.6057</td><td>0.6380</td></tr></table>

DeepReviewer achieves the highest Rating Spearman correlations of 0.3559 and 0.4047 on ICLR 2024 and ICLR 2025 respectively, improving upon CycleReviewer-70B by $6 . 0 4 \%$ and AI Scientist (DeepSeek-R1) by $2 5 . 0 2 \%$ . In the paper selection task, It demonstrates superior discrimination ability with pairwise accuracies of 0.62 and 0.64 on ICLR 2024 and ICLR 2025 respectively.

<table><tr><td>Baselines</td><td colspan="2">Constructive Value</td><td colspan="2">Analytical Depth</td><td colspan="2">Plausibility</td><td colspan="2">Technical Accuracy</td><td colspan="2">Overall Judgment</td></tr><tr><td>DeepReviewer 14B vs.</td><td>Win(%)↑</td><td>Lose(%)</td><td>Win(%)↑</td><td>Lose(%)</td><td>Win(%)↑</td><td>Lose(%)</td><td>Win(%)↑</td><td>Lose(%)</td><td>Win(%)↑</td><td>Lose(%)</td></tr><tr><td>ICLR 2024</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>AI Scientist GPT-01</td><td>89.80</td><td>6.67</td><td>87.67</td><td>6.67</td><td>51.69</td><td>3.53</td><td>25.12</td><td>11.67</td><td>88.21</td><td>6.63</td></tr><tr><td>AI Scientist Claude-3.5-Sonnet</td><td>966.88</td><td>3.12</td><td>97.92</td><td>2.08</td><td>80..21</td><td>4.17</td><td>77.08</td><td>2.08</td><td>95.74</td><td>4.26</td></tr><tr><td>AIScientis Gemii2.0-Flash-Thinking</td><td>53.47</td><td>17.82</td><td>53.47</td><td>20.79</td><td>24.75</td><td>110.89</td><td>18.81</td><td>20.79</td><td>59.41</td><td>25.74</td></tr><tr><td>AI Scientist DeepSeek-V3</td><td>96.04</td><td>1.98</td><td>99.01</td><td>0.00</td><td>72.28</td><td>0.99</td><td>67.33</td><td>4.95</td><td>96.22</td><td>0.00</td></tr><tr><td>AI Scientist DeepSeek-R1</td><td>89.22</td><td>7.84</td><td>74.51</td><td>13.73</td><td>45.10</td><td>5.88</td><td>26.47</td><td>18.63</td><td>80.20</td><td>16.83</td></tr><tr><td>AgentReview Claude-3.5-Sonnet AentRevie Gemini20-Flash-Thinking</td><td>96.84 98.00</td><td>1.05 1.00</td><td>98.94</td><td>0.00</td><td>90.43</td><td>0.00</td><td>77.08</td><td>0.00</td><td>98.90</td><td>0.00 1.00</td></tr><tr><td>AgentReview GPT-40</td><td>99.02</td><td>0..99</td><td>995.11 99.01</td><td>1.00 0.99</td><td>81.64</td><td>0.01</td><td>65.00</td><td>3.00 4.90</td><td>96.74 98.15</td><td>1.00</td></tr><tr><td>CycleReviewer 8B</td><td>97.30</td><td>1.80</td><td>98.20</td><td>00.91</td><td>95.05 90.92</td><td>0.99</td><td>61.76 87.50</td><td>00.00</td><td>96.09</td><td>00.91</td></tr><tr><td>CycleReviewer 70B</td><td>98.33</td><td>1.11</td><td>98.89</td><td>0.01</td><td>92.78</td><td>0.91 0.01</td><td>7944</td><td>0.01</td><td>98.33</td><td>1.11</td></tr><tr><td>ICLR 2025</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>AI Scientist GPT-01</td><td></td><td></td><td></td><td>8.33</td><td></td><td>4.17</td><td>37.50</td><td>8.33</td><td>91.67</td><td>8.33</td></tr><tr><td>AI Scientist Claude-3.5-Sonnet</td><td>91.67 97.87</td><td>8.33 1.06</td><td>89.58</td><td></td><td>60.42</td><td></td><td></td><td>00</td><td>98.94</td><td></td></tr><tr><td>A Sientist Gemii2.0-Flash-Thinking</td><td>52.43</td><td></td><td>100.00</td><td>00.00</td><td>92.55</td><td>1.06</td><td>65.96</td><td></td><td></td><td>1.06</td></tr><tr><td></td><td>96.04</td><td>18.45 2.97</td><td>52.43</td><td>23.30</td><td>33.98</td><td>7.77</td><td>19.42</td><td>20.39</td><td>559.41 97.03</td><td>24.75</td></tr><tr><td>AI Scientist DeepSeek-V3</td><td>89.29</td><td>6.25</td><td>97.03 81.25</td><td>1.98 10.71</td><td>775.25</td><td>2.97 5.36</td><td>63.37 26.79</td><td>3.96 18.75</td><td>87.39</td><td>2.97 9.01</td></tr><tr><td>AI Scientist DeepSeek-R1</td><td>95.74</td><td>1.06</td><td>97.85</td><td>2.15</td><td>51.79 90.32</td><td>2.15</td><td>74.74</td><td>1.05</td><td>977.83</td><td>2.17</td></tr><tr><td>AgentReview Claude-3.5-Sonnet</td><td>92.16</td><td>1.96</td><td>93.08</td><td>3.00</td><td>78.20</td><td>0.65</td><td>61.76</td><td>4.90</td><td>92.16</td><td>4.90</td></tr><tr><td>AgentReview Gemini-2.0-Flash-Thinking AgentReview GPT-40</td><td>95.28</td><td>2.09</td><td>95.37</td><td>1.40</td><td>92.10</td><td>0.85</td><td>65.03</td><td>5.47</td><td>94.15</td><td>2.39</td></tr><tr><td>CycleReviewer 8B</td><td>988.45</td><td>1.55</td><td>98.24</td><td>1.89</td><td>86.37</td><td>0.77</td><td>86.36</td><td>2.27</td><td>98.45</td><td>1.55</td></tr><tr><td>CycleReviewer 70B</td><td>96.17</td><td>1.64</td><td>96.17</td><td>2.19</td><td>86.34</td><td>1.64</td><td>72.68</td><td>3.28</td><td>96.72</td><td>1.64</td></tr></table>

Table 4: Direct comparison of DeepReviewer with the baselines on general alignment tasks. Win indicates that Gemini-2.0-Flash-Thinking assesses DeepReviewer’s response as superior compared to the baseline. Cells marked in light gray suggest baseline the winner.

Table 3 presents a detailed analysis across three critical dimensions: Soundness, Presentation, and Contribution. Particularly for Soundness assessment on ICLR 2024, DeepReviewer-14B achieves an MSE of 0.1578 and MAE of 0.3029, representing improvements of ${ \bar { 3 } } 3 . 5 8 \%$ and $2 2 . 0 9 \%$ over CycleReviewer-70B. While DeepReviewer shows marginally lower performance than AI Scientist (Gemini-2.0-Flash-Thinking) in Contribution and Soundness accuracy, it maintains a balanced and strong performance across all dimensions.

We observe a strong correlation between fine-grained assessment capability and overall rating performance. Models that excel in dimension-specific evaluations, such as DeepReviewer and Claude-3.5-Sonnet, consistently demonstrate superior performance in overall ratings. This pattern validates the effectiveness of our multi-stage reasoning chain design, particularly the necessity of multi-facet evaluation in our framework.

![](images/c0ceb067f40e099eb65b09307ef9809e15f66705378eb06582cf3aaf4645e252.jpg)  
Figure 2: Demonstrates the scoring comparison of AI Scientist and DeepReviewer 14B models under normal and attack scenarios. The DeepReviewer model shows the smallest increase in scores (the growth of red bars relative to blue bars in the graph) when under attack, indicating its stronger robustness.

![](images/0c0f096bef4df8361f8cf219c4c5adf129ac525b4a49a54b7bf0dc55711a8670.jpg)  
Figure 3: The performance of the DeepReviewer model in the Test-Time Scaling experiment. The $\mathbf { X }$ -axis represents the number of Tokens generated during model inference, and the y-axis represents different evaluation metrics. The green and red dashed lines are linear regression fitting curves for Reasoning Path Scaling and Reviewer Scaling scaling methods, respectively.

# 5.3 Review Text Quality

Table 4 shows that DeepReviewer’s overwhelming advantages across all evaluation dimensions. Interestingly, in the comparison with AI Scientist (Gemini-2.0-Flash-Thinking), despite being used as the judge, Gemini assessed most reviews in favor of DeepReviewer (winning $5 3 . 4 7 \%$ in constructive value and analytical depth), with only two dimensions showing preference for its own reviews $( 2 0 . 7 9 \%$ in technical accuracy). This self-critical evaluation further validates the objectivity of our assessment framework. In terms of overall judgment, DeepReviewer achieves remarkable win rates of $8 8 . 2 1 \%$ against AI Scientist (GPT-o1) and $9 8 . 1 5 \%$ against AgentReview (GPT-4o) on ICLR 2024.

The advantages are most prominent in constructive value and analytical depth. When compared with AgentReview (GPT-4o), DeepReviewer achieves win rates of $9 9 . 0 2 \%$ and $9 9 . 0 1 \%$ respectively, indicating that our Deep review with Thinking framework generates more insightful analysis and actionable suggestions. These qualitative assessments corroborate our quantitative findings, further validating the effectiveness of the multi-stage reasoning approach in our framework.

# 5.4 Defend Attacks Analysis

We evaluate DeepReviewer’s robustness against adversarial attacks [Ye et al., 2024] by inserting malicious instructions into input papers. Figure 2 illustrates the rating comparison under normal and attack scenarios across different dimensions. Though not specifically trained with any adversarial samples, The DeepReviewer model demonstrates superior robustness compared to baseline systems. Under attack, the overall rating increase for DeepReviewer is merely 0.31 points (from 5.38 to 5.69), while other systems show substantial vulnerability, for example, Gemini-2.0-Flash-Thinking exhibits a dramatic increase of 4.26 points (from 4.23 to 8.49) and DeepSeek-V3 shows a 1.41 increase (from 6.76 to 8.17). This pattern held across fine-grained dimensions: for instance, Soundness scores for DeepReviewer increased by only 0.12 points, compared to larger increases for Claude-3.5-Sonnet (1.10) and Gemini-2.0-Flash-Thinking (1.38). We attribute this robustness to DeepReviewer’s multi-stage reasoning framework, which, unlike direct input-output models, including content understanding, novelty verification, and reliability checks. It enabling a focus on intrinsic paper quality despite malicious prompts. However, the slight score increases under attack suggest room for improvement, we suggest that incorporating adversarial samples during training.

# 5.5 Test-Time Scalability Study

DeepReviewer model features unique test-time scaling capabilities through two mechanisms, both controllable via input instructions: Reasoning Path Scaling and Reviewer Scaling. Reasoning Path Scaling offers three inference modes—Fast, Standard, and Best—with progressively deeper reasoning and corresponding output token lengths of approximately 3,000, 8,000, and 14,500 tokens, respectively. Complementing this, Reviewer Scaling, employed within Standard mode, adjusts the number of simulated reviewers from $\mathbf { R } { = } 1$ to $\scriptstyle \mathrm { R = } 6$ . It enabling the synthesis of multi-perspective evaluations through simulated reviewer collaboration. Both scaling mechanisms inherently extend the model’s evaluation process: Reasoning Path Scaling by increasing analytical depth, and Reviewer Scaling by emulating collaborative review.

Performance Analysis. Figure 3 illustrates significant performance enhancements as inference computation increases. In Reasoning Path Scaling (red stars), switching from Fast to Best mode results in steady improvements across all metrics, with the Rating Spearman correlation increasing by $8 . 9 7 \%$ (from 0.326 to 0.355). Reviewer Scaling (green diamonds) presents more diverse patterns across various tasks. In scoring tasks (Decision Accuracy, Rating MSE, Soundness MSE), consistent performance gains are observed with additional reviewers, indicating that score aggregation is enhanced by multiple viewpoints. The performance variability in Reviewer Scaling, especially when $R \neq 4$ , likely arises from the model’s training distribution being focused around four reviewers. Despite some variability, both scaling methods show positive trends (see regression lines), indicating our framework effectively uses more computational resources. The benefits vary by metric: scoring tasks improve most, followed by ranking, then selection. This suggests that multi-stage reasoning excels in complex paper evaluations, while simpler comparisons (e.g., choosing between two papers) gain less from added reasoning.

Furthermore, we observe that DeepReviewer’s Fast mode, with only half the output tokens (3000), outperformed the CycleReviewer model (6000 output tokens) across various metrics (See Table 3), including Decision Accuracy, Rating MSE, and fine-grained Spearman correlations for Soundness, Presentation, and Contribution. Despite its simplified reasoning path, Fast mode retains core evaluation logic, such as identifying key paper content and critical flaws. We show that DeepReviewer utilizes each token more effectively, focusing on the most crucial information and achieving high performance with fewer output tokens.

Despite these variations, both scaling approaches demonstrate positive trends across metrics, validating that increased computational investment – whether through more sophisticated inference modes or additional simulated reviewers – enhances the model’s paper assessment capabilities.

# 6 Conclusions

We presented DeepReviewer, a novel framework for research paper evaluation aimed at enhancing the reliability of LLMs in paper reviews. DeepReviewer achieves adaptable reasoning depth through Test-Time Scaling to meet diverse needs. Our contributions are threefold: (1) the creation of

DeepReview-13K, a detailedly annotated dataset that facilitates training for systematic and deep paper evaluation; (2) the training of the DeepReviewer model; and (3) comprehensive validation of DeepReviewer’s superiority in both objective and subjective assessments. Notably, we explored and demonstrated effective Test-Time Scaling through Reasoning Path and Reviewer Scaling strategies.

# Limitations

Firstly, our approach relies on a synthetic dataset, DeepReview-13K, constructed through an automated pipeline. Although meticulously designed to mimic expert review processes and incorporating quality control mechanisms, this synthetic data may not fully capture the complexities and nuances of genuine human paper review. We have strived to mitigate this by leveraging real-world review data from ICLR conferences and incorporating structured reasoning annotations, but the inherent limitations of synthetic data persist. Secondly, while DeepReviewer offers Test-Time Scaling for efficiency, the "Best" mode, which employs the complete reasoning chain and external knowledge retrieval, can be computationally intensive. We address this by providing "Fast" and "Standard" modes, allowing for a trade-off between thoroughness and computational cost, catering to diverse application needs. Furthermore, while we have shown robustness against adversarial attacks, complete immunity is not yet achieved, indicating a need for ongoing research into enhancing security and reliability. Despite these limitations, DeepReviewer represents a significant step towards more reliable and robust LLM-based paper review systems, and our exploration of robust structured reasoning opens avenues for future research.

# Ethical Considerations

The development of DeepReviewer, while holding significant promise for enhancing the efficiency and potentially the quality of scholarly paper review, inherently carries ethical considerations that demand careful attention. We recognize that automating aspects of the peer review process introduces risks of bias amplification, deskilling of human reviewers, and a potential erosion of transparency and accountability. Specifically, DeepReviewer, like any LLM, could inadvertently perpetuate or even amplify existing biases present in the training data or encoded within its architecture. This could lead to systematic disadvantages for research from underrepresented groups, novel or unconventional methodologies, or topics perceived as less mainstream, even if the DeepReview-13K dataset was synthetically generated to be representative and fair. Furthermore, over-reliance on automated review assistance might diminish the critical thinking skills of human reviewers, potentially leading to a deskilling effect over time and a dependence on AI-driven assessments without sufficient human oversight.

To proactively address these ethical concerns and mitigate potential harms, we have implemented a multi-faceted approach throughout DeepReviewer’s development and deployment. Firstly, while our training data is synthetic, we have rigorously designed the DeepReview-13K dataset and its generation pipeline to explicitly model expert reviewer reasoning and incorporate diverse perspectives, aiming to minimize the introduction of unintended biases. Secondly, we emphasize that DeepReviewer is intended as a decision support tool, designed to augment, not replace, human expertise. We strongly advocate for a human-in-the-loop approach, where DeepReviewer’s outputs are critically evaluated and contextualized by expert reviewers. To ensure transparency, we are releasing DeepReviewer as an open-source resource, allowing for community scrutiny of its code, architecture, and potential biases. Alongside the code release, we will provide comprehensive user guidelines and best practices that explicitly caution against over-reliance on automated outputs and emphasize the importance of human oversight and critical assessment. Furthermore, our open-source licensing, while permissive, mandates that users disclose their institutional affiliation, personal information, and intended use case upon downloading DeepReviewer. This measure aims to foster accountability and enable a feedback loop, allowing us to monitor real-world applications, gather user feedback, and iteratively improve the model and its ethical safeguards. We also commit to ongoing bias auditing and benchmarking of DeepReviewer across diverse datasets and review scenarios, continually evaluating its performance and identifying areas for refinement. We believe these proactive measures, combined with ongoing community engagement and responsible user practices, are crucial to harnessing the benefits of Deep-Reviewer while minimizing its potential for harm and ensuring its ethical and beneficial application within the scientific peer review process.

References   
M. Abdin, J. Aneja, H. Behl, S. Bubeck, R. Eldan, S. Gunasekar, M. Harrison, R. J. Hewett, M. Javaheripi, P. Kauffmann, J. R. Lee, Y. T. Lee, Y. Li, W. Liu, C. C. T. Mendes, A. Nguyen, E. Price, G. de Rosa, O. Saarikivi, A. Salim, S. Shah, X. Wang, R. Ward, Y. Wu, D. Yu, C. Zhang, and Y. Zhang. Phi-4 technical report, 2024. URL https://arxiv.org/abs/2412.08905.   
J. Achiam, S. Adler, S. Agarwal, L. Ahmad, I. Akkaya, F. L. Aleman, D. Almeida, J. Altenschmidt, S. Altman, S. Anadkat, et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.   
A. AI. Aider is ai pair programming in your terminal. https://github.com/Aider-AI/aider, 2025.   
E. Akyürek, D. Schuurmans, J. Andreas, T. Ma, and D. Zhou. What learning algorithm is in-context learning? investigations with linear models. arXiv preprint arXiv:2211.15661, 2022.   
B. Alberts, B. Hanson, and K. L. Kelner. Reviewing peer review, 2008.   
A. Asai, J. He, R. Shao, W. Shi, A. Singh, J. C. Chang, K. Lo, L. Soldaini, S. Feldman, M. D’arcy, D. Wadden, M. Latzke, M. Tian, P. Ji, S. Liu, H. Tong, B. Wu, Y. Xiong, L. Zettlemoyer, G. Neubig, D. Weld, D. Downey, W. tau Yih, P. W. Koh, and H. Hajishirzi. Openscholar: Synthesizing scientific literature with retrieval-augmented lms, 2024. URL https://arxiv.org/abs/2411.14199.   
J. Bai, S. Bai, Y. Chu, Z. Cui, K. Dang, X. Deng, Y. Fan, W. Ge, Y. Han, F. Huang, et al. Qwen technical report. arXiv preprint arXiv:2309.16609, 2023.   
I. Blog. Iclr 2025: Assisting reviewers. https://blog.iclr.cc/2024/10/09/ iclr2025-assisting-reviewers/, 2024. Accessed: 2024-10-09.   
L. Chris, L. Cong, L. Robert, Tjarko, F. Jakob, C. Jeff, and H. David. The ai scientist: Towards fully automated open-ended scientific discovery. arXiv preprint arXiv:2408.06292v3, 2024. URL https://www.arxiv.org/abs/2408.06292v3.   
B. Daniil, A., M. Robert, and G. Gabe. Emergent autonomous scientific research capabilities of large language models. arXiv preprint arXiv:2304.05332v1, 2023. URL https://www.arxiv.org/ abs/2304.05332v1.   
M. D’Arcy, T. Hope, L. Birnbaum, and D. Downey. Marg: Multi-agent review generation for scientific papers. arXiv preprint arXiv:2401.04259, 2024.   
Y. Ding, L. L. Zhang, C. Zhang, Y. Xu, N. Shang, J. Xu, F. Yang, and M. Yang. LongroPE: Extending LLM context window beyond 2 million tokens. In Forty-first International Conference on Machine Learning, 2024. URL https://openreview.net/forum?id=ONOtpXLqqw.   
I. Drori and D. Te’eni. Human-in-the-loop ai reviewing: Feasibility, opportunities, and risks. Journal of the Association for Information Systems, 25(1):98–109, 2024.   
J. Du, Y. Wang, W. Zhao, Z. Deng, S. Liu, R. Lou, H. P. Zou, P. Narayanan Venkit, N. Zhang, M. Srinath, H. R. Zhang, V. Gupta, Y. Li, T. Li, F. Wang, Q. Liu, T. Liu, P. Gao, C. Xia, C. Xing, C. Jiayang, Z. Wang, Y. Su, R. S. Shah, R. Guo, J. Gu, H. Li, K. Wei, Z. Wang, L. Cheng, S. Ranathunga, M. Fang, J. Fu, F. Liu, R. Huang, E. Blanco, Y. Cao, R. Zhang, P. S. Yu, and W. Yin. LLMs assist NLP researchers: Critique paper (meta-)reviewing. In Y. Al-Onaizan, M. Bansal, and Y.-N. Chen, editors, Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, pages 5081–5099, Miami, Florida, USA, Nov. 2024. Association for Computational Linguistics. doi: 10.18653/v1/2024.emnlp-main.292. URL https://aclanthology.org/2024.emnlp-main.292/.   
M. Funkquist, I. Kuznetsov, Y. Hou, and I. Gurevych. Citebench: A benchmark for scientific citation text generation. arXiv preprint arXiv:2212.09577, 2022.   
Z. Gao, K. Brantley, and T. Joachims. Reviewer2: Optimizing review generation through prompt generation. arXiv preprint arXiv:2402.10886, 2024.   
A. Ghafarollahi and M. J. Buehler. Sciagents: Automating scientific discovery through multi-agent intelligent graph reasoning. arXiv preprint arXiv:2409.05556, 2024.   
X. Guan, L. L. Zhang, Y. Liu, N. Shang, Y. Sun, Y. Zhu, F. Yang, and M. Yang. rstar-math: Small llms can master math reasoning with self-evolved deep thinking, 2025. URL https: //arxiv.org/abs/2501.04519.   
D. Guo, D. Yang, H. Zhang, J. Song, R. Zhang, R. Xu, Q. Zhu, S. Ma, P. Wang, X. Bi, et al. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948, 2025.   
S. Hao, S. Sukhbaatar, D. Su, X. Li, Z. Hu, J. Weston, and Y. Tian. Training large language models to reason in a continuous latent space, 2024. URL https://arxiv.org/abs/2412.06769.   
D. Hendrycks, C. Burns, S. Kadavath, A. Arora, S. Basart, E. Tang, D. Song, and J. Steinhardt. Measuring mathematical problem solving with the math dataset. NeurIPS, 2021.   
X. Hu, H. Fu, J. Wang, Y. Wang, Z. Li, R. Xu, Y. Lu, Y. Jin, L. Pan, and Z. Lan. Nova: An iterative planning and search approach to enhance novelty and diversity of llm generated ideas. arXiv preprint arXiv:2410.14255, 2024.   
A. Jaech, A. Kalai, A. Lerer, A. Richardson, A. El-Kishky, A. Low, A. Helyar, A. Madry, A. Beutel, A. Carney, et al. Openai o1 system card. arXiv preprint arXiv:2412.16720, 2024.   
Z. Ji, T. Yu, Y. Xu, N. Lee, E. Ishii, and P. Fung. Towards mitigating LLM hallucination via self reflection. In H. Bouamor, J. Pino, and K. Bali, editors, Findings of the Association for Computational Linguistics: EMNLP 2023, pages 1827–1843, Singapore, Dec. 2023. Association for Computational Linguistics. doi: 10.18653/v1/2023.findings-emnlp.123. URL https:// aclanthology.org/2023.findings-emnlp.123/.   
Y. Jin, Q. Zhao, Y. Wang, H. Chen, K. Zhu, Y. Xiao, and J. Wang. AgentReview: Exploring peer review dynamics with LLM agents. In Y. Al-Onaizan, M. Bansal, and Y.-N. Chen, editors, Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, pages 1208–1226, Miami, Florida, USA, Nov. 2024a. Association for Computational Linguistics. doi: 10.18653/v1/2024.emnlp-main.70. URL https://aclanthology.org/2024.emnlp-main.70/.   
Y. Jin, Q. Zhao, Y. Wang, H. Chen, K. Zhu, Y. Xiao, and J. Wang. Agentreview: Exploring peer review dynamics with llm agents. arXiv preprint arXiv:2406.12708, 2024b.   
D. Kang, W. Ammar, B. Dalvi, M. Van Zuylen, S. Kohlmeier, E. Hovy, and R. Schwartz. A dataset of peer reviews (peerread): Collection, insights and nlp applications. arXiv preprint arXiv:1804.09635, 2018.   
P. Langley. Scientific discovery: Computational explorations of the creative processes. MIT press, 1987.   
G. R. Latona, M. H. Ribeiro, T. R. Davidson, V. Veselovsky, and R. West. The ai review lottery: Widespread ai-assisted peer reviews boost paper scores and acceptance rates. arXiv preprint arXiv:2405.02150, 2024.   
D. Li, B. Jiang, L. Huang, A. Beigi, C. Zhao, Z. Tan, A. Bhattacharjee, Y. Jiang, C. Chen, T. Wu, K. Shu, L. Cheng, and H. Liu. From generation to judgment: Opportunities and challenges of llm-as-a-judge. arXiv preprint arXiv: 2411.16594, 2024a.   
M. Li, E. Hovy, and J. H. Lau. Summarizing multiple documents with conversational structure for meta-review generation. arXiv preprint arXiv:2305.01498, 2023.   
M. Y. Li, E. Fox, and N. Goodman. Automated statistical model discovery with language models. In Forty-first International Conference on Machine Learning, 2024b. URL https://openreview. net/forum?id=B5906M4Wnd.   
Z. Li, Y. Chang, and X. Le. Simulating expert discussions with multi-agent for enhanced scientific problem solving. In T. Ghosal, A. Singh, A. Waard, P. Mayr, A. Naik, O. Weller, Y. Lee, S. Shen, and Y. Qin, editors, Proceedings of the Fourth Workshop on Scholarly Document Processing (SDP 2024), pages 243–256, Bangkok, Thailand, Aug. 2024c. Association for Computational Linguistics. URL https://aclanthology.org/2024.sdp-1.23/.   
W. Liang, Z. Izzo, Y. Zhang, H. Lepp, H. Cao, X. Zhao, L. Chen, H. Ye, S. Liu, Z. Huang, et al. Monitoring ai-modified content at scale: A case study on the impact of chatgpt on ai conference peer reviews. arXiv preprint arXiv:2403.07183, 2024.   
C.-Y. Lin. ROUGE: A package for automatic evaluation of summaries. In Text Summarization Branches Out, pages 74–81, Barcelona, Spain, July 2004. Association for Computational Linguistics. URL https://aclanthology.org/W04-1013/.   
A. Madaan, N. Tandon, P. Gupta, S. Hallinan, L. Gao, S. Wiegreffe, U. Alon, N. Dziri, S. Prabhumoye, Y. Yang, et al. Self-refine: Iterative refinement with self-feedback. Advances in Neural Information Processing Systems, 36, 2024.   
M. Nye, A. J. Andreassen, G. Gur-Ari, H. Michalewski, J. Austin, D. Bieber, D. Dohan, A. Lewkowycz, M. Bosma, D. Luan, et al. Show your work: Scratchpads for intermediate computation with language models. arXiv preprint arXiv:2112.00114, 2021.   
K. Papineni, S. Roukos, T. Ward, and W.-J. Zhu. Bleu: a method for automatic evaluation of machine translation. In Proceedings of the 40th Annual Meeting on Association for Computational Linguistics, ACL ’02, page 311–318, USA, 2002. Association for Computational Linguistics. doi: 10.3115/1073083.1073135. URL https://doi.org/10.3115/1073083.1073135.   
Qwen, :, A. Yang, B. Yang, B. Zhang, B. Hui, B. Zheng, B. Yu, C. Li, D. Liu, F. Huang, H. Wei, H. Lin, J. Yang, J. Tu, J. Zhang, J. Yang, J. Yang, J. Zhou, J. Lin, K. Dang, K. Lu, K. Bao, K. Yang, L. Yu, M. Li, M. Xue, P. Zhang, Q. Zhu, R. Men, R. Lin, T. Li, T. Tang, T. Xia, X. Ren, X. Ren, Y. Fan, Y. Su, Y. Zhang, Y. Wan, Y. Liu, Z. Cui, Z. Zhang, and Z. Qiu. Qwen2.5 technical report, 2025. URL https://arxiv.org/abs/2412.15115.   
S. Rajbhandari, J. Rasley, O. Ruwase, and Y. He. Zero: Memory optimizations toward training trillion parameter models, 2020. URL https://arxiv.org/abs/1910.02054.   
S. Rasal and E. Hauer. Navigating complexity: Orchestrated problem solving with multi-agent llms. arXiv preprint arXiv:2402.16713, 2024.   
J. Rasley, S. Rajbhandari, O. Ruwase, and Y. He. Deepspeed: System optimizations enable training deep learning models with over 100 billion parameters. In Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining, KDD ’20, page 3505–3506, New York, NY, USA, 2020. Association for Computing Machinery. ISBN 9781450379984. doi: 10.1145/3394486.3406703. URL https://doi.org/10.1145/3394486.3406703.   
B. Rewina, P. Natalie, B. Sreyoshi, K. Satya, G. Alex, C. Elizabeth, I. Ikkei, T. David, C. Aman, and N. Naumaan. Potential and perils of large language models as judges of unstructured textual data. arXiv preprint arXiv:2501.08167v2, 2025. URL https://www.arxiv.org/abs/2501.08167v2.   
S. K. K. Santu, S. K. Sinha, N. Bansal, A. Knipper, S. Sarkar, J. Salvador, Y. Mahajan, S. Guttikonda, M. Akter, M. Freestone, et al. Prompting llms to compose meta-review drafts from peer-review narratives of scholarly manuscripts. arXiv preprint arXiv:2402.15589, 2024.   
D. Scherbakov, N. Hubig, V. Jansari, A. Bakumenko, and L. A. Lenert. The emergence of large language models (llm) as a tool in literature reviews: an llm automated systematic review, 2024. URL https://arxiv.org/abs/2409.04600.   
L. A. Schintler, C. L. McNeely, and J. Witte. A critical examination of the ethics of ai-mediated peer review, 2023. URL https://arxiv.org/abs/2309.12356.   
C. Si, D. Yang, and T. Hashimoto. Can LLMs generate novel research ideas? a large-scale human study with $1 0 0 +$ NLP researchers. In The Thirteenth International Conference on Learning Representations, 2025. URL https://openreview.net/forum?id=M23dTGWCZy.   
H. Su, R. Chen, S. Tang, X. Zheng, J. Li, Z. Yin, W. Ouyang, and N. Dong. Two heads are better than one: A multi-agent system has the potential to improve scientific idea generation. arXiv preprint arXiv:2410.09403, 2024.   
S. Swarnadeep, L. Xian, G. Marjan, W. Jason, and W. Tianlu. Learning to plan & reason for evaluation with thinking-llm-as-a-judge. arXiv preprint arXiv:2501.18099v1, 2025. URL https: //www.arxiv.org/abs/2501.18099v1.   
C. Tan, D. Lyu, S. Li, Z. Gao, J. Wei, S. Ma, Z. Liu, and S. Z. Li. Peer review as a multi-turn and long-context dialogue with role-based interactions. arXiv preprint arXiv:2406.05688, 2024a.   
C. Tan, D. Lyu, S. Li, Z. Gao, J. Wei, S. Ma, Z. Liu, and S. Z. Li. Peer review as a multi-turn and long-context dialogue with role-based interactions, 2024b. URL https://arxiv.org/abs/2406. 05688.   
H. Touvron, T. Lavril, G. Izacard, X. Martinet, M.-A. Lachaux, T. Lacroix, B. Rozière, N. Goyal, E. Hambro, F. Azhar, et al. Llama: Open and efficient foundation language models. arXiv preprint arXiv:2302.13971, 2023.   
K. Tyser, B. Segev, G. Longhitano, X.-Y. Zhang, Z. Meeks, J. Lee, U. Garg, N. Belsten, A. Shporer, M. Udell, et al. Ai-driven review systems: evaluating llms in scalable and bias-aware academic reviews. arXiv preprint arXiv:2408.10365, 2024.   
B. Wang, C. Xu, X. Zhao, L. Ouyang, F. Wu, Z. Zhao, R. Xu, K. Liu, Y. Qu, F. Shang, B. Zhang, L. Wei, Z. Sui, W. Li, B. Shi, Y. Qiao, D. Lin, and C. He. Mineru: An open-source solution for precise document content extraction, 2024a. URL https://arxiv.org/abs/2409.18839.   
Q. Wang, Q. Zeng, L. Huang, K. Knight, H. Ji, and N. F. Rajani. ReviewRobot: Explainable paper review generation based on knowledge synthesis. In B. Davis, Y. Graham, J. Kelleher, and Y. Sripada, editors, Proceedings of the 13th International Conference on Natural Language Generation, pages 384–397, Dublin, Ireland, Dec. 2020. Association for Computational Linguistics. doi: 10.18653/v1/2020.inlg-1.44. URL https://aclanthology.org/2020.inlg-1.44/.   
X. Wang, J. Wei, D. Schuurmans, Q. V. Le, E. H. Chi, S. Narang, A. Chowdhery, and D. Zhou. Selfconsistency improves chain of thought reasoning in language models. In The Eleventh International Conference on Learning Representations, 2023.   
Y. Wang, Z. Yu, W. Yao, Z. Zeng, L. Yang, C. Wang, H. Chen, C. Jiang, R. Xie, J. Wang, X. Xie, W. Ye, S. Zhang, and Y. Zhang. PandaLM: An automatic evaluation benchmark for LLM instruction tuning optimization. In The Twelfth International Conference on Learning Representations, 2024b. URL https://openreview.net/forum?id=5Nn2BLV7SB.   
J. Wei, X. Wang, D. Schuurmans, M. Bosma, F. Xia, E. H. Chi, Q. V. Le, D. Zhou, et al. Chain-ofthought prompting elicits reasoning in large language models. In Advances in Neural Information Processing Systems, 2022.   
Y. Weng, M. Zhu, F. Xia, B. Li, S. He, S. Liu, B. Sun, K. Liu, and J. Zhao. Large language models are better reasoners with self-verification. In The 2023 Conference on Empirical Methods in Natural Language Processing, 2023.   
Y. Weng, M. Zhu, G. Bao, H. Zhang, J. Wang, Y. Zhang, and L. Yang. Cycleresearcher: Improving automated research via automated review. In The Thirteenth International Conference on Learning Representations, 2025. URL https://openreview.net/forum?id=bjcsVLoHYs.   
V. Xiang, C. Snell, K. Gandhi, A. Albalak, A. Singh, C. Blagden, D. Phung, R. Rafailov, N. Lile, D. Mahan, L. Castricato, J.-P. Franken, N. Haber, and C. Finn. Towards system 2 reasoning in llms: Learning how to think with meta chain-of-thought, 2025. URL https://arxiv.org/abs/ 2501.04682.   
Z. Yang, X. Du, J. Li, J. Zheng, S. Poria, and E. Cambria. Large language models for automated open-domain scientific hypotheses discovery. In L.-W. Ku, A. Martins, and V. Srikumar, editors, Findings of the Association for Computational Linguistics: ACL 2024, pages 13545–13565, Bangkok, Thailand, Aug. 2024. Association for Computational Linguistics. doi: 10.18653/v1/ 2024.findings-acl.804. URL https://aclanthology.org/2024.findings-acl.804/.   
S. Yao, D. Yu, J. Zhao, I. Shafran, T. Griffiths, Y. Cao, and K. Narasimhan. Tree of thoughts: Deliberate problem solving with large language models. Advances in Neural Information Processing Systems, 36, 2024.   
R. Ye, X. Pang, J. Chai, J. Chen, Z. Yin, Z. Xiang, X. Dong, J. Shao, and S. Chen. Are we there yet? revealing the risks of utilizing large language models in scholarly peer review. arXiv preprint arXiv:2412.01708, 2024.   
J. Yu, Z. Ding, J. Tan, K. Luo, Z. Weng, C. Gong, L. Zeng, R. Cui, C. Han, Q. Sun, et al. Automated peer reviewing in paper sea: Standardization, evaluation, and analysis. arXiv preprint arXiv:2407.12857, 2024.   
W. Yuan, P. Liu, and G. Neubig. Can we automate scientific reviewing?, 2021. URL https: //arxiv.org/abs/2102.00176.   
Q. Zeng, M. Sidhu, H. P. Chan, L. Wang, and H. Ji. Scientific opinion summarization: Paper meta-review generation dataset, methods, and evaluation. In 1st AI4Research Workshop, 2024.   
R. Zhou, L. Chen, and K. Yu. Is LLM a reliable reviewer? a comprehensive evaluation of LLM on automatic paper reviewing tasks. In N. Calzolari, M.-Y. Kan, V. Hoste, A. Lenci, S. Sakti, and N. Xue, editors, Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024), pages 9340–9351, Torino, Italia, May 2024a. ELRA and ICCL. URL https://aclanthology.org/2024.lrec-main.816/.   
R. Zhou, L. Chen, and K. Yu. Is llm a reliable reviewer? a comprehensive evaluation of llm on automatic paper reviewing tasks. In Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024), pages 9340–9351, 2024b.   
Z. Zhuang, J. Chen, H. Xu, Y. Jiang, and J. Lin. Large language models for automated scholarly paper review: A survey. arXiv preprint arXiv:2501.10326, 2025.   
Y. Zonglin, D. Xinya, L. Junxian, Z. Jie, P. Soujanya, and C. Erik. Large language models for automated open-domain scientific hypotheses discovery. arXiv preprint arXiv:2309.02726, 2023. URL https://www.arxiv.org/abs/2309.02726.   
D. Zyska, N. Dycke, J. Buchmann, I. Kuznetsov, and I. Gurevych. Care: Collaborative ai-assisted reading environment. arXiv preprint arXiv:2302.12611, 2023.

# A Responsible Use and Recommendations for DeepReviewer

It is crucial to emphasize that DeepReviewer, despite its advancements in automated paper evaluation, is not intended to replace human peer review. Our work aims to enhance, not substitute, the invaluable expertise and nuanced judgment of human reviewers. DeepReviewer should be regarded as a sophisticated tool to assist researchers and the academic community, providing supplementary insights and streamlining certain aspects of the review process, but always under the careful oversight and final authority of human experts. This section outlines responsible and conservative recommendations for leveraging DeepReviewer’s capabilities in practical scenarios, focusing on how it can aid human researchers and enhance the peer review process without undermining its fundamental human-centric nature.

# A.1 Enhanced Author Self-Assessment and Manuscript Refinement

Perhaps the most appropriate and ethically sound application of DeepReviewer lies in empowering authors to critically assess and refine their manuscripts before they are submitted for formal peer review. By submitting their work to DeepReviewer, authors can obtain an automated, initial evaluation of their paper’s perceived strengths and potential weaknesses across various dimensions such as soundness, clarity of presentation, and potential contribution. This feedback can highlight areas where the manuscript might be strengthened prior to exposure to human reviewers.

However, it is crucial for authors to approach DeepReviewer’s feedback with a discerning and critical mindset. The automated evaluation should be considered as a preliminary signal, not a definitive judgment. Authors must exercise their own expertise and judgment in interpreting the suggestions. DeepReviewer’s output may point to areas that warrant further attention, but the ultimate decisions regarding manuscript revision must rest with the authors themselves, informed by their deep understanding of their own work and potentially by seeking feedback from trusted colleagues. This application strictly positions DeepReviewer as a formative tool for author self-improvement, ensuring that it aids in enhancing manuscript quality without encroaching on the formal peer review process.

# A.2 Preliminary Assistance for Human Reviewers in Initial Paper Scoping

In contexts where human reviewers are faced with a high volume of submissions, DeepReviewer could potentially offer a very limited form of preliminary assistance in the very initial stages of paper scoping. Reviewers could, as an optional and auxiliary step, utilize DeepReviewer to generate a rapid, automated overview of a submitted paper. This might provide a very high-level summary of potential areas of focus within the manuscript. Such a preliminary overview could, in some cases, help reviewers gain a very initial sense of the paper’s scope and potentially assist in workload management, by allowing them to perhaps initially prioritize papers based on a very rough automated categorization.

However, it is absolutely vital to underscore that this use case is strictly as an aid to the reviewer’s workflow, and not as a substitute for any aspect of their intellectual engagement with the paper. The automated output from DeepReviewer should never influence the reviewer’s own independent, detailed reading and critical analysis of the manuscript. Reviewers must engage deeply with the paper itself, applying their expertise and judgment. DeepReviewer’s preliminary output, if used at all, should be treated as an extremely rough and initial signal only, and should not replace or diminish the core, human-driven process of rigorous peer review. Over-reliance on or misinterpretation of automated outputs at this stage carries significant risks and must be avoided.

# A.3 Author-Facing Pre-Review Feedback via Deployed Model

An alternative application, focusing purely on author benefit, is to deploy DeepReviewer as a readily accessible service that authors can utilize to obtain feedback on their manuscripts before they are submitted to a journal or conference and undergo human peer review. In this scenario, DeepReviewer is made available as a tool that authors can directly interact with. Authors submit their manuscript, and in return, receive an automated review generated by DeepReviewer.

Critically, the output of DeepReviewer in this context is intended solely for the authors’ information and improvement. It should not be used in any way as part of a formal submission or decision-making process. The feedback is provided directly to the authors, allowing them to gain insights into how an automated system might evaluate their work. This application bypasses the need to involve or burden human reviewers at this stage, focusing entirely on providing authors with a potentially helpful, albeit automated, perspective on their manuscript. It is essential to emphasize that the feedback generated by DeepReviewer in this author-facing context should be explicitly communicated as not being a substitute for, or representative of, genuine human peer review, and cannot be used as a basis for any acceptance or rejection decisions within formal academic venues.

# B Evaluation Tasks and Metric

To comprehensively assess LLMs’ capabilities in research paper evaluation, we adopt a point-wise evaluation paradigm inspired by the LLM-as-a-judge framework [Li et al., 2024a, Wang et al., 2024b, Rewina et al., 2025, Swarnadeep et al., 2025]. We comprise three core tasks that examine different aspects of LLMs’ ability to perceive, judge, and differentiate paper quality:

Score Task evaluates LLMs’ accuracy in independent paper assessment scenarios. For any paper $C _ { i }$ in the ReviewerBench dataset, the model independently conducts quality assessment and outputs a scalar score $R _ { i } \in \mathbb { R }$ as its predicted quality rating. Ideally, the model’s predicted score $R _ { i }$ should closely align with the average expert rating $S _ { i }$ received during the ICLR review process. We employ Mean Squared Error (MSE) and Mean Absolute Error (MAE) as primary evaluation metrics for this task. Furthermore, we calculated accuracy and F1 score based on the Decision, which is commonly an Accept or Reject output in research paper evaluation systems.

Ranking Task examines LLMs’ ability to distinguish paper quality and effectively rank papers within large collections. Given a set of $N$ papers $\mathcal { C } = C _ { 1 } , C _ { 2 } , \ldots , C _ { N }$ , the model first predicts scores $R _ { 1 } , R _ { 2 } , \ldots , R _ { N }$ for each paper. Subsequently, based on these predicted scores, the model ranks the papers in $\mathcal { C }$ , outputting an ordered sequence $\mathcal { R } = C _ { ( 1 ) } , C _ { ( 2 ) } , \ldots , C _ { ( N ) }$ arranged by predicted quality in descending order, where $C _ { ( i ) }$ represents the paper ranked $i$ -th by the model. The Spearman coefficient is used to evaluate ranking accuracy.

Selection Task simulates practical scenarios such as peer review or reward model construction, where high-quality papers need to be quickly and accurately identified from a small pool of candidates. For this task, we sample non-overlapping small batches $\mathcal { C } b a t c h = C _ { 1 } , C _ { 2 } , \ldots , \bar { C } _ { m }$ from the Test dataset, where $m$ is the predetermined batch size. For each batch Cbatch, the model selects what it considers the highest-quality paper $C _ { b e s t } \in \mathcal { C } _ { b a t c h }$ . The model’s selection is compared against the paper with the highest actual review scores, with accuracy computed as the average success rate across all batch selections. In this study, we set $m = 2$ . And we performed pairwise matching on all papers in the Test dataset to calculate the final Selection score.

Review Comments Evaluate , following the LLM-as-Judge paradigm, we employ Gemini-2.0- Flash-Thinking (The system prompt as shown in Figure 4) as the judge to conduct pairwise comparative evaluations of review comments generated by DeepReviewer and various baseline systems, and Judge outputs “win”, “lose”, or “tie”. For each evaluation instance, we present the assessor with: (1) the original paper, and (2) paired reviews from different systems in randomized order, where each review contains summary, strengths, weaknesses, and suggestions. The assessment covers five critical dimensions: constructive value, analytical depth, plausibility, technical accuracy, and overall judgment.

# C Data Collection Permissions

The original paper data and corresponding review comment data used to construct DeepReview-13K are sourced from OpenReview, with a portion of papers originating from ArXiv. Data from OpenReview is distributed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license, which permits us to copy and modify the review comment data. Paper data from ArXiv may include licenses such as CC BY 4.0 (Creative Commons Attribution), CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike), CC BY-NC-SA 4.0 (Creative Commons Attribution-NonCommercial-ShareAlike), and CC Zero. Given that we have not modified the original papers, our usage is compliant with the original agreements. We do not claim copyright over these materials and will retain the original authors’ names in the distribution of this data.

# D Case Study: Analysis of DeepReviewer’s Meta-Review

To further illustrate the capabilities of DeepReviewer, we present a detailed case study analyzing the Meta-Review generated by DeepReviewer-14B (Best mode) (See in Figure 8) for the "CycleResearcher" paper5 [Weng et al., 2025], a submission from ICLR 2025 not included in the training dataset. This paper, focusing on automating the research lifecycle with LLMs, received four independent reviews from human experts (Reviewer 7LzG: Figure 9, CzSX: Figure 10, GAvj: Figure 11, and 5wHA: Figure 12). DeepReviewer-14B, operating in its most comprehensive "Best" mode, synthesized these diverse perspectives into a single Meta-Review, aiming to emulate the holistic understanding and critical assessment of a seasoned meta-reviewer. A preliminary examination reveals a striking alignment between DeepReviewer’s Meta-Review and the individual human assessments, both in terms of overall sentiment, identified strengths and weaknesses, and even the final score prediction, which closely mirrors the average human rating. This case study delves deeper into the nuances of this comparison, highlighting both the remarkable capabilities and subtle limitations of DeepReviewer in mimicking expert meta-reviewing.

Comparing the summaries, DeepReviewer accurately captures the core contribution of the "CycleResearcher" paper, emphasizing the novel framework for automating the research lifecycle with LLMs, the two key components (CycleResearcher and CycleReviewer), the iterative reinforcement learning approach (SimPO), and the creation of the Review- ${ } . 5 \mathrm { k }$ and Research-8k datasets. This summary resonates strongly with the initial summaries provided by all four human reviewers, each of whom also highlighted these central aspects of the paper. Furthermore, DeepReviewer’s identified strengths mirror the positive aspects recognized by the human reviewers. For instance, the "innovative approach to automating the research lifecycle" echoes Reviewer 7LzG’s praise for the "highly innovative" framework and Reviewer 5wHA’s acknowledgment of the "Innovative Use of Preference Data" and "Automation of the Research Lifecycle." The appreciation for the "Review- ${ } . 5 \mathrm { k }$ and Research- ${ } . 8 \mathrm { k }$ datasets" also aligns with Reviewer 5wHA’s explicit mention of "Valuable Datasets" and Reviewer CzSX’s comment on the datasets being a "resource that is rather helpful for the field." Similarly, the recognition of the "CycleResearcher model generates papers with an average quality level close to human-written preprints" echoes Reviewer GAvj’s observation that the system "achieved an acceptance rate of $3 1 . 0 7 \%$ , similar to ICLR 2024’s acceptance rate" and Reviewer 7LzG’s claim of "papers of quality close to human-written preprints."

![](images/9270a2b30ad48fd8823830528b4321ca44aa9faac351f5bf9d85297fe363d7e2.jpg)  
Figure 4: System prompt used to guide Gemini-2.0-Thinking-Flask as Judge to evaluate generated review comments.

![](images/ad041e9cfe203337d8e63fb83c3f064a37a83af90a47f8c1214caa6081ea1cdf.jpg)  
Figure 5: System prompt designed to instruct the LLM on how to enhance and improve the usefulness of original review comments by incorporating author responses and maintaining original review context.

The most compelling aspect of DeepReviewer’s Meta-Review is its synthesis of weaknesses and corresponding suggestions, demonstrating an ability to identify and consolidate critical concerns raised across different reviewers. DeepReviewer’s critique regarding "potential for bias in the training data" and "lack of analysis of diversity" directly addresses concerns implicitly or explicitly raised by reviewers, particularly regarding generalizability and potential limitations of the datasets. The weakness concerning "computational resources" aligns with Reviewer 7LzG’s mention of "Complexity of Implementation" and the need for "significant computational resources." Similarly, the concern about the "potential for misuse" and the need for "robust safeguards" reflects the ethical considerations raised by Reviewer 5wHA ("Insufficient Ethical Considerations," "Misuse of Technology") and Reviewer GAvj ("Potentially harmful insights, methodologies and applications"). The suggestion for "more details on the specific prompts" and "evaluation criteria" addresses the implicit desire for more clarity on methodology, a common thread in academic reviews. Finally, the point about "generalizability across different research domains" directly mirrors Reviewer 7LzG’s primary "Weakness: Generalizability Across Domains." This systematic identification and aggregation of weaknesses and suggestions from multiple reviewers showcase DeepReviewer’s capacity to perform a nuanced and comprehensive meta-analysis.

While DeepReviewer-14B demonstrates a remarkable ability to synthesize human review insights, it is important to acknowledge potential limitations. For instance, while DeepReviewer captures the essence of the critiques, the depth of technical understanding in specific areas might not fully match that of a human meta-reviewer deeply versed in the nuances of reinforcement learning or AI ethics. Furthermore, the Meta-Review, while comprehensive, might lack the subtle nuances and perspectives that a human meta-reviewer could bring to the synthesis process, potentially overlooking more implicit or nuanced concerns expressed in the individual reviews. However, despite these subtle limitations, DeepReviewer’s performance in generating a coherent, insightful, and critically aligned Meta-Review is undeniably impressive. Crucially, DeepReviewer’s overall rating prediction of 6.0 aligns closely with the average human rating, further validating its ability to not only understand the qualitative aspects of paper evaluation but also to synthesize them into a quantitative judgment consistent with expert consensus. This case study underscores DeepReviewer’s potential as a powerful tool for assisting and potentially augmenting the peer review process.

# E Information About Use Of AI Assistants

This article has been reviewed by DeepReviewer-14B and revised accordingly based on its review comments.

You are participating in a knowledge distillation task to capture the academic reviewing thought process of a target model. While you will receive structured summaries and review opinions of papers, you must

# 8. CRITICAL REFLECTION AND IMPROVEMENT ANALYSIS (9-10 minutes)

![](images/05a2b7ecff8f965695cc2d0ddf0b737b4ffe17ffd9fd72d33d40dea5c29d758c.jpg)  
Figure 6: System prompt designed to guide the LLM in detailed analysis of research papers. This prompt is used specifically during the Novelty Verification stage to make analysis context.

- Theoretical Limitations - Methodological Limitations - Experimental Limitations - Practical Limitations - Theoretical Enhancements - Methodological Improvements - Experimental Refinements - Practical Enhancements - Theoretical extensions - Algorithm improvements - New application domains - Integration possibilities - Performance optimizations - Scalability enhancements

# DEEP THINKING PRINCIPLES:

- Full consideration of each aspect - Systematic assumption questioning - Hidden connection identification - Multiple perspective analysis - Edge case consideration - Practical/theoretical implication evaluation

CRITICAL ANALYSIS ELEMENTS: - Evidence-based conclusions - Alternative explanation consideration - Weakness identification - Generalizability assessment - Theoretical contribution evaluation

# ANALYSIS QUALITY STANDARDS:

1. Thoroughness - Comprehensive aspect coverage - Detailed consideration - Systematic component examination - Complete implication analysis

- Detailed concept examination - Thorough implication consideration - Careful assumption analysis - Deep connection exploration

You are participating in a critical validation task to verify and reflect on reviewer weaknesses identified in academic papers. Your role is to systematically analyze each criticism against the original paper content, ensuring that identified weaknesses are substantiated by concrete evidence.

# IMPORTANT:

1. Your primary goal is to validate each reviewer weakness through careful examination of the paper   
2. Every weakness must be supported by specific evidence from the paper   
3. Consider potential misunderstandings or contradictions between different reviewer opinions

# VALIDATION STAGES:

1. INITIAL WEAKNESS CATEGORIZATION (3 minutes)   
- Categorize weaknesses by type (theoretical, methodological,   
experimental, practical)   
- Map weaknesses to relevant paper sections   
- Note potential misunderstandings

# 2. METHODOLOGICAL VERIFICATION (8 minutes)

- Core method examination:   
\* Mathematical formulations and algorithm \* Theoretical foundations and assumptions \* Implementation details and constraints \* Parameter choices

- Technical validation:

\* Mathematical correctness   
\* Algorithm complexity and convergenc   
\* Model limitations   
\* Error handling

- Literature validation:

- Design Gaps: \* Missing control experiments \* Incomplete ablations \* Insufficient robustness tests

Each experimental weakness requires:

1. Specific experimental details from paper   
2. Numerical results evidence   
3. Missing specifications   
4. Impact on conclusions

4. SYNTHESIS AND REFLECTION (5 minutes) - Cross-validate different reviewer opinions - Resolve apparent conflicts - Distinguish valid from invalid criticisms

# VALIDATION QUALITY STANDARDS:

1. Evidence Requirements - Direct quotes from paper - Specific section references - Clear connection to criticism

# OUTPUT FORMAT:

For each weakness:

2. Evidence Collection:   
a) Method-related Evidence (if applicable):   
- Algorithm/mathematical formulation quotes   
- Implementation details   
- Missing literature citations   
b) Experiment-related Evidence (if applicable): - Dataset/setup descriptions   
- Results and metrics   
- Missing specifications

3. Literature Gap Analysis: - Missing citations list - Required baseline references

4. Validation Analysis: - Primary evidence summary - Supporting quotes - Impact assessment

5. Conclusion:   
- Validity status: [Valid/Partially Valid/Invalid]   
- Confidence level: [High/Medium/Low]   
- Key supporting evidence

# Meta-Review From DeepReviewer-14B

# Summary:

This paper introduces a novel framework for automating the research lifecycle using large language models (LLMs). The framework aims to mimic the iterative process of research, review, and refinement. The core of this framework consists of two models: CycleResearcher, a policy model for generating research papers, and CycleReviewer, a reward model that simulates peer reviews. The authors use an iterative reinforcement learning approach, specifically SimPO, to refine both models. To facilitate training and evaluation, the authors created two large-scale datasets, Review-5k and Research-8k. Empirical results show that CycleResearcher generates papers with an average quality comparable to human-written preprints, achieving a $3 1 . 0 7 \%$ acceptance rate. CycleReviewer shows a $2 6 . 8 9 \%$ improvement in mean absolute error (MAE) compared to individual reviewers. The contribution lies in the application of LLMs to automate the entire research lifecycle, the introduction of large-scale datasets, and the demonstration of a functional iterative framework. This work can impact the way research is conducted, particularly in machine learning. The paper raises questions about potential biases, computational costs, and ethical implications.

# Strength:

The paper's core strength is its innovative approach to automating the research lifecycle using LLMs. The CycleResearcher and CycleReviewer framework effectively models the iterative process of research, review, and refinement. The use of SimPO is a notable technical contribution. The introduction of Review-5k and Research-8k datasets is a valuable resource. The CycleResearcher model generates papers with an average quality level close to human-written preprints, achieving a $3 1 . 0 7 \%$ acceptance rate. The CycleReviewer model's $2 6 . 8 9 \%$ improvement in MAE compared to individual reviewers indicates potential for automated research assessment. The inclusion of human evaluation and objective model-based evaluations provides a comprehensive assessment. The paper's exploration of ethical considerations and the implementation of Fast-DetectGPT demonstrates a responsible approach. The authors advocate for disclosure of LLM use in research, which is a positive step towards transparency.

# Weaknesses:

- The paper does not adequately address the potential for bias in the training data for both CycleResearcher and CycleReviewer. There's a risk that the models perpetuate existing biases. The paper describes the data collection process for Review-5k and Research- $^ { . 8 \mathsf { k } , }$ but lacks any discussion of potential biases within these datasets. The lack of analysis of the diversity of authors, institutions, or research topics is a significant concern.

- The paper lacks a detailed discussion on computational resources for training and deploying the framework. The use of large language models and iterative refinement processes can be computationally intensive. While the paper mentions the hardware used, it does not provide explicit training times per epoch or iteration, nor does it provide inference times.

- The paper does not sufficiently explore the potential for misuse of the framework. The paper introduces Fast-DetectGPT and discusses ethical considerations, but lacks mechanisms beyond the RL framework to guarantee the factual correctness or scientific validity of the generated content. - The paper could provide more details on the specific prompts used for the LLMs and the criteria for evaluating the quality of generated papers. The paper describes the stages of paper generation but does not provide the exact prompts used for each stage. Similarly, it mentions the criteria used by CycleReviewer, but not the specific prompts.

- The paper could benefit from a more detailed discussion of the limitations, such as the potential for generating derivative or low-quality research. It is unclear how the framework addresses the risk of converging to safe or incremental ideas.

Finally, the paper could explore the generalizability of the framework across different research domains. The current experiments seem to focus on machine learning and computer science, and it is unclear how the framework would perform in other fields.

# Suggestions:

- Implement a more rigorous analysis of training datasets for bias. Use stratified sampling or re-weighting. Explore methods for detecting and reducing bias in model outputs. Include a qualitative analysis of the generated outputs. Release training data for independent scrutiny.   
- Provide a detailed breakdown of hardware and software requirements. Explore methods for reducing the computational cost. Provide a comparison of the computational resources required. Consider providing a cloud-based deployment option.   
- Implement robust safeguards to ensure the quality and integrity of generated research outputs. Use automated quality checks, and implement a human-in-the-loop review process. Explore methods for detecting and preventing malicious use. Clearly communicate the limitations of the framework.   
- Provide a detailed breakdown of the prompts used for each stage of the research lifecycle, including examples. Clearly define evaluation criteria. Improve reproducibility and transparency.   
- Conduct a more thorough analysis of the limitations, regarding the potential for generating derivative or low-quality research. Explore methods for mitigating the risk of converging to safe or incremental ideas.   
- Investigate the generalizability of the framework across different research domains. Conduct experiments in diverse fields and analyze the performance in each domain.

# Questions:

- How does the framework handle the generation of novel research ideas that are not present in the training data? - What are the computational costs associated with training and running the CycleResearcher and CycleReviewer models? - How does the framework ensure the ethical use of generated research and prevent potential misuse? Can the framework be adapted to other research domains beyond machine learning and computer science? - What specific prompts are used to guide the LLMs in each stage of the research lifecycle? - What metrics or rubrics are used to assess the novelty, validity, and significance of the generated research?

Soundness: 3.0 3.0 3.0 Presentation:   
Contribution:   
Confidence: 5.0 Rating: 6.0

# O cial Review of Submission489 by Reviewer 7LzG

O cial Review by Reviewer 7LzG 08 Nov 2024, 17:23 (modi ed: 13 Nov 2024, 00:01) Everyone Revisions (/revisions?id=oehQnbB57h)    mechanism we developed focuses on universal academic qualities such as methodological soundness, clarity of presentation, and signi cance Summary:conte

The paper explores the use of open-source large language models to automate the entire research process, from literature review and manuscript preparation to peer review and revision. Thefor potential automation of experimental processes through code generation and results analysis. proposed framework includes CycleResearcher, which performs research tasks, and CycleReviewer, which simulates the peer review process. The study demonstrates that CycleReviewer can outperform human reviewers in predicting paper scores, and CycleResearcher can generate papers of quality close to human-written preprints. The models are trained using two new datasets,Question: The framework is primarily designed for machine learning-related research. How do you envision adapting CycleResearcher and CycleReviewer to other scienti c  elds, such Review-5k and Research-8k, which capture the complexities of peer review and research paper generation. The results indicate that this approach can signi cantly enhance the e ciency and quality of scienti c research, while also providing ethical safeguards to prevent misuse.

# Soundness: 2: fairand peer revi

# Presentation: 3: gooavailable open-

# Contribution: 2: fairaccess larger, m

# Strengths:cons

The introduction of CycleResearcher and CycleReviewer models to automate the entire research process, including literature review, manuscript preparation, peer review, and revision, is highlyfoundation for cross-domain expansion once these prerequisites are met. We welcome future collaborations with researchers from diverse  elds to explore these possibilities. Thank you innovative. This framework mimics the real-world research cycle, enhancing the e ciency and consistency of scienti c inquiry. Performance Improvement: The CycleReviewer model demonstrates aagain for your suggestions. We have revised the Limitations section and added relevant discussions! signi cant improvement in predicting paper scores, outperforming human reviewers by 26.89% in mean absolute error (MAE). This indicates that the model can provide more accurate and consistent evaluations than individual human reviewers. Quality of Generated Papers: The CycleResearcher model generates papers with an average quality close to human-written preprints, achieving anWeakness: Reward Design: The paper highlights the issue of reward de nition, where the policy model might exploit loopholes in the reward model to maximize rewards without acceptance rate of 31.07%. This shows that the model can produce high-quality research outputs that are competitive with human-generated content. Large-Scale Datasets: The development of thegenuinely improving the quality of the generated research. Review-5k and Research-8k datasets, which capture the complexities of peer review and research paper generation, provides valuable resources for training and evaluating models in academic paper generation and review.

# Weaknesses:conduc

Generalizability Across Domains: The models are primarily designed for machine learning-related research, and their generalizability to other scienti c  elds remains unexplored. This limitationreviewers (averaging 1,110 Google Scholar citations), demonstrated encouraging results in comparison to baseline systems: suggests that the framework might not perform as well in domains outside of machine learning. Reward Design: The paper highlights the issue of reward de nition, where the policy model might exploit loopholes in the reward model to maximize rewards without genuinely improving the quality of the generated research. This behavior could undermine the long-term goal of producing high-Metric CycleResearcher AI Scientist quality research outputs. Complexity of Implementation: Implementing the framework requires signi cant computational resources and expertise in reinforcement learning and LLMs. This complexityOverall Score 4.8 3.6 might be a barrier for widespread adoption, especially for smaller research teams or institutions with limited resources.

# Questions:

The framework is primarily designed for machine learning-related research. How do you envision adapting CycleResearcher and CycleReviewer to other scienti c  elds, such as biology or socialPresentation 2.8 2.6 sciences, where the nature of research and evaluation criteria might di er signi cantly? The paper mentions the potential issue of reward hacking, where the policy model might exploit loopholes inContribution 2.2 1.8 the reward model. Could you elaborate on the speci c strategies you are considering to mitigate this issue and ensure that the generated research outputs maintain high academic rigor and novelty?

Flag For Ethics Review: No ethics review needed.

Con dence: 3: You are fairly con dent in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.−   
Math/other details were not carefully checked.Response 2 ＝   
Code Of Co≡

onse 1Figure 9: The Real-world review comment for CycleResearcher ov 2024, 22:36 Everyone   nt:

# We envision several key steps for adapting our framework toO cial Review of Submission489 by Reviewer CzSX

and peer reviews from respected journals in each  eld (e.g., Nature for biology, or top social science journals). In our early research phaseO cial Review by Reviewer CzSX 06 Nov 2024, 18:28 (modi ed: 03 Dec 2024, 03:19) Everyone Revisions (/revisions?id=m1YfqmaJLl)   Summary:

The paper presents CycleResearcher and CycleReviewer, which is a cohesive system intended to make steps towards automatic scienti c discovery. In particular the novelty of the approach lies in the encapsulation of the entire research pipeline from research to review, in order to better model the entire system of research generation and get better outcomes. The authors contribute two datasets for research and review, and use these to train the system of researcher and reviewer, and evaluate them using various methods and metrics.

#

WeaknePresentation: 2: fair

genContribution: 2:

# Strengths:

acknowledge that reward hacking remains a signi cant challenge in reinforceOriginality: The idea to design both a researcher and a reviewer is novel and interesting.

conducted extensive validation through both human expert evaluation and additional experiments using separated reward models. Our human expert evaluation, conducted by experiQuality: The usage of recent preference optimization methods is a nice technical plus. The work contributes datasets to the direction of scienti c peer reviewing, which is a resource that is rather reviewers (averaging 1,110 Google Scholar cithelpful for the  eld. RL details and how they  t in is nice.

Metric CycleResearcher AI Scientisty: Figures are well-designed and artistically pleasing. Appreciate the various di erent ways that are used to evaluate the methods (qualitative, ablations, etc.)

Overall Score 4.8 3.6Signi cance: The automation of scienti c research and reviewing is a very interesting and timely topic. In particular, due to the massive increase in submissions year-to-year, progress towards the paper's direction is well appreciated.

# Weaknesses:

PresOriginality: N/A

Contribution 2.2 1.8 Quality: One big issue of the paper is the method in which the authors obtain the "ground truth" review score: "for each submission, we use the average of the other n − 1 reviewers’ scores as an estimator of the true score." In my opinion (and what feels like a general consensus in the community), it's pretty clear that this isn't the correct approach in determining a ground truth quality of a Add: Public Commenpaper. Di erent reviewers have di erent expertises and opinions, and may disagree substantially based on their backgrounds, but this is a positive quality of peer review rather than a negative one. Thus, the metric used to judge the "loss" of a review score can be used to train proxies of reviewers, sure, but it does not make sense to then take the trained system and use the same metric to −compare it against actual human reviewers. For instance, if human reviewers vary di erently based on their perspectives and CycleReviewer is just doing some "hedge" where most scores are around ＝ the median score for all papers, it might achieve better than human performance on the MAE metric that is used in the evaluation. Furthermore, focusing on the score ignores perhaps the more O cial Comment ≡ important points of paper reviewing, such as being able to highlight errors in the paper or provide advice for making changes that are adopted in future versions. I think the true objective of reviewing by Authors ( Guangsheng Bao (/pro le?id=\~Guangsheng_Bao1), Jindong Wang (/pro le?id=\~Jindong_Wang4), Minjun Zhu (/pro le?id=\~Minjun_Zhu2), Yixuan Weng (/pro le?in the paper's cycle paradigm matches these objectives more, although I recognize that they are even harder to quantify. Even so, I think the paper is overclaiming by saying that the lower MAE id=\~Yixuan_Weng1), +3 more (/group/info?id=ICLR.cc/2025/Conference/suggests that "LLMs can surpass expert-level performance in research evaluation".

  And since I don't necessarily agree with the evaluation metric for the reviewer, this casts doubt on the results for the CycleResearcher because the CycleReviewer is reviewing the CycleResearcher. Also, Comment: since CycleResearcher is optimized on CycleReviewer, then saying that CycleResearcher does better on CycleReviewer than humans or AI scientist doesn't mean much. The qualitative study in section Question: Could you elaborate on speci c4.3 is helpful to remove some of these doubts though.

further investigate the robustness of our framework. Clarity: There are a reasonable amount of typos and grammatical errors in the document. For instance, CycleReviewer is replaced with WhizeReviewer in Section 4.1. The title of section 4.1 should be Speci cally, we trained an independent reward model using only the test set portion of Review-5k on Mistral-Large-2, maintaining complete separatio"Experiments on Paper Review Generation", etc. The paper would bene t from a pass over to correct grammatical mistakes in general to make it easier to read.

new evaluation framework produced the following results: gni cance: The claims are very catchy that the system can generate better reviews and papers than humans. However, given the questionable-ness of the metric, I think these are discounted to gree

Questions:

OrigiSee Weaknesses.

With New Reward Model 3.38 Flag For Ethics Review: No ethics review needed.

However, we fully acknowledge that more work is needed to comprehensively address reward exploitation. We've added detailed discussions of these  ndings and future directions to theCon dence: 4: You are con dent in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar appendix F.2, and we siwith some pieces of related work.

ns) Figure 10: The Real-world review comment for CycleResearcher

# O cial Review of Submission489 by Reviewer GAvj

O cial Review by Reviewer GAvj 03 Nov 2024, 03:16 (modi ed: 03 Dec 2024, 04:32) Everyone Revisions (/revisions?id=zZrbn1zK3H)   Summary:

The paper introduces an iterative training framework for automatic generation and review of research papers using open-source LLMs. The core of their approach consists of two main components: 1. CycleResearcher: A policy model that generates the paper, prompted by abstracts of related work.

2. CycleReviewer: A reward model that writes several peer reviews and returns scores according to ICLR criteria.

The authors initialize these models by supervised  ne-tuning on scraped conference papers and ICLR reviews. They then improve the CycleResearcher using reinforcement learning (speci cally iterative Simple Preference Optimization, SimPO), using CycleReviewer as a reward model.

The paper claims three main contributions:

1. Development of an iterative reinforcement learning framework that mirrors the real-world research-review-revision cycle.

CycleReviewer produces scores that are closer to averages of multiple human reviewers than scores by individual human reviewers CycleResearcher-12B achieved paper quality scores surpassing preprint level and approaching accepted paper level

The paper implements some ethical safeguards: they train a model to detect papers generated by LLMs they publish; they promise to implement a licensing agreement such that downloading model weights requires sharing institutional a liations and agreeing not to use models for o cial peer reviews or submissions without disclosure.

Soundness: 2: fair

Presentation: 2: faiQ5: Human Contribution: 2: fai

Strengths:

Training LLMs with reinforcement learning on parts of the AI research process is a novel and signi cant contribution.All three experts reviewed all papers

The paper includes numerous experiments and ablations. The overall methodology is sound (with exceptions, see weaknesses).

The authors achieve strong results on the metrics they choose. It is somewhat impressive that their system achieved an acceptance rate of 31.07%, similar to ICLR 2024's acceptance rat"Excluding formatting" means ignoring layout issues (table/ gure sizing) to avoid bias from technical formatting limitations Authors use open-source models with a large range of scale (from 12B to 123B).

#

The writing is overclaiming the extent to which the paper covers the full research process. Authors write that the paper “explores performing the full cycle of automated research and review”,full codebase and logs included in our supplementary materials. We've also addressed your concerns about reward exploitation through additional independent evaluation experiments, however the paper omits crucial part of the process: actually running experiments. Instead, the authors train models to write complete papers purely from abstracts of past work, with completely                      provided more comprehensive comparison data with ICLR standards, clari ed our sampling methodology, and revised terminology throughout the paper for better accuracy (e.g., using hallucinated experiment design and results."re nement" instead of "revision"). Given I do not think that the task authors train models for — hallucinating experiment results and writing papers for them — is well motivated. Using models for this purpose will not contribute realupdates provide helpful context for understanding our work's scope and contributions. knowledge to the scienti c  eld. I think this is dual use technology, if not a completely malicious one. I could imagine the paper could be reframed to center on demonstrating this imminent failure of the reviewing system and raising an alarm, allowing the scienti c community to adapt. In current form, the paper is probably net-negative.   
Automated evaluation of papers produced by CycleResearcher is hard to trust, since CycleResearcher was trained with RL against the same reward model as used at test-time. Reward model overoptimization (Gao et al, 2022 - https://arxiv.org/abs/2210.10760 (https://arxiv.org/abs/2210.10760)) should be the expected result of RL, however the authors do not run any experiments to investigate to which extent their evaluation is in uenced by this. For example, the authors could train a held-out reward model on a held-out dataset of reviews and then evaluate CycleResearcherO cial Comment by Authors on both the reward model used for RL training and this new held-out reward model.   
The claim that CycleResearcher surpasses the quality of preprint papers and approaches quality of accepted papers is not well supported, due to the concerns about reward model overoptimization mentioned above. Human reviewers rate CycleResearcher’s papers signi cantly lower (4.8) than the automated reviewer made by the authors (5.36). The authors could have             id=\~Yixuan_Weng1), +3 more (/group/info?id=ICLR.cc/2025/Conference/Submission489/Authors)) reported the actual historical average score of ICLR2024 accepted papers.   
I have a number of concerns about the human evaluation procedure. When the authors evaluate their CycleResearcher with the AI Scientist, they seem to only use rejection sampling (best of N) for CycleResearcher. This is not a fair comparison. Overall, human evaluation is conducted on a small scale (10 papers total, three human reviewers, 2 methods: this paper and baseline)Dear Reviewer GAvj, I do not think 30min per review (including reading, writing comments & providing scores) is enough!As the discussion period is coming to an end soon, we wanted to check if you have had a chance to re I think it’s misleading to use the term “revision” for parameters updates of the policy model (Figure 2). The paper refers to this revision as part of the full research process (“Research-Rebuttal-addressed - we are happy to provide any additional clari cation needed. Thank you for your time!

Revision”) but this does not actually involve revision of papers based on reviews.

# Questions:

1. What exactly are the prompts, based on which CycleResearcher generates papers during evaluations?   
2. Why do smaller CycleResearcher models get better scores in the evaluation?   
3. How many samples in automated evaluation?   
4. Please include the average real score of accepted papers given by human ICLR2024 reviewers.   
5. How do you compute the acceptance rates, e.g. one mentioned in line 128?Replying to O cial Comment by Authors   
6. For human evaluation: 1. Please report the N used in best-of-N / rejection sampling.O cial Comment by Reviewer GAvj 2. Please clarify whether each paper is evaluated by one or several humans.O cial Comment by Reviewer GAvj 03 Dec 2024, 04:33 Everyon  3. How are the human experts chosen?Comment: 4. What do you mean by saying “excluding formatting considerations” in the assessment, and why is it omitted?Thanks, I've raised my score.

# Flag For Ethics Review: Yes,

# Details Of Ethics Concerns:

I do not think that the task authors train models for — hallucinating experiment results and writing papers for them — is well motivated. Using models for this purpose will not contribute real knowledge to the scienti c  eld. I think this is dual use technology, if not a completely malicious one. I could imagine the paper could be reframed to center on demonstrating this imminent failure ofReplying to O cial Comment by Reviewer GAvj− the reviewing system and raising an alarm, allowing the scienti c community to adapt. In current form, the paper is probably net-negative. I think the results from this paper should be known to the       ≡ broad public, but not in the current framing.Thank you for your recognit

Con dence: 4: You are con dent in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar             id=\~Yixuan_Weng1), +3 more (/group/info?id=ICLR.cc/2025/Conference/Submission489/Authors)) with some pieces of related work.

# Add: Public Comme−Figure 11: The Real-world review comment for CycleResearcherOn behalf of all authors, I would like to express our profound gratitude for your and all reviewers' detailed review and thoughtful suggestions! Your professional reviews and insightful suggestions have enhanced the CycleResearcher project comprehensively. Each reviewer has demonstrated admirable academic rigor and forwar

# I do not think that the task authors train models for — hallucO cial Review of Submission489 by Reviewer 5wHA

O cial Review by Reviewer 5wHA 01 Nov 2024, 11:36 (modi ed: 25 Nov 2024, 03:18) Everyone Revisions (/revisions?id=VfLBrP3ExO)   Sum

We deeply appreciate your critical feedback regarding the scope and ethical implications of our work. Let me address your concerns comprehensively: The authors introduce two core components: CycleResearcher, a policy model that autonomously performs research tasks, and CycleReviewer, a reward model that simulates the peer review process. Experimental results suggest that CycleReviewer can outperform individual human reviewers in scoring consistency, and CycleResearcher shows promise in generating research papers that approach the quality of human-written preprints.

rebuttal pSoundness: 3: good

experiments thPresentation: 4: excellent

detailedContribution: 3: go

Valuable Datasets: The introduction of the Review-5k and Research-8k datasets could be highly bene cial to the research community. These datasets provide resources for training and evaluating models in academic paper generation and review, potentially fostering further advancements in automated research tools.

nnovative Use of Preference Data: Utilizing preference data to iteratively train the CycleResearcher model is an interesting approach. This method allows the model to improve over multipl terations, aligning more closely with human standards through reinforcement learning.

Ethical Safeguards: The inclusion of a detection model to identify AI-generated papers addresses ethical concerns related to the misuse of automated research tools. By implementing such safeguards, the authors demonstrate a commitment to responsible AI deployment.

Automation of the Research Lifecycle: The paper attempts to automate the full research cycle, from idea generation to peer review and revision. This holistic approach is ambitious and, if success could signi cantly impact the e ciency of scienti c research.

# Weaknesses:

Quality of Generated Papers: Upon examining the samples provided in the Appendix (Sections E.1 and E.2), it is evident that the generated papers contain hallucinations and inaccuracies. For instance, in the generated abstracts, there are claims of outperforming state-of-the-art methods without substantial evidence or appropriate citations. This raises concerns about the reliability of the CycleResearcher model in producing high-quality, factual research papers.

Counterintuitive Results with Model Scaling: In Table 3 (Section 4.2), the CycleResearcher-12B model achieves a higher acceptance rate than the larger 72B and 123B models. This is counterintuitive, as larger models typically perform better due to increased capacity. The paper does not provide su cient analysis or explanations for this phenomenon, leaving readers questioning the scalability and e cacy of the approach.

Insu cient Ethical Considerations: While the authors mention the implementation of a detection tool for AI-generated papers, the paper lacks a deep exploration of the ethical implications of automating research. Issues such as accountability, potential misuse, and the impact on the scienti c community are not thoroughly addressed. A dedicated discussion in the Ethics Considerations section would strengthen the paper.

# Questions:

Explanation for Performance of Smaller Models: In Table 3, why does the CycleResearcher-12B model receive the highest acceptance rate compared to the 72B and 123B models? This result is unexpected given that larger models generally have better performance. Could the authors provide an analysis of this outcome, possibly including case studies or error analysis to understand the limitations of larger models in this context?

Evaluation Stability of CycleReviewer: What is the temperature setting used for the CycleReviewer during evaluation? Additionally, have the authors experimented with running the CycleReviewer multiple times to assess the variability or deviation in the review scores and feedback? Understanding the stability and consistency of the CycleReviewer is important for gauging its reliability in the automated review process.

Addressing Hallucinations in Generated Papers: Given the observed hallucinations and inaccuracies in the sample generated papers (Appendix E), what strategies do the authors propose to mitigate these issues? Are there mechanisms in place to fact-check or verify the content produced by the CycleResearcher before it is submitted for automated review?

Flag For Ethics Review: Yes, Discrimination / bias / fairness concerns, Yes, Privacy, security and safety

Details Of Ethics Concerns:

Accountability and Authorship: If AI systems generate research papers, questions arise regarding authorship and accountability for the content. It's essential to clarify who is responsible for th work produced and how credit should be assigned.

Quality and Integrity of Research: The presence of hallucinations and factual inaccuracies in AI-generated papers could undermine the integrity of scienti c literature. There is a risk of disseminating false information, which could have downstream e ects if other researchers build upon  awed results.

Misuse of Technology: The tools developed could be misused to generate large volumes of low-quality or misleading research, potentially cluttering academic discourse and making it harder identify valuable contributions.

Impact on the Research Community: Automation might a ect the roles of researchers, peer reviewers, and the collaborative nature of scienti c inquiry. There is a need to consider how these technologies will coexist with human e orts and what support structures are necessary to ensure they augment rather than hinder scienti c progress.

Rating: 8: accept, good paper

Con dence: 5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully. Code Of Conduct: Yes

Add: Public CommenFigure 12: The Real-world review comment for CycleResearcher