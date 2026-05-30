---
pdf: REMOR_Automated_Peer_Review_Generation_with_LLM_Reasoning_2505.11718.pdf
source: MinerU API
batch_id: d6e8dbb5-b049-4ed8-8c56-40ee66b039f6
data_id: REMOR_Automated_Peer_Review_Generation_with_LLM_Reasoning_2505.11718
parsed_at: 2026-05-23
---

# REMOR: Automated Peer Review Generation with LLM Reasoning and Multi-Objective Reinforcement Learning

Pawin Taechoyotin1 Daniel Acuna1,2,3

pawin.taechoyotin@colorado.edu daniel.acuna@colorado.edu

1Department of Computer Science, University of Colorado Boulder 2Department of Information Science, University of Colorado Boulder 3ReviewerZero AI Inc., Boulder, CO

## Abstract

AI-based peer review systems tend to produce shallow and overpraising suggestions compared to human feedback. Here, we evaluate how well a reasoning LLM trained with multi-objective reinforcement learning (REMOR) can overcome these limitations. We start by designing a multi-aspect reward function that aligns with human evaluation of reviews. The aspects are related to the review itself (e.g., criticisms, novelty) and the relationship between the review and the manuscript (i.e., relevance). First, we perform supervised fine-tuning of DeepSeek-R1-Distill-Qwen-7B using LoRA on PeerRT, a new dataset of high-quality top AI conference reviews enriched with reasoning traces. We then apply Group Relative Policy Optimization (GRPO) to train two models: REMOR-H (with the human-aligned reward) and REMOR-U (with a uniform reward). Interestingly, the human-aligned reward penalizes aspects typically associated with strong reviews, leading REMOR-U to produce qualitatively more substantive feedback. Our results show that REMOR-U and REMOR-H achieve more than twice the average rewards of human reviews, non-reasoning state-of-the-art agentic multi-modal AI review systems, and general commercial LLM baselines. We found that while the best AI and human reviews are comparable in quality, REMOR avoids the long tail of low-quality human reviews. We discuss how reasoning is key to achieving these improvements and release the Human-aligned Peer Review Reward (HPRR) function, the Peer Review Reasoning-enriched Traces (PeerRT) dataset, and the REMOR models, which we believe can help spur progress in the area.

## 1 Introduction

Scientific peer review seeks to guide modern science by assessing manuscripts across multiple aspects, including novelty, methodological rigor, and potential impact [17, 24]. Typically, manuscripts are evaluated by multiple reviewers to capture diverse perspectives and provide authors with thorough feedback [31]. Such varied assessments can ideally offer authors fresh insights into their work, helping them address potential weaknesses. Ultimately, peer review aspires to identify research that genuinely matters to the broader scientific community, though achieving this goal consistently remains challenging.

There are multiple problems with the scientific peer review that could be improved. The process tends to linger too long, the reviewers have biases against certain topics, and other scientists [14, 29]. Other problems include the lack of incentive to review, low review panel diversity, and small expert availability [11, 34]. With the exponential increase in submissions across science, these issues are exacerbated, creating "reviewer fatigue" for experts [4]. Less-experienced reviewers end up writing reports with unhelpful feedback [16, 10]. The scientific community needs to experiment with new ways of scaling high-quality scientific peer review.

In recent years, Large Language Models (LLMs) have demonstrated remarkable capabilities in understanding and generating text. The models perform well in text summarization, question answering, coding, and more [35, 49]. It is only natural that these capabilities can translate into automating peer review. Recent work has shown how useful LLMs can be for this task (e.g., [20, 9, 41, 54]). The advances have been encouraging, but similar failures keep appearing across models and systems, calling for improvements.

Issues with current AI review generation systems The first issue concerns the depth of the review. It has been found that the generated comments overpraise the work, are too generic, and overlook details [47, 6]. The second issue involves formalizing and operationalizing what a good peer review should be. Currently, there have been many studies on the components of an ideal peer review [43, 39, 33, 40], but the metrics have not been operationalized for AI. On the other hand, many frameworks have been proposed for evaluating a manuscript and producing the peer review [18, 9, 53], but have the limitations of requiring human oversight. Therefore, the issues revolve around depth, operationalized human-aligned evaluation, and effective automation.

In this work, we propose REMOR (AI-Generated Peer Reviews through Reasoning and Multi-Objective Reinforcement Learning). Figure 1 shows a diagram outlining our work. REMOR is a framework that uses reasoning and a multi-objective reward strategy. The reasoning is meant to increase the depth of the review. The multi-objective part is meant to operationalize what a good review should look like. We begin with a model fine-tuned on a novel dataset we call the Peer Review Reasoning-enriched Traces (PeerRT). The fine-tuning step enables the model to learn domain-specific language styles and common review structures. We then perform Reinforcement Learning (RL) with GRPO using a new reward function aligned to human preferences across multiple aspects of review quality, including detailed criticisms, tangible examples, importance-based prioritization, and well-grounded suggestions. We call this function Human-Aligned Peer Review Reward (HPRR). We develop two models, one that uses human-aligned human preferences (REMOR-H) and another that is uniform (REMOR-U). We quantitatively and qualitatively show that the reviews generated by REMOR achieve twice as high rewards as those generated by humans and other agentic and non-agentic systems. In sum, our work provides the following contributions:

• PeerRT: An enriched dataset of peer reviews with reasoning traces and metrics in each aspect.

• Human-aligned Peer Review Reward (HPRR): An operationalized metric for RL that quantifies the quality of peer review feedback.

• REMOR: An LLM reasoning model that specializes in peer review.

• A comparison of multiple non-reasoning, agentic, and general reasoning models against REMOR-U and REMOR-H

• A qualitative analysis of reviews generated by REMOR.

## 2 Related Work

## 2.1 Non-reasoning AI-based Peer Review Generation Systems

Automated scientific review generation has seen significant advancements in recent years thanks to LLMs [47, 2, 44, 22, 9, 41]. It has been shown that LLMs are highly capable but contain limitations such as a lack of personalization, context-awareness, and subtle critiques often found in human feedback [20]. Potential biases also exist within the models, such as overpraising the work and providing shallow suggestions. There have been promising efforts in mitigating these limitations, such as engineering system prompts to add personalization and structure to the review [20]. Currently, the most promising systems are based on a panel of AI agents. In [9], the authors created sets of agents that focus on different parts of the review, such as experiment quality, overall clarity, and work impact, with later sets of agents refining the feedback. In the recent work of [41], the authors used multiple agents with large context windows, each attending to different aspects of the article, such as novelty, impact, and figures (the model was multi-modal), with an "area chair" agent that condensed the suggestions. The authors show that the large context windows of current models, their multi-modality, and their ability to call external tools significantly improved review quality.

![](images/b0e1b603b8e6cb8e25ba2232df3ad08394cb0bdd0a028b04d24a5f2efb91bd60.jpg)  
Figure 1: Illustrative diagram of how REMOR works. A. AI-review generation system with our proposed multi-dimensional reward function (HPRR), which evaluates the quality of the peer review. A sample review is shown and color-coded to indicate the relevance between the analysis metric and the review. For this instance, purple indicates content related to praise, and blue is content related to criticism. B. The training is performed on a dataset (PeerRT) comprising the manuscripts, human peer review, and synthetic thinking traces. The base model is first trained via supervised fine-tuning (SFT) and later by GRPO with a multi-dimensional reward function. Finally, we use human-aligned weights to create a linear combination of the multi-dimensional reward for GRPO.

One downside of AI agent panels is that they take excessively long to coordinate and exchange contextual information. In the recent work of [41, 9], the agents spend 20 minutes or more creating the review, using millions of tokens, many of them solely for coordinating. In contrast, non-agent systems take significantly less (e.g., less than 1 minute in [20]). Still, agentic systems are perceived as significantly better than human reviews and non-agentic systems [41].

## 2.2 Evaluating peer review generation systems

Evaluating the quality of generated peer reviews is complex and subjective. In [9], the authors used a survey asking humans to determine whether the comments were relevant. In [41], the authors created an arena-style match system to ask humans to choose between pairs of AI-generated reviews. The same quality evaluation issues that plague human reviews also affect AI: it is challenging to develop guidelines.

Other work has sought to automate parts of the evaluation system. Similar to how LLMs are evaluated for other tasks, scientists have used translation quality metrics such as ROUGE [21], BERTScore [48], and METEOR [1] to assess how closely the reviews discuss topics present in the manuscript or align with human-generated reviews. Automated evaluations can also use LLMs themselves as LLM-as-judge [51] or even use an LLM to address the applicability and relevance of suggestions [18, 9]. A more systematic approach to evaluating AI-generated peer review was proposed by [18]. In such a study, the authors suggest an evaluation that focuses on evaluating comparisons with human reviews, factual accuracy, analytical depth, and actionable insights. The goal is to detect superficial critiques, hallucinations, and next-step feedback.

The overall issue with evaluation is that most methods assume a human review is available. As AI systems improve, good-quality human reviews to continue guiding AI are scarce. One possibility is to take principles of a good review and create an automated evaluation based on them. If we use such an automated method, we could drive a system to achieve "superhuman" performance, optimizing a review along all the aspects of what is considered a desirable review.

## 2.3 Reasoning, Reinforcement Learning, and GRPO

Chain-of-Thought Prompting showed a remarkable ability to improve the performance of existing systems [45]. Through this experience, the idea of building "chains of thought" directly in the generation resulted in "reasoning" models. Reasoning systems have become increasingly dominant in LLM leaderboards (e.g., top places in llmarena.ai [7]). One of the first applications of this idea was in GPT-3 where human feedback was used to train a reward model that reinforcement learning can use. This technique is called Reinforcement Learning with Human Feedback (RLHF) [8]. RLHF can be used to generate models that go beyond next-token generation. For example, it can generate instruction-following GPTs [27].

Early reasoning ideas relied on explicit differentiable reward models [32, 37], such as Proximal Policy Optimization (PPO). In other words, the reward model needed to be a neural network used appropriately by reinforcement learning. However, these models are hard to define and optimize. In [36], the authors proposed a novel method for reinforcement learning that did not require an explicit model. The method proved to improve memory usage and performance of training LLMs with reinforcement learning. The method is called Group Relative Policy Optimization (GRPO). Importantly, this technique only needs the reward values of generation traces to optimize the underlying policy, which is much more flexible.

## 3 Reasoning and Reinforcement Learning for Automated Peer Review Generation

Our current work uses recent developments in reasoning LLMs. In particular, we use supervised fine-tuning on high-quality reviews (in the spirit of [25]), followed by a multi-objective reinforcement step that tries to mimic what humans like in a review. We now review the datasets used and later describe the method.

## 3.1 Peer review datasets and models

## 3.1.1 Data curation

We base our dataset on readily available review data from ICLR 2017-2020 [43, 15]. The dataset contains 16.8K reviews across 5.5K submissions. We augmented the data with the full text of each paper in OpenReview. The full text is extracted from a PDF file using GROBID [23, 30]. Additionally, we augmented the reviews with reasoning traces generated from Claude Sonnet 3.7 extended thinking model. The thinking trace is meant to force the supervised fine-tuned (SFT) model to generate thinking traces. We call this final dataset the Peer Review Reasoning-enriched Traces (PeerRT). The prompt templates are in the Appendix C.

## 3.1.2 Models

We use the Claude Sonnet 3.7 extended thinking model as a base, large and proprietary LLM model, and DeepSeek-R1 (7B distillation) [13] model to compare against. We further use the DeepSeek-R1

model during the supervised-fine-tuning (SFT) and reinforcement learning via group relative policy optimization (GRPO) phases.

## 3.1.3 Reward Model

Our reward model combines a sentence-level review assessment model and a relevance score between the generated review and the reviewed manuscript. The sentence-level review assessment is based on the work of [33]. It evaluates a sentence along several aspects of what a review should contain: criticism, example, importance and relevance, materials and methods, presentation and reporting, results and discussion, suggestion and solution. We normalize each aspect by the number of sentences in the review. To measure the review’s relevance to the manuscript, we use the METEOR score between the review and the manuscript’s text [1]. The final reward is the weighted sum of the eight normalized quality metrics and METEOR.

## 3.2 Multi-objective reinforcement learning

Because our reward model contains multiple aspects, we must combine them to make them usable within GRPO. There are multiple methods for achieving this combination. In this article, we use a weighted sum of the rewards to achieve a multi-objective reinforcement learning (MORL) that is Pareto-optimal [5, 19, 50]. The first weighted structure is Uniform (U). The second weighted structure is called Human-aligned weights (H), where the values are computed from the human preferences in [41]. The basic idea is to boost aspects that humans prefer when comparing reviews (see below for details).

## 3.2.1 Obtaining reward weights from human preferences

Here we detail how to find the weights of the human-aligned reward. We use the dataset of human preferences described in [41], which results from an arena-style competition across multiple human and AI-generated reviews. In particular, for a paper $p$ and a reviewer k, we have pairs of reviews review and revie $\mathrm { w } _ { b }$ from two systems and the user vote of whether $" \mathbf { A }$ is better than ${ \mathrm { ~ B ~ } } " , ~ { \mathrm { ~ } } ^ { \prime } { \mathrm { B } }$ is better than $\mathbf { A } " .$ , or $" \mathbf { A }$ is equal to $\mathbf { B } "$ . In this task, "better" was defined as having "overall" higher quality. We compute the set of dimensions of the reward system based on 3.1.3 as covariates and use a Bradley-Terry (BT) Model [3] and two other variations to understand how to weigh each review aspect to maximize the predictive accuracy. We now explain these models:

Adapted Bradley-Terry Model (ABT) The adapted Bradley-Terry Model explicitly models ties as a three-outcome regression. We further constrained the weights to be positive. (In the standard BT analysis, we found that some weights were negative, which is not qualitatively sensible [3])

Constrained Reward Model (CRM) This model is similar to ABT, where an L1 regularization on the weights is applied to avoid overfitting (see Appendix B.1).

After obtaining the weights from each algorithm, we scale them with a min-max scaler and reweigh them to add up to nine. To avoid an aspect being discarded in our Multi-objective Reinforcement Learning, we apply Laplace smoothing with $\alpha = 0 . 0 1$ . The unadjusted weights can be found in Appendix B.

## 4 Experimental results

## 4.1 Experimental Setup

All training was performed on a single virtual server with 64 vCPUs, 256 GB of RAM, and 2 NVIDIA A100 80GB GPUs. Our preliminary results show that training on high-quality samples results in the best performance. The selection is done by computing each sample’s uniform reward (3.1.3) and selecting the samples with a score above the 90th percentile. The selected samples are used for supervised fine-tuning (SFT) and reinforcement learning via Group Relative Policy Optimization (GRPO). The code and dataset links are in Appendix E and D.

## 4.1.1 Software setup

We used DeepSpeed [28] with LLaMA-Factory [52] and TRL to train our models. DeepSpeed enables splitting optimizer states of the model across multiple heterogeneous devices. This enabled the training of LLMs to a broader population with limited computing resources. Essentially, it enables training of LLMs that do not fit within a single GPU to be trained across multiple GPUs. In most cases, it also enables scientists to train LLMs using multiple smaller GPUs instead of just a single large GPU. Supervised fine-tuning may outperform test-timing reasoning, given enough computational resources [38].

## 4.1.2 Supervised fine-tuning

To simplify supervised fine-tuning (SFT), we use LLaMA-Factory [52]. LLaMA-Factory is a unified framework that provides tools and implementation of techniques to finetune LLMs efficiently. We trained DeepSeek-R1-Qwen-Distilled-7B via LoRA with rank = 8, cutoff length = 32,768, gradient accumulation steps = 4, learning rate = 0.0001 for three epochs. The training time on 1.7k samples is approximately 6.5 hours.

## 4.1.3 Multi-objective RL + GRPO

Due to LLaMA-Factory not supporting GRPO, we used the TRL software package to perform multi-objective reinforcement learning with GRPO on our LLMs. The parameters used for training are generations = 4, max prompt length = 12,288, max completion length = 4096, device batch size = 4, gradient accumulation steps = 1, and temperature = 0.9 for one epoch. The other non-specified parameters are kept at their default value. The training time on 1.7k samples was approximately 100 hours for one epoch. The 1.7k samples and the aforementioned parameters resulted in 864 total optimization steps.

## 4.2 Human-aligned reward vs. uniform rewards

We estimate the best weights with various algorithms as described in section 3.2.1. The Adapted Bradly-Terry obtained the best five-fold cross-validation performance for predicting human preferences (Appendix Table 3). The results indicate that humans mostly favor "Importance and Relevance", "Suggestions and Solution", and "Relevance" (METEOR) with a weight of 0.11, 0.16, and 8.67, respectively. Other metrics were irrelevant, with a weight of 0.01 (the Laplace smoothing parameter). The final human-aligned weights can be found in Appendix B, Table 3.

## 4.3 Reasoning model results

The performance of all models is shown in Figure 2. We have included the average score across different metrics for each model and the uniform and human-aligned weighted reward. The pretrained model DeepSeek-R1 (DS) has the lowest total rewards at 1.317 and 0.283 for uniform reward and human-aligned reward, respectively. With supervised fine-tuning, the DeepSeek-R1 model improved dramatically and outperformed both Sonnet 3.7 and human reviewers in uniform reward but slightly underperformed with human-aligned reward. After applying reinforcement learning with GRPO to the SFT model, the performance drastically improved once more. In this instance, both GRPO model variants outperformed humans and Sonnet 3.7 by a significant margin. The model DeepSeek-R1, which was trained with the uniform reward, is called REMOR-U. This model had the highest uniform reward at 3.884. The model DeepSeek-R1, which was trained with the human-aligned reward, is called REMOR-H. For obvious reasons, REMOR-H loses to REMOR-U regarding uniform reward but has the highest human-aligned reward at 0.670. A variance analysis across metrics shows that REMOR-U can excel at multiple metrics simultaneously, while other models only focus on one metric at a time (Figure 2). A distribution analysis of the uniform reward shows that on average REMOR-U has a higher score than human reviews (see Appendix Figure 6).

## 4.4 Learning Curve For GRPO

Figure 3 shows the average reward across each metric. The left and right panel show the improvement for REMOR-U and REMOR-H, respectively. The reward improvement trend of REMOR-U gives us insight into the difficulty of improving each metric. We can divide the metrics into groups: hard, moderate, and easy. The hard difficulty has a peak reward at 0.1. The moderate difficulty has a peak reward within the range of 0.4 to 0.6. The easy difficulty has a peak at 0.8. This insight can lead to a normalization scheme for each metric in future studies that factor in the different nature of each metric. The relevance METEOR metric is an example where a score of 1.0 is not ideal since that requires the review to be excessively long to contain all the contents within the manuscript. The relevance METEOR is in the hard difficulty group.

presentation and reporting results and discussion suggestions and solution relevance METEOR  
![](images/59ec9c9c122870142a5d0d29e74c74f884d68dee15a2d9d87bbfa79f8b08ccbc.jpg)  
Figure 2: The left panel shows the average reward across the metrics for each model. We can see that REMOR-U has the top reward across all metrics and has the second highest score in METEOR. The middle and right panels show each model’s total uniform and human-aligned reward. REMOR-U significantly outperforms all models in total uniform reward. For total human-aligned reward, REMOR-H has the highest score. All values had a SEM within the range of 0.001. (See Table 4 for full results in the Appendix.)

![](images/71b1b3bd366c36ab36f0c8c58bdf7a38bc8374d24f0b654948f949b0bab1248d.jpg)

![](images/ffdbd1c3de03967c427ef16acb668e2b630665e79a4600f43d9350b0f952cc07.jpg)  
Figure 3: Reward for each aspect per each optimization step. The left panel depicts the reward trend for all metrics of REMOR-U; the right panel depicts the reward trend for all metrics of REMOR-H. The vertical axis depicts the reward value from 0 to 1. The horizontal axis depicts the optimization step.

## 4.5 Non-reasoning, agentic systems for peer review generation

We benchmark REMOR with other peer-review generation systems using papers from various conferences. The results are shown in Figure 4. Both variants of REMOR significantly outperformed human reviewers, all non-reasoning model systems, and other reasoning models in terms of uniform and human-aligned reward. REMOR-U had the highest average uniform reward at 3.292. REMOR-H has the highest average human-aligned reward at 1.438. REMOR-U also has the highest average score in "criticism", "example", "importance and relevance", "praise", "presentation and reporting", "result and discussion", "suggestion and solution" with a score of 0.273, 0.105, 0.422, 0.466, 0.306,

0.468, and 0.456 respectively. Interestingly, "materials and methods" of REMOR-H has a higher score than "importance and relevance," even though "importance and relevance" has around 10 times higher weight value. Additionally, the results in Figure 4 indicate that reasoning models outperform non-reasoning agentic AI systems such as MARG-S [9] and MAMORX [41].

![](images/30164fa987c41c5bb2bff5827a8debd2e3205f307f673d19312c08ad343160d2.jpg)

![](images/3985dc49f481b6fdceeb725ae5a6d40b2544ccd0a7280f5c6640f07cc5b1a238.jpg)  
Figure 4: The comparison shows that REMOR outperforms non-reasoning models across all metrics. The left panel shows that REMOR-U has the highest scores across metrics compared to other models. The middle and the right panel show that REMOR outperforms all models in uniform reward and human-aligned reward. All values had a SEM within the range of 0.001. (Full results in Appendix Table 5)

## 4.6 Variance analysis

We wanted to understand how robustly REMOR-U, the best model, produced the reward. Maybe it produced high reward with high variance, making it unreliable. We performed a normalized mean and variance analysis and found that REMOR has both the highest mean and lowest variance in rewards. This should lead to more consistent review outcomes (Figure 5).

![](images/4d8f31ef5078cdae4f7b795b05b7134a850b440723be27a7f9c85a59801249a1.jpg)

![](images/51dfd167aeccbbcc8810a961d26dd7384999e53da26101442555f88617d2bd42.jpg)  
Figure 5: The left panel shows the normalized mean across metrics. We can see the REMOR-U significantly outperforms other systems, while the fine-tuned model (DS SFT) is the second best, with half the score of REMOR-U. The right panel shows the variance across the metrics. The chart shows that REMOR-U has very low variance. Overall, REMOR-U has the highest mean and lowest variance across metrics, which indicates it is the best-performing model.

## 4.7 Qualitative Analysis

We qualitatively analyze the reviews to assess differences between our REMOR models. We found that the highest-reward human and REMOR-U reviews contain high-quality comments that contribute to the improvement of the paper (e.g., "The paper is well written but...", "There is a lack of explanation in section 3.1 ...". Sample reviews can be found in (Appendix Table 6). The comments provided by REMOR-U are direct and concise. Figure 4 shows that REMOR-U and REMOR-H should be similar quantitatively. However, we found that REMOR-H reviews tend to be too long and redundant. We believe this is caused by an excessive focus on the METEOR reward component, which attempts to align the review produced with the manuscript. Even though the comments are similar to REMOR-U, the review as a whole is difficult to understand. Therefore, we judge REMOR-U as qualitatively better than REMOR-H. Overall, we found that a higher uniform reward correlates with higher-quality reviews. Future studies should confirm this with a human comparison to reinforce this claim.

## 5 Discussion

In this article, we explore how reasoning models can help improve AI-generated reviews. We develop a multi-aspect reward function that feeds into Reinforcement Learning with GRPO. Once fine-tuning and RL GRPO are in place, the performance of the model in regards to multi-aspect reward function increased dramatically, showing that RL GRPO can surpass human performance for our tasks.

We found that human preferences do not favor criticism despite multiple guidelines encouraging this type of feedback [17]. We believe this is because criticism is perceived as a net negative [26]. In contrast, humans prefer the "importance and relevance" aspect because they consider it crucial that novelty and impact assessment are part of a review [42, 12]. A similar pattern is found for the "suggestion and solution" aspect. Lastly, we think "relevance" (METEOR) is highly favored because the comments directly relate to the work. Also, relevancy is a standard metric found in previous studies regarding peer review [46, 20, 9]. Thus, there can be significant differences between human preferences and the principles of a good peer review.

We found that general reasoning models (non-finetuned) performed comparably to multi-agentic review generation systems. However, with the addition of RL GRPO, the specialized reasoning models substantially outperform complex agentic systems like MARG-S [9] and MAMORX [41]. A byproduct of this new architecture comes in processing time. Agentic systems are notoriously slow (approximately 20 - 30 minutes [41]) compared to REMOR (approximately 1 minute). Thus, a reasoning model with simple prompts is a promising alternative to augmenting the peer review process with LLMs.

Overall, our results show that reasoning in automated review generation systems leads to excellent performance improvements. We found that our training scheme effectively used the reasoning traces that allowed it to optimize multiple metrics simultaneously. Our system achieves better performance than other systems that use even more information, such as MAMORX [41], which uses figures and external knowledge. Notably, while other systems appear to be doing reasoning in the form of chain-of-thought and multi-agent coordination (e.g., [9]), it is not the type of modern reasoning used today. We also show how synthetic rewards can be effective for GRPO and training these systems.

## 6 Limitations and Future work

There are limitations in our study. Our set of reviews is narrow, and we are not using other modalities such as citations or figures. Previous studies have connected to external knowledge and multi-modality [41], but we did not include this information. Furthermore, we could only support a limited context window, potentially leading to incomplete manuscript analysis or the impossibility of including raw external knowledge within the prompt. Also, our human-aligned reward model is based on a relatively small sample of votes. Finally, our evaluation is not based on direct human feedback but on a constructed human-aligned reward function. Therefore, a true blinded human evaluation by experts should confirm our findings. We believe these shortcomings are addressable, which we will do in future work.

## 7 Conclusion

In this work, we demonstrated that explicit reasoning combined with multi-objective reinforcement learning significantly enhances the depth and quality of automated peer review generation. By incorporating detailed, aspect-based reward signals, REMOR produced feedback that achieves approximately double the Human-aligned Peer Review Reward (HPRR) of typical human reviews, approaching parity with the best-quality human-generated reviews. Our proposed human-aligned reward function can also serve as a self-assessment tool for reviewers, encouraging more detailed and relevant feedback. To facilitate continued research, we release the PeerRT dataset enriched with reasoning traces, the HPRR evaluation metric, and our trained REMOR models. Future work will extend REMOR to incorporate multimodal information, such as figures and external references, and evaluate its applicability across broader scientific disciplines.

## References

[1] Satanjeev Banerjee and Alon Lavie. Meteor: An automatic metric for mt evaluation with improved correlation with human judgments. In Proceedings of the acl workshop on intrinsic and extrinsic evaluation measures for machine translation and/or summarization, pages 65–72, 2005.

[2] Alberto Bartoli, Andrea De Lorenzo, Eric Medvet, and Fabiano Tarlao. Your paper has been accepted, rejected, or whatever: Automatic generation of scientific paper reviews. In Availability, Reliability, and Security in Information Systems: IFIP WG 8.4, 8.9, TC 5 International Cross-Domain Conference, CD-ARES 2016, and Workshop on Privacy Aware Machine Learning for Health Data Science, PAML 2016, Salzburg, Austria, August 31-September 2, 2016, Proceedings, pages 19–28. Springer, 2016.

[3] Ralph Allan Bradley and Milton E. Terry. Rank analysis of incomplete block designs: I. the method of paired comparisons. Biometrika, 39(3/4):324–345, 1952. ISSN 00063444, 14643510. URL http://www.jstor.org/stable/2334029.

[4] Marijke Breuning, Jeremy Backstrom, Jeremy Brannon, Benjamin Isaak Gross, and Michael Widmeier. Reviewer fatigue? why scholars decline to review their peers’ work. PS: Political Science & Politics, 48(4):595–600, 2015.

[5] Andrea Castelletti, Francesca Pianosi, and Marcello Restelli. A multiobjective reinforcement learning approach to water resources systems operation: Pareto frontier approximation in a single run. Water Resources Research, 49(6):3476–3486, 2013.

[6] A Checco, L Bracciale, P Loreti, S Pinfield, and G Bianchi. Ai-assisted peer review. humanities and social sciences communications, 8 (1), 1-11, 2021.

[7] Wei-Lin Chiang, Lianmin Zheng, Ying Sheng, Anastasios Nikolas Angelopoulos, Tianle Li, Dacheng Li, Banghua Zhu, Hao Zhang, Michael Jordan, Joseph E Gonzalez, et al. Chatbot arena: An open platform for evaluating llms by human preference. In Forty-first International Conference on Machine Learning, 2024.

[8] Paul F Christiano, Jan Leike, Tom Brown, Miljan Martic, Shane Legg, and Dario Amodei. Deep reinforcement learning from human preferences. Advances in neural information processing systems, 30, 2017.

[9] Mike D’Arcy, Tom Hope, Larry Birnbaum, and Doug Downey. Marg: Multi-agent review generation for scientific papers. arXiv preprint arXiv:2401.04259, 2024.

[10] Rafael D’Andrea and James P O’Dwyer. Can editors save peer review from peer reviewers? PloS one, 12(10):e0186111, 2017.

[11] Nady El-Guebaly, John Foster, Anees Bahji, and Matilda Hellman. The critical role of peer reviewers: Challenges and future steps. Nordic Studies on Alcohol and Drugs, 40(1):14–21, 2023.

[12] Stephen Gallo, Lisa Thompson, Karen Schmaling, and Scott Glisson. Risk evaluation in peer review of grant applications. Environment Systems and Decisions, 38:216–229, 2018.

[13] Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong Ma, Peiyi Wang, Xiao Bi, et al. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning. arXiv preprint arXiv:2501.12948, 2025.

[14] Cigdem Kadaifci, Erkan Isikli, and Y Ilker Topcu. Fundamental problems in the peer-review process and stakeholders’ perceptions of potential suggestions for improvement. Learned Publishing, 38(1):e1637, 2025.

[15] Dongyeop Kang, Waleed Ammar, Bhavana Dalvi, Madeleine Van Zuylen, Sebastian Kohlmeier, Eduard Hovy, and Roy Schwartz. A dataset of peer reviews (peerread): Collection, insights and nlp applications. arXiv preprint arXiv:1804.09635, 2018.

[16] Ingvar Karlberg. On peer review–the cornerstone of scientific publication, 2015.

[17] Jacalyn Kelly, Tara Sadeghieh, and Khosrow Adeli. Peer review in scientific publications: benefits, critiques, & a survival guide. Ejifcc, 25(3):227, 2014.

[18] Chhavi Kirtani, Madhav Krishan Garg, Tejash Prasad, Tanmay Singhal, Murari Mandal, and Dhruv Kumar. Revieweval: An evaluation framework for ai-generated reviews. arXiv preprint arXiv:2502.11736, 2025.

[19] Kaiwen Li, Tao Zhang, and Rui Wang. Deep reinforcement learning for multiobjective optimization. IEEE transactions on cybernetics, 51(6):3103–3114, 2020.

[20] Weixin Liang, Yuhui Zhang, Hancheng Cao, Binglu Wang, Daisy Yi Ding, Xinyu Yang, Kailas Vodrahalli, Siyu He, Daniel Scott Smith, Yian Yin, et al. Can large language models provide useful feedback on research papers? a large-scale empirical analysis. NEJM AI, 1(8): AIoa2400196, 2024.

[21] Chin-Yew Lin. Rouge: A package for automatic evaluation of summaries. In Text summarization branches out, pages 74–81, 2004.

[22] Ryan Liu and Nihar B Shah. Reviewergpt? an exploratory study on using large language models for paper reviewing. arXiv preprint arXiv:2306.00622, 2023.

[23] Patrice Lopez. Grobid: Combining automatic bibliographic data recognition and term extraction for scholarship publications. In International conference on theory and practice of digital libraries, pages 473–474. Springer, 2009.

[24] Christopher P Morley and Sam Grammer. Now more than ever: reflections on the state and importance of peer review. PRiMER: Peer-review reports in medical education research, 5:36, 2021.

[25] Niklas Muennighoff, Zitong Yang, Weijia Shi, Xiang Lisa Li, Li Fei-Fei, Hannaneh Hajishirzi, Luke Zettlemoyer, Percy Liang, Emmanuel Candès, and Tatsunori Hashimoto. s1: Simple test-time scaling. arXiv preprint arXiv:2501.19393, 2025.

[26] Syavash Nobarany and Kellogg S Booth. Use of politeness strategies in signed open peer review. Journal of the Association for Information Science and Technology, 66(5):1048–1064, 2015.

[27] Long Ouyang, Jeffrey Wu, Xu Jiang, Diogo Almeida, Carroll Wainwright, Pamela Mishkin, Chong Zhang, Sandhini Agarwal, Katarina Slama, Alex Ray, John Schulman, Jacob Hilton, Fraser Kelton, Luke Miller, Maddie Simens, Amanda Askell, Peter Welinder, Paul F Christiano, Jan Leike, and Ryan Lowe. Training language models to follow instructions with human feedback. In S. Koyejo, S. Mohamed, A. Agarwal, D. Belgrave, K. Cho, and A. Oh, editors, Advances in Neural Information Processing Systems, volume 35, pages 27730–27744. Curran Associates, Inc., 2022. URL https://proceedings.neurips.cc/paper\_files/paper/ 2022/file/b1efde53be364a73914f58805a001731-Paper-Conference.pdf.

[28] Samyam Rajbhandari, Jeff Rasley, Olatunji Ruwase, and Yuxiong He. Zero: Memory optimizations toward training trillion parameter models. In SC20: International Conference for High Performance Computing, Networking, Storage and Analysis, pages 1–16. IEEE, 2020.

[29] David B Resnik, Christina Gutierrez-Ford, and Shyamal Peddada. Perceptions of ethical problems with scientific journal peer review: an exploratory study. Science and engineering ethics, 14:305–310, 2008.

[30] Laurent Romary and Patrice Lopez. Grobid-information extraction from scientific publications. ERCIM News, 100, 2015.

[31] Abu-Ubaida Sani. Journal peer review: Meaning, types, and processes. Journal Peer Review: Meaning, 2023.

[32] John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347, 2017.

[33] Anna Severin, Michaela Strinzel, Matthias Egger, Tiago Barros, Alexander Sokolov, Julia Vilstrup Mouatt, and Stefan Müller. Relationship between journal impact factor and the thoroughness and helpfulness of peer reviews. PLOS Biology, 21(8):1–18, 08 2023. doi: 10.1371/journal. pbio.3002238. URL https://doi.org/10.1371/journal.pbio.3002238.

[34] Nihar B Shah. Challenges, experiments, and computational solutions in peer review. Communications of the ACM, 65(6):76–87, 2022.

[35] Minghao Shao, Abdul Basit, Ramesh Karri, and Muhammad Shafique. Survey of different large language model architectures: Trends, benchmarks, and challenges. IEEE Access, 2024.

[36] Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Xiao Bi, Haowei Zhang, Mingchuan Zhang, YK Li, Y Wu, et al. Deepseekmath: Pushing the limits of mathematical reasoning in open language models. arXiv preprint arXiv:2402.03300, 2024.

[37] David Silver, Julian Schrittwieser, Karen Simonyan, Ioannis Antonoglou, Aja Huang, Arthur Guez, Thomas Hubert, Lucas Baker, Matthew Lai, Adrian Bolton, et al. Mastering the game of go without human knowledge. nature, 550(7676):354–359, 2017.

[38] Charlie Snell, Jaehoon Lee, Kelvin Xu, and Aviral Kumar. Scaling llm test-time compute optimally can be more effective than scaling model parameters, 2024. URL https://arxiv. org/abs/2408.03314.

[39] Cecilia Superchi, José Antonio González, Ivan Solà, Erik Cobo, Darko Hren, and Isabelle Boutron. Tools used to assess the quality of peer review reports: a methodological systematic review. BMC Medical Research Methodology, 19(1):48, Mar 2019. ISSN 1471-2288. doi: 10.1186/s12874-019-0688-x. URL https://doi.org/10.1186/s12874-019-0688-x.

[40] Cecilia Superchi, Darko Hren, David Blanco, Roser Rius, Alessandro Recchioni, Isabelle Boutron, and José Antonio González. Development of arcadia: a tool for assessing the quality of peer-review reports in biomedical research. BMJ Open, 10(6), 2020. ISSN 2044-6055. doi: 10.1136/bmjopen-2019-035604. URL https://bmjopen.bmj.com/content/10/6/ e035604.

[41] Pawin Taechoyotin, Guanchao Wang, Tong Zeng, Bradley Sides, and Daniel Acuna. Mamorx: Multi-agent multi-modal scientific review generation with external knowledge. In Neurips 2024 Workshop Foundation Models for Science: Progress, Opportunities, and Challenges, 2024.

[42] Misha Teplitskiy, Hao Peng, Andrea Blasco, and Karim R Lakhani. Is novel research worth doing? evidence from peer review at 49 journals. Proceedings of the National Academy of Sciences, 119(47):e2118046119, 2022.

[43] Gang Wang, Qi Peng, Yanfeng Zhang, and Mingyang Zhang. What have we learned from openreview? World Wide Web, 26(2):683–708, Mar 2023. ISSN 1573-1413. doi: 10.1007/ s11280-022-01109-z. URL https://doi.org/10.1007/s11280-022-01109-z.

[44] Qingyun Wang, Qi Zeng, Lifu Huang, Kevin Knight, Heng Ji, and Nazneen Fatema Rajani. Reviewrobot: Explainable paper review generation based on knowledge synthesis. arXiv preprint arXiv:2010.06119, 2020.

[45] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, brian ichter, Fei Xia, Ed Chi, Quoc V Le, and Denny Zhou. Chain-of-thought prompting elicits reasoning in large language models. In S. Koyejo, S. Mohamed, A. Agarwal, D. Belgrave, K. Cho, and A. Oh, editors, Advances in Neural Information Processing Systems, volume 35, pages 24824–24837. Curran Associates, Inc., 2022. URL https://proceedings.neurips.cc/paper\_files/paper/ 2022/file/9d5609613524ecf4f15af0f7b31abca4-Paper-Conference.pdf.

[46] Christie Wilcox. Rude reviews are pervasive and sometimes harmful, study finds. Science, 366 (6472):1433–1433, 2019.

[47] Weizhe Yuan, Pengfei Liu, and Graham Neubig. Can we automate scientific reviewing? Journal of Artificial Intelligence Research, 75:171–212, 2022.

[48] Tianyi Zhang, Varsha Kishore, Felix Wu, Kilian Q Weinberger, and Yoav Artzi. Bertscore: Evaluating text generation with bert. arXiv preprint arXiv:1904.09675, 2019.

[49] Tianyi Zhang, Faisal Ladhak, Esin Durmus, Percy Liang, Kathleen McKeown, and Tatsunori B Hashimoto. Benchmarking large language models for news summarization. Transactions of the Association for Computational Linguistics, 12:39–57, 2024.

[50] Youming Zhang. A novel multi-objective deep q-network: Addressing immediate and delayed rewards in multi-objective q-learning. IEEE Access, 12:144932–144949, 2024.

[51] Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu, Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric Xing, et al. Judging llm-as-a-judge with mt-bench and chatbot arena. Advances in Neural Information Processing Systems, 36:46595–46623, 2023.

[52] Yaowei Zheng, Richong Zhang, Junhao Zhang, Yanhan Ye, Zheyan Luo, Zhangchi Feng, and Yongqiang Ma. Llamafactory: Unified efficient fine-tuning of 100+ language models. In Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 3: System Demonstrations), Bangkok, Thailand, 2024. Association for Computational Linguistics. URL http://arxiv.org/abs/2403.13372.

[53] Ruiyang Zhou, Lu Chen, and Kai Yu. Is llm a reliable reviewer? a comprehensive evaluation of llm on automatic paper reviewing tasks. In Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024), pages 9340–9351, 2024.

[54] Zhenzhen Zhuang, Jiandong Chen, Hongfeng Xu, Yuwen Jiang, and Jialiang Lin. Large language models for automated scholarly paper review: A survey. arXiv preprint arXiv:2501.10326, 2025.

## A Metric names

Throughout the Appendix, we will use the following short names for each metric: criticism (Cr), example (Ex), importance and relevance (ImRe), materials and methods (MaMe), praise (Pr), presentation and reporting (PrRe), results and discussion (ReDi), and suggestion and solution (SuSo). The "relevance METEOR" score short name is ReME. The short names are meant to improve the ease of displaying results in tables.

## B Human values weights calculation

This section includes the details for calculating the human-aligned weights and intermediate weights that have not been adjusted.

## B.1 Constrained Reward Model (CRM)

The Constrained Reward Model (CRM) is formulated as a constrained problem where convex optimization techniques are applied to find the human-aligned weights. We define c as the weights, d as the number of metrics (e.g. Cr, Ex, ImRe, etc.) , $s _ { x }$ as the reward score for review x:

Let $c \in \mathbb { R } ^ { d }$ , where d = number\_of\_metrics.

$$
\sum _ { i = 1 } ^ { d } c _ { i }
$$

minimize

subject to $c _ { i } \geq 0 \quad \forall i \in \{ 1 , \ldots , d \}$

$$
\sum _ { i = 1 } ^ { d } c _ { i } \leq 1
$$

$$
\sum _ { i = 1 } ^ { d } c _ { i } \geq 0
$$

For each match (a, b) in dataset:

$$
s _ { a } = \sum _ { i = 1 } ^ { d } c _ { i } a _ { i } , \quad s _ { b } = \sum _ { i = 1 } ^ { d } c _ { i } b _ { i }
$$

where $a _ { i }$ and $b _ { i }$ are the covariates of reviews A and B, respectively

Constraints based on match outcome:

If the match is labeled as "A is better than $\mathbf { B } " : s _ { a } \geq s _ { b } + \varepsilon$

If the match is labeled as "B is better than ${ \mathrm { A } } " : s _ { a } \leq s _ { b } + \varepsilon$

If the match is labeled as "A is equal to $\mathbf { B } " : s _ { a } = s _ { b }$

where $\varepsilon = 1 0 ^ { - 1 2 }$ is a small positive constant to ensure numerical stability for strict inequalities.

## C Prompt Templates

## C.1 User Message prompt for Supervised Fine Tuning and Reinforcement Learning

The following template is used as the user message prompt.

II II "I

You are a member of the scientific community tasked with peer review.   
Review the following paper content.

\### Paper Content

Table 1: Unadjusted human-aligned weights from each algorithm. F1 is the average F1 score computed from performing cross-validation.
<table><tr><td rowspan=1 colspan=11>Model                   Cr   Ex   ImRe MaMe Pr   PrRe ReDi SuSo ReME F1</td></tr><tr><td rowspan=1 colspan=11>Bradley-Terry</td></tr><tr><td rowspan=1 colspan=1>Logistic Regression</td><td rowspan=1 colspan=1>-0.20</td><td rowspan=1 colspan=1>-0.74</td><td rowspan=1 colspan=1>-0.14</td><td rowspan=1 colspan=1>0.22</td><td rowspan=1 colspan=1>-0.11</td><td rowspan=1 colspan=1>0.05</td><td rowspan=1 colspan=1>-0.05</td><td rowspan=1 colspan=1>0.54</td><td rowspan=1 colspan=1>1.21</td><td rowspan=1 colspan=1>0.43</td></tr><tr><td rowspan=1 colspan=1>Logistic RegressionCross Validation</td><td rowspan=1 colspan=1>-0.04</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.22</td><td rowspan=1 colspan=1>0.40</td></tr><tr><td rowspan=1 colspan=11>Adapted Bradley-Terry</td></tr><tr><td rowspan=1 colspan=1>Linear Regression</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.23</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.33</td><td rowspan=1 colspan=1>19.09</td><td rowspan=1 colspan=1>0.55</td></tr><tr><td rowspan=1 colspan=1>Linear RegressionScaled</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.03</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.06</td><td rowspan=1 colspan=1>0.47</td><td rowspan=1 colspan=1>0.08</td></tr><tr><td rowspan=1 colspan=11>Optimization Problem</td></tr><tr><td rowspan=1 colspan=1>without L1 regularization</td><td rowspan=1 colspan=1>0.79</td><td rowspan=1 colspan=1>0.38</td><td rowspan=1 colspan=1>0.26</td><td rowspan=1 colspan=1>0.05</td><td rowspan=1 colspan=1>0.06</td><td rowspan=1 colspan=1>-0.24</td><td rowspan=1 colspan=1>0.15</td><td rowspan=1 colspan=1>0.30</td><td rowspan=1 colspan=1>2.27</td><td rowspan=1 colspan=1>0.36</td></tr><tr><td rowspan=1 colspan=1>with L1 regularization</td><td rowspan=1 colspan=1>0.49</td><td rowspan=1 colspan=1>0.27</td><td rowspan=1 colspan=1>0.20</td><td rowspan=1 colspan=1>0.02</td><td rowspan=1 colspan=1>0.03</td><td rowspan=1 colspan=1>-0.16</td><td rowspan=1 colspan=1>0.05</td><td rowspan=1 colspan=1>0.22</td><td rowspan=1 colspan=1>1.55</td><td rowspan=1 colspan=1>0.39</td></tr></table>

Table 2: Human values weights adjusted as strictly positive values. F1 is the average F1 score computed from performing cross validation.
<table><tr><td rowspan=1 colspan=11>Model                    Cr  Ex  ImRe MaMe Pr  PrRe ReDi SuSo ReME F1</td></tr><tr><td rowspan=1 colspan=11>Bradley-Terry</td></tr><tr><td rowspan=1 colspan=1>Logistic Regression</td><td rowspan=1 colspan=1>0.66</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.73</td><td rowspan=1 colspan=1>1.16</td><td rowspan=1 colspan=1>0.77</td><td rowspan=1 colspan=1>0.95</td><td rowspan=1 colspan=1>0.83</td><td rowspan=1 colspan=1>1.54</td><td rowspan=1 colspan=1>2.35</td><td rowspan=1 colspan=1>0.33</td></tr><tr><td rowspan=1 colspan=1>Logistic RegressionCross Validation</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.61</td><td rowspan=1 colspan=1>1.03</td><td rowspan=1 colspan=1>0.67</td><td rowspan=1 colspan=1>0.67</td><td rowspan=1 colspan=1>0.67</td><td rowspan=1 colspan=1>0.67</td><td rowspan=1 colspan=1>0.67</td><td rowspan=1 colspan=1>3.99</td><td rowspan=1 colspan=1>0.41</td></tr><tr><td rowspan=1 colspan=11>Adapted Bradley-Terry</td></tr><tr><td rowspan=1 colspan=1>Linear Regression</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.10</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.15</td><td rowspan=1 colspan=1>8.74</td><td rowspan=1 colspan=1>0.55</td></tr><tr><td rowspan=1 colspan=1>Linear RegressionScaled</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.53</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.99</td><td rowspan=1 colspan=1>7.49</td><td rowspan=1 colspan=1>0.47</td></tr><tr><td rowspan=1 colspan=11>Optimization Problem</td></tr><tr><td rowspan=1 colspan=1>without L1 regularization</td><td rowspan=1 colspan=1>1.50</td><td rowspan=1 colspan=1>0.91</td><td rowspan=1 colspan=1>0.73</td><td rowspan=1 colspan=1>0.42</td><td rowspan=1 colspan=1>0.43</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.57</td><td rowspan=1 colspan=1>0.79</td><td rowspan=1 colspan=1>3.65</td><td rowspan=1 colspan=1>0.46</td></tr><tr><td rowspan=1 colspan=1>with L1 regularization</td><td rowspan=1 colspan=1>1.42</td><td rowspan=1 colspan=1>0.94</td><td rowspan=1 colspan=1>0.80</td><td rowspan=1 colspan=1>0.40</td><td rowspan=1 colspan=1>0.42</td><td rowspan=1 colspan=1>0.00</td><td rowspan=1 colspan=1>0.46</td><td rowspan=1 colspan=1>0.83</td><td rowspan=1 colspan=1>3.73</td><td rowspan=1 colspan=1>0.44</td></tr></table>

Table 3: Human values adjusted as positive weights and applied Laplace smoothing. F1 CV is the average F1 score computed from performing 5-fold cross validation on 130 samples.
<table><tr><td rowspan=1 colspan=1>Model</td><td rowspan=1 colspan=2>Cr  Ex</td><td rowspan=1 colspan=1>ImRe</td><td rowspan=1 colspan=7>MaMe Pr  PrRe ReDi SuSo ReME F1</td></tr><tr><td rowspan=1 colspan=11>Bradley-Terry</td></tr><tr><td rowspan=1 colspan=1>Logistic Regression</td><td rowspan=1 colspan=1>0.66</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.73</td><td rowspan=1 colspan=1>1.16</td><td rowspan=1 colspan=1>0.77</td><td rowspan=1 colspan=1>0.96</td><td rowspan=1 colspan=1>0.84</td><td rowspan=1 colspan=1>1.54</td><td rowspan=1 colspan=1>2.34</td><td rowspan=1 colspan=1>0.33</td></tr><tr><td rowspan=1 colspan=1>Logistic RegressionCross Validation</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.62</td><td rowspan=1 colspan=1>1.02</td><td rowspan=1 colspan=1>0.68</td><td rowspan=1 colspan=1>0.68</td><td rowspan=1 colspan=1>0.68</td><td rowspan=1 colspan=1>0.68</td><td rowspan=1 colspan=1>0.68</td><td rowspan=1 colspan=1>3.96</td><td rowspan=1 colspan=1>0.41</td></tr><tr><td rowspan=1 colspan=11>Adapted Bradley-Terry</td></tr><tr><td rowspan=1 colspan=1>Linear Regression</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.11</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.16</td><td rowspan=1 colspan=1>8.67</td><td rowspan=1 colspan=1>0.57</td></tr><tr><td rowspan=1 colspan=1>Linear RegressionScaled</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.53</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.99</td><td rowspan=1 colspan=1>7.42</td><td rowspan=1 colspan=1>0.47</td></tr><tr><td rowspan=1 colspan=11>Optimization Problem</td></tr><tr><td rowspan=1 colspan=1>without L1 regularization</td><td rowspan=1 colspan=1>1.50</td><td rowspan=1 colspan=1>0.91</td><td rowspan=1 colspan=1>0.73</td><td rowspan=1 colspan=1>0.43</td><td rowspan=1 colspan=1>0.44</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.57</td><td rowspan=1 colspan=1>0.79</td><td rowspan=1 colspan=1>3.63</td><td rowspan=1 colspan=1>0.46</td></tr><tr><td rowspan=1 colspan=1>with L1 regularization</td><td rowspan=1 colspan=1>1.41</td><td rowspan=1 colspan=1>0.94</td><td rowspan=1 colspan=1>0.80</td><td rowspan=1 colspan=1>0.40</td><td rowspan=1 colspan=1>0.42</td><td rowspan=1 colspan=1>0.01</td><td rowspan=1 colspan=1>0.47</td><td rowspan=1 colspan=1>0.83</td><td rowspan=1 colspan=1>3.70</td><td rowspan=1 colspan=1>0.44</td></tr></table>

{paper\_content}   
" II "II

## C.2 Assistant Prompts for Supervised Fine Tuning

The following template is used as the target response from the LLM.

```twig
<think> {thinking traces from Sonnet 3.7} </think>
```

{review content}   
I II II

## D Models and Dataset

The trained models and datasets will be publicly available at huggingface.co. Below is the list of resources:

## Models

• SFT on 16k reviews: pawin205/Qwen-7B-Review-ICLR-sft

• SFT on 90th Percentile reviews: pawin205/Qwen-7B-Review-ICLR-90th-sft

• GRPO Uniform (REMOR-U): pawin205/Qwen-7B-Review-ICLR-GRPO-U

• GRPO Human-aligned (REMOR-H): pawin205/Qwen-7B-Review-ICLR-GRPO-H

## Dataset

• PeerRT: ICLR 2017-2020 Reviews augmented with thinking traces, full text, and metric scores: pawin205/iclr-2017-2020-peer-review-with-thinking-trace

• ICLR 2017-2020 Reviews with just title and abstract with metric scores: pawin205/paperreview-pair

• ICLR 2017-2020 Reviews with just title, abstract, and static thinking traces with metric scores: pawin205/paper-review-pair-reason

## E Code Repository

All scripts to process data can be found at REPOSITORY. This includes example scripts to load the dataset as well as loading models and perform text generation.

## F Model performance across different metrics

This section includes the performance of each model in tabular form.

Table 4: Metric-wise average reward comparison between Human, Sonnet 3.7, Deepseek and REMOR. Scores are calculated from 5.5k papers. All values had a SEM within the range of 0.001.
<table><tr><td rowspan=1 colspan=1>Model</td><td rowspan=1 colspan=1>Cr</td><td rowspan=1 colspan=1>Ex</td><td rowspan=1 colspan=1>ImRe</td><td rowspan=1 colspan=1>MaMe</td><td rowspan=1 colspan=1>Pr</td><td rowspan=1 colspan=1>PrRe</td><td rowspan=1 colspan=1>ReDi</td><td rowspan=1 colspan=1>SuSo</td><td rowspan=1 colspan=1>ReME</td><td rowspan=1 colspan=1>Reward(U)</td><td rowspan=1 colspan=1>Reward(H)</td></tr><tr><td rowspan=1 colspan=1>Human</td><td rowspan=1 colspan=1>0.212</td><td rowspan=1 colspan=1>0.051</td><td rowspan=1 colspan=1>0.118</td><td rowspan=1 colspan=1>0.558</td><td rowspan=1 colspan=1>0.129</td><td rowspan=1 colspan=1>0.189</td><td rowspan=1 colspan=1>0.193</td><td rowspan=1 colspan=1>0.175</td><td rowspan=1 colspan=1>0.026</td><td rowspan=1 colspan=1>1.654</td><td rowspan=1 colspan=1>0.285</td></tr><tr><td rowspan=1 colspan=1>Sonnet 3.7</td><td rowspan=1 colspan=1>0.058</td><td rowspan=1 colspan=1>0.010</td><td rowspan=1 colspan=1>0.210</td><td rowspan=1 colspan=1>0.515</td><td rowspan=1 colspan=1>0.224</td><td rowspan=1 colspan=1>0.050</td><td rowspan=1 colspan=1>0.179</td><td rowspan=1 colspan=1>0.161</td><td rowspan=1 colspan=1>0.037</td><td rowspan=1 colspan=1>1.445</td><td rowspan=1 colspan=1>0.384</td></tr><tr><td rowspan=1 colspan=1>DS [13]</td><td rowspan=1 colspan=1>0.026</td><td rowspan=1 colspan=1>0.009</td><td rowspan=1 colspan=1>0.154</td><td rowspan=1 colspan=1>0.646</td><td rowspan=1 colspan=1>0.116</td><td rowspan=1 colspan=1>0.041</td><td rowspan=1 colspan=1>0.225</td><td rowspan=1 colspan=1>0.073</td><td rowspan=1 colspan=1>0.028</td><td rowspan=1 colspan=1>1.317</td><td rowspan=1 colspan=1>0.283</td></tr><tr><td rowspan=1 colspan=1>DS SFT</td><td rowspan=1 colspan=1>0.231</td><td rowspan=1 colspan=1>0.053</td><td rowspan=1 colspan=1>0.277</td><td rowspan=1 colspan=1>0.776</td><td rowspan=1 colspan=1>0.263</td><td rowspan=1 colspan=1>0.164</td><td rowspan=1 colspan=1>0.330</td><td rowspan=1 colspan=1>0.233</td><td rowspan=1 colspan=1>0.022</td><td rowspan=1 colspan=1>2.349</td><td rowspan=1 colspan=1>0.276</td></tr><tr><td rowspan=1 colspan=1>REMOR-U</td><td rowspan=1 colspan=1>0.310</td><td rowspan=1 colspan=1>0.112</td><td rowspan=1 colspan=1>0.564</td><td rowspan=1 colspan=1>0.794</td><td rowspan=1 colspan=1>0.605</td><td rowspan=1 colspan=1>0.322</td><td rowspan=1 colspan=1>0.594</td><td rowspan=1 colspan=1>0.548</td><td rowspan=1 colspan=1>0.034</td><td rowspan=1 colspan=1>3.884</td><td rowspan=1 colspan=1>0.470</td></tr><tr><td rowspan=1 colspan=1>REMOR-H</td><td rowspan=1 colspan=1>0.169</td><td rowspan=1 colspan=1>0.041</td><td rowspan=1 colspan=1>0.380</td><td rowspan=1 colspan=1>0.780</td><td rowspan=1 colspan=1>0.333</td><td rowspan=1 colspan=1>0.144</td><td rowspan=1 colspan=1>0.327</td><td rowspan=1 colspan=1>0.378</td><td rowspan=1 colspan=1>0.063</td><td rowspan=1 colspan=1>2.614</td><td rowspan=1 colspan=1>0.670</td></tr></table>

Table 5: Performance comparison with previous systems over multiple papers from ACL 2017 and NeurIPS 2019
<table><tr><td>Model</td><td>Cr</td><td>Ex</td><td>ImRe</td><td>MaMe</td><td>Pr</td><td>PrRe</td><td>ReDi</td><td>SuSo</td><td>ReME</td><td>Reward (U)</td><td>Reward (H)</td></tr><tr><td>Human Reviewer</td><td>0.161</td><td>0.072</td><td>0.116</td><td>0.440</td><td>0.244</td><td>0.335</td><td>0.174</td><td>0.191</td><td>0.029</td><td>1.762</td><td>0.306</td></tr><tr><td colspan="10">Non-reasoning models</td></tr><tr><td>Barebones</td><td>0.047</td><td>0.006</td><td>0.209</td><td>0.459</td><td>0.307</td><td>0.179</td><td>0.213</td><td>0.257</td><td>0.022</td><td>1.700</td><td>0.269</td></tr><tr><td>Liang et al [20]</td><td>0.157</td><td>0.000</td><td>0.037</td><td>0.374</td><td>0.000</td><td>0.030</td><td>0.150</td><td>0.220</td><td>0.009</td><td>0.978</td><td>0.128</td></tr><tr><td>MARG-S [9]</td><td>0.027</td><td>0.019</td><td>0.264</td><td>0.500</td><td>0.221</td><td>00.139</td><td>0.160</td><td>0.234</td><td>0.050</td><td>1.615</td><td>0.514</td></tr><tr><td>MAMORX [41]</td><td>0.054</td><td>0.024</td><td>0.229</td><td>0.527</td><td>0.184</td><td>0.201</td><td>0.123</td><td>0.250</td><td>0..067</td><td>1.658</td><td>0.658</td></tr><tr><td colspan="10"></td></tr><tr><td>Explicit reasoning models</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>Sonnet 3.7</td><td>0.049</td><td>0.004</td><td>0.200</td><td>0.492</td><td>0.222</td><td>0.111</td><td>0.150</td><td>0.177</td><td>0.039</td><td>1.443</td><td>0.398</td></tr><tr><td>DeepSeek  [13]</td><td>0.031</td><td>0.017</td><td>0.174</td><td>0.688</td><td>0.143 0.187</td><td>0.181 0.211</td><td>0.189 0.194</td><td>0.138 0.214</td><td>0.055</td><td>1.616</td><td>0.529</td></tr><tr><td>DS SFT REMOR-U</td><td>0.163 0.273</td><td>0.043 0.105</td><td>0.201 0.422</td><td>0.694 0.728</td><td>0.466</td><td>0.306</td><td>0468</td><td>0.456</td><td>0.047 0.068</td><td>1.953 3.292</td><td>0.478</td></tr><tr><td>REMOR-H</td><td>0.152</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>00.731</td></tr><tr><td></td><td></td><td>0.032</td><td>0.370</td><td>0.747</td><td>0.333</td><td>0.249</td><td>0.255</td><td>0.376</td><td>0.152</td><td>2.667</td><td>1.438</td></tr></table>

![](images/9e2507d546b80e3665ba9880d3be91424a3232c575cfa6fbd173a29604203e21.jpg)  
Figure 6: A distribution of Reward (U) of human and REMOR-U reviews. The plot shows that REMOR-U reviews mostly have higher uniform reward than the average human reviews. It should be noted that human reviews with a uniform reward of four exist, but in very small numbers.

## G Sample review comparison between humans and REMOR

This section shows sample reviews from papers with a high contrast between human reviewers and REMOR. Table 6 contains the sampled reviews.

Table 6: Qualitative comparison of reviews with high aspect reward but low METEOR score against low aspect reward but high METEOR score
<table><tr><td rowspan=1 colspan=2>Sample Reviews from Humans and REMOR</td></tr><tr><td rowspan=1 colspan=2>↑ Human (U) ↓ REMOR-U</td></tr><tr><td rowspan=1 colspan=1>+ An interesting idea to learn the hidden state evolution and the state-observationmapping jointly + The experiments on Euler*s equation are slightly better thanResNet for 30 steps ahead forecasting in terms of MSE + The paper is clearly writtenand well-explained - The model is not new: ResNet for state evolution and Conv-Deconv for state-observation mapping - The difference between ResNet and theproposed framework is not significant, ResNet is even better in Figure 2 - Missing animportant experiment: test whether the model can generalize, that is to forecast ondifferent initial conditions than the training dataset - How does the model comparewith GANs (Y. Xie* , E. Franz* and M. Chu* and N. Thuereyy, &quot;tempoGAN: ATemporally Coherent, Volumetric GAN for Super-resolution Fluid Flow&quot;)?</td><td rowspan=1 colspan=1>This paper presents a novel approach called Flow-Flow Estimation with SystematicTeacher Forcing (FST) for predicting velocity fields using both physical principlesand learned controls. The authors propose FST-Accurate ODE (FST-Accurate OD ) as a practical extension of the original FST method, with improved numericalstability when applied to flows.The paper is well-written, but I have some concerns about clarity: - Some sectionsfeel like they could be more concise or provide clearer explanations - The tablesare dense with detailed results and would benefit from better organization - A briefexplanation of the different velocity field types (NSV, NSV, TVF) in Table 1 wouldhelp readers understand what they&#x27;re measuringThe results appear promising for fluid simulations: - Their FST model outperformsbaseline approaches by 26% at average MSE per time-step and by 83% for velocityfields - The approach seems particularly valuable when working with small timesteps(10 or fewer steps), but performs poorly on larger horizons.The paper makes a valuable contribution to the field of fluid simulations, providing anew method that can be applied in various contexts. ….</td></tr><tr><td rowspan=1 colspan=1>↓ Human (U)</td><td rowspan=1 colspan=1>↑ REMOR-U</td></tr><tr><td rowspan=1 colspan=1>GraphNVP is the first paper to introduce the concept of *invertible flow*, thatis to construct the invertible mapping from latent vector z to the graph G. Byconstructing the mapping from G to z, GraphNVP first changes the discrete featurevector into continuous variables, then update this matrix representation by scalingand transforming functions (Eq. (2)-(5) in this GRF paper). In each iteration thematrix is only updated by one row (one slice for the tensor), while keep other rowsintact. Then for constructing the inverse mapping, we can first sample a randomvector and then apply the &quot;inverse&quot; of the update rule to recover the edge matrix andnode matrix respectively..</td><td rowspan=1 colspan=1>The paper is well written but has several issues which I will now point out: - Thetheoretical results in Section 3.1 are interesting, however they are quite hard to parsesince there is a lack of an explanation for some terms and it*s not clear what the finalresult is (e.g., Theorem 1). It would be useful to provide more intuitive explanationsor examples on how these can be applied - The experiments could have been betterorganized with clearer descriptions, as the experimental section was quite confusing- The authors should explain in greater detail why the experimental results showthat GRF has lower variance than other methods (this is stated several times butexplained briefly) - While I am not convinced by the results on ZINC-250k datasetwhich is not very challenging compared to QM9, the results are interesting and couldbe interesting for further research directions.</td></tr><tr><td rowspan=1 colspan=1>↑ Human (H)</td><td rowspan=1 colspan=1>↓ REMOR-H</td></tr><tr><td rowspan=1 colspan=1>The paper considers the problem of out-of-distribution (OOD) sample detectionwhile solving a classification task. The authors tackle the problem of OOD detectionwith exploiting uncertainty while passing a test sample through the neural network.They treat outputs of (some) layers in a NN as random Gaussian-distributed variablesand measure uncertainty as variance of these Gaussians. Then when uncertainty ishigh, OOD is detected. The overall idea behind the paper could be interesting, but itsrealization in the current form is questionable. The paper seems totally misusing thereparameterization trick and stochastic outputs of layers in NNs. Eq. (2) is not theobjective of variational inference that seems to be required for stochastic outputs andthe reparameterization trick as presented before the equation. The objective missesthe KL-divergence term! Without it what would stop a neural net to set sigmasto 0 and forget about the stochasticity altogether? Not to mention that the currentobjective is not mathematically justified. …</td><td rowspan=1 colspan=1>The problem addressed here is interesting and has high practical importance, but themethod proposed seems to be somewhat incremental, without being able to showmuch improvements on all datasets, and it requires more extensive experiments withdifferent models and datasets than what have been presented so far (though some ofthem are provided as a part of the paper). The quality of writing is also quite poor insome parts.</td></tr><tr><td rowspan=1 colspan=1>↓ Human (H)</td><td rowspan=1 colspan=1>↑ REMOR-H</td></tr><tr><td rowspan=1 colspan=1>Summary: The paper proposes a simple technique to address the problem introducedby Adebayo et al. that several saliency approaches do not pass sanity checks. Theproposed approach computes the saliency maps for allthe classes and removes thepixels that play a role in predicting several classes. Strengths: 1. Simple and intuitiveapproach. 2. Well written and easy to read paper. 3. The introduced approachmakes Grad.Input pass the sanity checks introduced by Adebayo et al. Weaknesses:Fo  tepability tnqu, pass he ny e s  mu, buubecause a saliency technique passes the sanity checks, it doesn&#x27;t mean that thesemaps explain the network&#x27;s decision well. 2. Lack of any quantitative evaluation(such as localization or pointing experiment) of their approach. 3. Failure to showif the resultant maps are class-discriminative. Show performance on images withmultiple classes. 4...</td><td rowspan=1 colspan=1>This paper discusses a relatively simple modification to existing methods that helpssaliency maps pass sanity checks proposed by Adebayo et al., 2018. The approach isinteresting, and the idea of using competition among labels seems to make sense inorder to remove features which are deemed irrelevant or coincidental by humans. Itis well written paper discussing an interesting modification and its effect on existingmethods (but not really a novel method), which I think should be published aftermore analysis and experimentation would have been possible, such as comparisonwith other existing approaches for saliency evaluation. However the modificationsintroduced here seem to work wellin practice. The experimental results are promisingalthough some of them could be better explained by the theory presented earlier inthe paper (section 4). Overall I think this is a solid submission that addresses aninteresting topic, though I feel it would be more interesting with a more theoreticaljustification for why the method works and comparison to other existing approachesfor saliency evaluation. ...</td></tr></table>