---
pdf: Towards_Reasoning_in_LLMs_via_Multi_Agent_Peer_Review_2311.08152.pdf
source: MinerU API
batch_id: d6e8dbb5-b049-4ed8-8c56-40ee66b039f6
data_id: Towards_Reasoning_in_LLMs_via_Multi_Agent_Peer_Review_2311.08152
parsed_at: 2026-05-23
---

# Towards Reasoning in Large Language Models via Multi-Agent Peer Review Collaboration

Zhenran Xu1, Senbao Shi1, Baotian Hu1∗, Jindi Yu1, Dongfang Li1, Min Zhang1, Yuxiang Wu2

1Harbin Institute of Technology (Shenzhen) 2University College London

xuzhenran@stu.hit.edu.cn, shisenbaohit@gmail.com

{hubaotian, zhangmin2021}@hit.edu.cn

22S051013@stu.hit.edu.cn, crazyofapple@gmail.com, yuxiang.wu@cs.ucl.ac.uk

## Abstract

Large Language Models (LLMs) have shown remarkable capabilities in general natural lan guage processing tasks but often fall short in complex reasoning tasks. Recent studies have explored human-like problem-solving strategies, such as self-correct, to push further the boundary of single-model reasoning ability. In this work, we let a single model “step outside the box” by engaging multiple models to correct each other. We introduce a multi-agent collaboration strategy that emulates the academic peer review process. Each agent independently constructs its own solution, provides reviews on the solutions of others, and assigns confidence levels to its reviews. Upon receiving peer reviews, agents revise their initial solutions. Extensive experiments on three different types of reasoning tasks show that our collaboration approach delivers superior accuracy across all ten datasets compared to existing methods. Further study underscores the effectiveness of integrating confidence in reviews, demonstrates the superiority of feedback exchange over mere solution sharing, and highlights the role of capability and diversity in fostering successful collaboration. Code is available at https://github.com/ HITsz-TMG/Multi-agent-peer-review.

## 1 Introduction

“Lookers-on see the chess game better than players.” – Chinese Proverb

Large language models (LLMs) have demonstrated remarkable capabilities in a wide range of natural language processing (NLP) tasks (Touvron et al., 2023; OpenAI, 2023; Anil et al., 2023). The emergent abilities of LLMs have showcased promising results across a multitude of benchmarks (Wei et al., 2022a). Among all rising capabilities, complex reasoning opens up opportunities for building a large spectrum of applications upon LLMs, effectively making LLMs the nextgeneration computation platform (Fu et al., 2023). Current studies have explored human-like problemsolving strategies to push further the boundary of single-model reasoning ability, such as chain-ofthought prompting (Wei et al., 2022b) and selfconsistency (Wang et al., 2023b).

![](images/30a3fc7df1b46db69bc4ddfed6f63641e32bf86b4a260675d0c08f96173c662a.jpg)  
Figure 1: Comparison of self-correction (Huang et al., 2023) and our multi-agent collaboration method. While a single LLM struggles to develop new ideas and selfcorrect its response, our approach enables multiple agents to engage in mutual review and correction, leading to an accurate consensus.

Amidst this background, inspired by the typical human learning strategy of “self-reflection”, the idea of “self-correction” has gained significant research interest, where an LLM automatically reflects on its response and refines based solely on its inherent capabilities (Madaan et al., 2023; Shinn et al., 2023; Pan et al., 2023). However, Liang et al. (2023) suggest that, once the LLM has formulated initial solutions, it cannot generate novel thoughts through self-reflection. Considering the example in Figure 1, the initial answer of the LLM is incorrect. Despite conducting a self-review and attempting to identify problems, the LLM still assesses its answer as being correct. Huang et al. (2023) further note that a single LLM struggles to self-correct its response without external feedback, which leads us to the motivation behind our work: Why not let a single LLM “jump outside the box” and let multiple LLMs provide feedback to each other?

To this end, we propose a multi-agent collaboration strategy that mirrors the academic peer review process. For a given question, each agent first independently submits its own solution. Then the agents perform a systematic review of their peers solutions. They not only examine the reasoning process step by step but also attach a confidence score to quantify the reliability of their feedback. Drawing on the insights from the peer review, each agent finally refines its initial submission and creates an improved version. In the example shown in Figure 1, our collaboration strategy enables multiple agents to engage in mutual review and correction, leading to an accurate consensus. This iterative cycle of creation, review, and revision is akin to the collaborative efforts seen in human learning and problem-solving.

We conduct extensive experiments across three types of reasoning tasks: mathematical reasoning, commonsense reasoning, and symbolic reasoning. The results illustrate that our collaboration method achieves superior performance across all ten datasets compared to previous strong singleagent and multi-agent baselines. Further analysis underscores the effectiveness of expressing uncertainty in the reviews, demonstrates the advantage of sharing feedback rather than solutions, and sug gests that models with minimal capability differences but high diversity can collaborate better.

The contributions of this work are threefold:

• By letting a single agent “think outside the box”, we propose a multi-agent collaboration method that emulates the peer review process – “creation, review, and revision”.

• Our collaboration method consistently outperforms previous strong baselines across three reasoning tasks and ten datasets.

• We demonstrate the efficacy of integrating confidence and sharing feedback, suggesting a viable path forward the optimization of LLMbased multi-agent systems.

## 2 Related Work

With language models scaling up, the emergent abilities have showcased remarkable results across a variety of domains and tasks, challenging our understanding of learning and cognition (Bubeck et al., 2023; OpenAI, 2023). Among these rising capabilities, complex reasoning draws significant interest for its central role in building autonomous language agents and the next-generation computation platform (Xi et al., 2023; Fu et al., 2023).

To push further the boundary of single-agent reasoning, researchers have adopted strategies akin to teaching kids to reason. For example, the chainof-thought prompting (Wei et al., 2022b) employs rationales to steer LLMs through a multi-step reasoning process; the self-consistency method (Wang et al., 2023b) selects the most likely answer from multiple reasoning paths by majority voting; the plan-and-solve prompting (Wang et al., 2023a) and the least-to-most prompting (Zhou et al., 2023) both apply a divide-and-conquer strategy: break down a complex problem into a series of simpler sub-problems and then solve them in sequence.

Amidst this backdrop, a prevailing strategy to address reasoning errors is self-correction, mirroring a typical human learning strategy of selfreflection (Pan et al., 2023). This approach involves an LLM attempting to refine its prior response based solely on its inherent capabilities, without the crutch of external feedback. Contrary to the optimism about self-correction (Madaan et al., 2023; Shinn et al., 2023; Kim et al., 2023), Huang et al. (2023) find that an LLM struggles to correct its response without external feedback. Liang et al. (2023) also conclude that, once the LLM has formulated initial solutions, it cannot generate novel thoughts through self-reflection. In this work, we let a single LLM “jump outside the box” and change its viewpoint from a participant to a critical observer by enabling multiple LLMs to correct each other.

Multi-agent collaboration for task solving is still in its preliminary stages, presenting vast opportunities for exploration. This approach aligns with the Society of Mind (SoM) theory (Minsky, 1988), which suggests that intelligence arises from the interaction of computational modules, achieving collective goals beyond the capabilities of individual modules. CAMEL (Li et al., 2023a) proposes a cooperative agent framework known as roleplaying, enabling agents to cooperate on complex tasks. Such role-playing collaboration has been extended to software development (Qian et al., 2023) and text evaluation (Chan et al., 2023; Li et al., 2023b). Liang et al. (2023) and Du et al. (2023) have delved into multi-agent debates for translation and arithmetic problems. Corex (Sun et al., 2023) has explored three collaboration paradigms in reasoning – debate, code review and retrieve. Through these multi-agent simulations, Zhang et al. (2023) observe human-like social behaviors typical of human collaboration. To this end, we propose a human-mimicking multi-agent collaboration process, wherein multiple agents engage in peer discussions and provide feedback to one another.

![](images/5a1910678a032d229417f3391061323d0d3c9d0cc5bfa8b7b2bb4b9ffa0f81f9.jpg)  
Figure 2: Illustration of our multi-agent peer review collaboration with an example in GSM8K (Cobbe et al., 2021). The process consists of three stages – “creation, review, and revision”. The process starts with three incorrect initial responses. Through a series of human-like discussions and critiques among the agents, two of them arrive at the same correct solution.

## 3 Methodology

Overview. In this work, we introduce a multi-agent collaboration strategy that mirrors the academic peer review process. The overall process is illustrated in Figure 2. The process consists of three stages – “creation, review, and revision”. In stage 1, for a given question, each agent first independently submits its own solution. In stage 2, each agent performs a systematic review of its peers’ solutions. In stage 3, upon receiving the reviews, each agent refines its initial solution and re-submits the improved version. An example of these stages is provided in Section 4.6. We next elaborate these stages in detail.

Stage 1: Create. The peer review process starts with each agent submitting its own solution. Specifically, when presented with a question $q ,$ A group of n agents, denoted as $A _ { 1 } , A _ { 2 } , . . . , A _ { n }$ , perform chain-of-thought reasoning. Each agent generates its own reasoning chains and corresponding answers $a _ { i }$ . Take Figure 2 as an example, the initial answers of three agents are all incorrect.

Stage 2: Review. We next feed each agent $A _ { i }$ with the solution of its peers (i.e., $A _ { j }$ , where $j \neq$ i), one at a time, to write reviews $r _ { i j }$ . Note that $r _ { i j }$ denotes the review from agent $A _ { i }$ to agent $A _ { j }$ In current review forms, reviewers do more than just provide overall assessments; they also indicate their certainty about their evaluations. Mirroring such real-life review practices, the agents not only examine the reasoning process step by step but also attach a confidence score to quantify the reliability of their feedback. To achieve this, we concatenate each peer solution with the following instruction: Please examine this agent’s reasoning process step by step and offer feedback on its reasoning. You can rate your confidence in your feedback on a scale from 1-10, where 10 indicates the highest level of confidence.

In the example shown in Figure 2, one agent accurately determines the initial height but forgets to multiply the ratio twice. Conversely, another agent multiplies the ratio twice but gets the initial height wrong. Although their initial answers are wrong, they can provide effective feedback confidently to each other, based on the difference between their solutions and those of their peers.

Stage 3: Revise. We finally feed each agent $A _ { i }$ with the reviews from its peers $( \mathrm { i } . \mathrm { e } . , r _ { j i } )$ , all at once, to refine the initial solutions. The agent considers both the peer solutions in dialogue history and the received peer reviews. To achieve this, we concatenate the reviews with the following instruction: Using other agents’ solutions and feedbacks as additional information, can you provide your answer to the problem? In the example illustrated in Figure 2, out of three agents, two successfully integrate accurate feedback into their final responses. This results in both agents converging on the same correct solution after revision.

<table><tr><td>Dataset</td><td>Domain</td><td># Samples</td><td>Avg. words</td><td>Answer</td></tr><tr><td>GSM8K (Cobbe et al., 2021)</td><td>Math</td><td>1319</td><td>46.9</td><td>Number</td></tr><tr><td>SVAMP (Patel et al., 2021)</td><td>Math</td><td>1000</td><td>31.8</td><td>Number</td></tr><tr><td>AQuA (Ling et al., 2017)</td><td>Math</td><td>254</td><td>51.9</td><td>Option</td></tr><tr><td>MultiArith (Roy and Roth, 2015)</td><td>Math</td><td>600</td><td>31.8</td><td>Number</td></tr><tr><td>AddSub (Hosseini et al., 2014)</td><td>Math</td><td>395</td><td>31.5</td><td>Number</td></tr><tr><td>SingleEq (Koncel-Kedziorski et al., 2015)</td><td>Math</td><td>508</td><td>27.4</td><td>Number</td></tr><tr><td>ARC-c (Clark et al., 2018)</td><td>CS</td><td>1172</td><td>22.3</td><td>Option</td></tr><tr><td>StrategyQA (Geva et al., 2021)</td><td>CS</td><td>2290</td><td>9.6</td><td>Yes / No</td></tr><tr><td>Colored Objects (Suzgun et al., 2023)</td><td>Sym.</td><td>250</td><td>37.2</td><td>Option</td></tr><tr><td>Penguins (Suzgun et al., 2023)</td><td>Sym.</td><td>146</td><td>86.7</td><td>Option</td></tr></table>

Table 1: Details of ten evaluation datasets. Math: mathematical reasoning. CS: commonsense reasoning. Sym.: symbolic reasoning.

Unlike prior studies such as Du et al. (2023) and Sun et al. (2023), we do not explicitly ask the agents to reach a consensus at the end of the review. The final prediction is determined through a majority vote among the n participating agents. This approach ensures the impartiality and balance of our peer review process.

## 4 Experiment

## 4.1 Benchmarks

Our method is evaluated on ten benchmark datasets from three categories of reasoning problems: mathematical reasoning, commonsense reasoning, and symbolic reasoning. Table 1 shows the statistics of evaluation datasets.

## Mathematical reasoning:

• GSM8K (Cobbe et al., 2021): A high quality linguistically diverse grade-school math word problems created by human problem writers.

• SVAMP (Patel et al., 2021): A challenging math word problem set with grade level up to 4, by applying simple variations over an existing dataset.

• AQuA (Ling et al., 2017): A math word problem set with natural language rationales.

• MultiArith (Roy and Roth, 2015): A set of math word problems requiring multiple reasoning steps and operations.

• AddSub (Hosseini et al., 2014): A set of addition and subtraction math word problems.

• SingleEq (Koncel-Kedziorski et al., 2015): A single-equation grade-school math word problems with multiple math operations over nonnegative rational numbers and one variable.

## Commonsense reasoning:

• ARC-c (Clark et al., 2018): A subset of the AI2 Reasoning Challenge, consisting of challenging science questions that require reasoning and a wide breadth of knowledge to answer the multiple-choice problems correctly.

• StrategyQA (Geva et al., 2021): A commonsense QA task with Yes or No answer format that requires models to perform multi-hop reasoning to answer the questions.

## Symbolic reasoning:

• Colored Objects (Suzgun et al., 2023): Given a context, answer a simple question about the color of an object on a surface.

• Penguins (Suzgun et al., 2023): Given a unique table of penguins, answer a question about the attributes of the them.

<table><tr><td></td><td>GSM8K</td><td>SVAMP</td><td>AQuA</td><td>MultiArith</td><td>AddSub</td><td>SingleEq</td></tr><tr><td>Zero-shot CoT</td><td>75.33</td><td>77.27</td><td>58.27</td><td>96.40</td><td>87.26</td><td>92.00</td></tr><tr><td>Self-correct</td><td>74.13</td><td>76.40</td><td>53.67</td><td>93.33</td><td>82.62</td><td>89.13</td></tr><tr><td>Multi-agent Majority</td><td>81.80</td><td>79.80</td><td>62.20</td><td>97.80</td><td>89.37</td><td>93.60</td></tr><tr><td>Multi-agent Debate</td><td>81.60</td><td>78.40</td><td>62.60</td><td>97.20</td><td>88.10</td><td>93.80</td></tr><tr><td>Ours</td><td>83.20</td><td>83.60</td><td>65.35</td><td>98.00</td><td>89.87</td><td>94.20</td></tr><tr><td>Ours (w/o confidence)</td><td>82.60</td><td>82.60</td><td>63.78</td><td>97.60</td><td>88.61</td><td>93.40</td></tr><tr><td>Ours (w/o solution)</td><td>82.80</td><td>83.30</td><td>64.96</td><td>97.40</td><td>89.87</td><td>94.00</td></tr></table>

Table 2: Accuracy of our collaboration strategy compared with previous state-of-the-art methods on six mathematical reasoning datasets. The best results are in bold.

<table><tr><td></td><td>ARC-c</td><td>StrategyQA</td></tr><tr><td>Zero-shot CoT</td><td>86.07</td><td>66.13</td></tr><tr><td>Self-correct</td><td>57.73</td><td>52.93</td></tr><tr><td>Multi-agent Majority</td><td>87.60</td><td>68.20</td></tr><tr><td>Multi-agent Debate</td><td>87.40</td><td>69.40</td></tr><tr><td>Ours</td><td>88.40</td><td>69.80</td></tr><tr><td>Ours (w/o confidence)</td><td>88.60</td><td>69.40</td></tr><tr><td>Ours (w/o solution)</td><td>88.00</td><td>67.00</td></tr></table>

Table 3: Accuracy on commonsense reasoning datasets.

<table><tr><td></td><td>Colored Objects</td><td>Penguins</td></tr><tr><td>Zero-shot CoT</td><td>66.13</td><td>70.78</td></tr><tr><td>Self-correct</td><td>28.27</td><td>47.95</td></tr><tr><td>Multi-agent Majority</td><td>70.40</td><td>73.29</td></tr><tr><td>Multi-agent Debate</td><td>69.60</td><td>76.71</td></tr><tr><td>Ours</td><td>73.20</td><td>79.45</td></tr><tr><td>Ours (w/o confidence)</td><td>74.40</td><td>79.45</td></tr><tr><td>Ours (w/o solution)</td><td>71.60</td><td>76.71</td></tr></table>

Table 4: Accuracy on symbolic reasoning datasets.

## 4.2 Baselines

We compare our peer review collaboration with the following single-agent and multi-agent methods:

• Zero-shot CoT (Kojima et al., 2022) utilizes prompts to elicit both reasoning chains and answers from an LLM.

• Self-correct (Huang et al., 2023) enables an LLM to iteratively review, find problems, and refine its answer.

• Multi-agent Majority (Wang et al., 2023b) selects the most consistent answer from several reasoning chains.

• Multi-agent Debate (Du et al., 2023): Each agent in the group sees solutions of others, up dates its own solution, and repeats this process iteratively.

## 4.3 Implementation Details

We use the gpt-3.5-turbo-0613 OpenAI API for all main experiments. In further analysis involving different LLMs for collaboration, we also incorporate the use of gpt-3.5-turbo-16k-0613, claude-instant-1.2 and claude-2.1. The details of prompts and hyperparameter settings are in Appendix A.

## 4.4 Results

Main results. Table 2 shows the accuracy comparison on the mathematical reasoning datasets. Our peer review strategy surpasses all single-agent and multi-agent baselines across all datasets, especially significant in more challenging benchmarks (+1.40% on GSM8K, +3.80% on SVAMP, +2.75% on AQuA over the prior state-of-the-art).

Table 3 and Table 4 show the results on commonsense reasoning and symbolic reasoning datasets, respectively. Our collaboration method consistently outperforms all prior baselines across all datasets. The effectiveness of self-correction notably decreases in non-math reasoning tasks, as seen with a substantial drop from 66.13% to 28.27% in accuracy on Colored Objects. However, when we introduce feedback from other agents, there is a significant enhancement in performance, rising from 66.13% to 73.20%. This demonstrates the advantage of integrating external feedback over relying solely on internal feedback mechanisms.

Ablation study. For the ablation of confidence in reviews, we alter the prompt of Stage 2 described in Section 3. Specifically, we remove the prompt of eliciting confidence, simplifying it to: “Please examine this agent’s reasoning process step by step and offer feedback on its reasoning”. Table 2 shows the effectiveness of expressing uncertainty and integrating confidence in feedback on mathematical reasoning datasets. An example of confidence ablation is shown in Appendix B. As stated in the prompt of Stage 3, the updated answer uses other agents’ solutions and feedback as additional information. In the absence of confidence scores, the updated answer tends to be misled by ineffective feedback and remains incorrect. In contrast, the integration of confidence score enables the model to selectively aggregate valuable information. By focusing more on solutions with higher confidence levels rather than on less reliable feedback, the confidence scores guide the model towards the correct answer.

![](images/c63f307a503cae03dd6c250330988d77cf39d5378f2236e08cbaa6bec1600e0a.jpg)  
(a) Self-correct

![](images/e127204d120f3ea58e55788e45c0db1de9cd7512b2f08441a1ab800b272df7a3.jpg)  
(b) Our method  
Figure 3: Comparison of the changes in answers on GSM8K after self-correction and our collaboration method. No change: The answer remains unchanged; Correct→Incorrect: A correct answer is changed to an incorrect one; Incorrect→Correct: An incorrect answer is revised to a correct one; Incorrect→Incorrect: An incorrect answer is altered but remains incorrect.

For commonsense reasoning in Table 3 and symbolic reasoning in Table 4, incorporating confidence can result in unchanged or even reduced performance. This decrease may stem from the tendency of LLMs to exhibit overconfidence and significant miscalibration when verbalizing their confidence in non-math datasets (Xiong et al., 2023b). We will further discuss the relationship between the level of confidence and the correctness of feedback in Section 4.5.

For the ablation of solutions, we leave out the the dialogue history of Stage 2 during the answer revision process in Stage 3, so that the peer solutions cannot be seen. We also change the prompt of Stage 3 into “Using other agents’ feedbacks as additional information, can you provide your answer to the problem? ”. From Table 2, 3 and 4, omitting solutions resulted in decreased performance in 9 out of 10 datasets, indicating that solutions contribute valuable complementary information to the feedback received. In addition, Ours (w/o solution), which involves exchanging only peer feedback, outperforms Multi-agent Debate, which exchanges only peer solutions, in 8 out of 10 datasets. This demonstrates that peer feedback is more effective than peer solutions in multi-agent collaboration.

## 4.5 Analysis

Comparison of answer changes. We compare the revised solutions with the initial solutions, and summarize the results of changes in answers after self-correction and our method. Figure 3 and Appendix C show the answer changes on GSM8K and Penguins respectively. When applying selfcorrection on GSM8K, the model is more likely to modify a correct answer to an incorrect one than to revise an incorrect answer to a correct one. In the non-math dataset Penguins, there is a higher chance that the model alters its answer after selfcorrection. In 37.0% of the time, the model changes a correct answer into an incorrect one. However, our method exhibits a different pattern for both the GSM8K and Penguins datasets, with the portion of Incorrect→Correct significantly larger than Correct→Incorrect. Both figures illustrate the benefits of incorporating external feedback over relying solely on internal feedback mechanisms.

Impact of agent numbers and review rounds. We study how the number of agents and review rounds affects performance. From Figure 4a, an upward trend is observed in the relationship between the accuracy and the agent number. The growth pattern reaches an apex at 4 agents before declin ing at agent number 5. Regarding the relationship between the accuracy and the review rounds, as shown in Figure 4b, no significant improvement trend is detected with more review rounds. This observation is consistent with the findings of Chan et al. (2023), which suggest that continual discussions often lead to reduced performance. The decrease may be due to issues associated with the ever-increasing long-context modeling, which negatively affects the performance.

![](images/94d11327b6869b30e010106d463f4673e8b70b063e076b26851ae3fb7914ad8e.jpg)  
(a) Accuracy vs. Agent Number

![](images/07f1948f339a09c0ef0d37d8baac094bc1bd2d71d0d4b63181a601ea88b6decf.jpg)  
(b) Accuracy vs. Review Round

Figure 4: Performance on GSM8K and SVAMP with increased agents and review rounds: Performance shows an upward trend as the number of involved agents increases, while no significant improvement trend is detected with more review rounds.
<table><tr><td>Peer Review</td><td>Capability Gap</td><td>Diversity</td><td>LLM</td><td>Initial Acc.</td><td>Updated Acc.</td><td> $\Delta$ </td></tr><tr><td>gpt-3.5-turbo-0301 &amp; gpt-3.5-turbo-0613</td><td>2.8</td><td>35.4</td><td> $\mathtt { g p t - 3 . 5 - t u r b o - } \theta 3 \theta 1$   $\mathsf { g p t } - 3 . 5 \mathsf { - t u r b o } \mathsf { - } 0 6 1 3$ </td><td>72.6 75.4</td><td>80.0 77.8</td><td>+7.4 +2.4</td></tr><tr><td>gpt-3.5-turbo-0613  $\mathtt { \& } \mathtt { c l a u d e  – i n s t a n t - 1 . 2 }$ </td><td>10.0</td><td>31.4</td><td>gpt-3.5-turbo-0613  $\mathtt { c l a u d e - i n s t a n t - } 1 . 2$ </td><td>75.4 85.4</td><td>83.0</td><td>+7.6</td></tr><tr><td>claude-instant-1.2</td><td></td><td>15.8</td><td>claude-instant-1.2</td><td>85.4</td><td>86.0 86.6</td><td>+0.6 +1.2</td></tr><tr><td>&amp; claude-2.1</td><td>2.2</td><td></td><td>claude-2.1</td><td>87.6</td><td>87.4</td><td>-0.2</td></tr></table>

Table 5: The peer review collaboration results with different LLMs. LLMs with smaller capability gap but higher diversity can improve and collaborate with each other better.

Interplay between confidence scores and feedback correctness. We manually annotate the correctness of 600 feedback each from the GSM8K and Penguins datasets. We present the relationship between confidence scores and feedback correctness in Figure 5, along with the evaluation metrics such as feedback accuracy, Area Under the Receiver Operating Characteristic curve (AUROC) and Expected Calibration Error (ECE). We have the following observations: (1) From the confidence distribution in the first row of Figure 5, most verbalized confidence scores fall within the 80% to

100% range. (2) The second row of Figure 5 shows that the accuracy of each bar ranging from 80% to 100% is much less than 80%, suggesting significant overconfidence and miscalibration in LLMs. (3) When comparing the math dataset GSM8K with the non-math dataset Penguins, the feedback in the non-math dataset tends to be more poorly calibrated and exhibit greater overconfidence. This observation might explain the finding in ablation study (Section 4.4), which suggests that incorporating confidence on non-math datasets may not improve performance.

Performance variability with diverse LLMs. We explore what kind of LLMs can collaborate well and improve each other through the peer review process. We set the agent number at 2, and use GSM8K for the analysis. We focus on two key factors: the capability gap and diversity between LLMs. The capability gap refers to the difference in the accuracy of initial responses provided by two LLMs. The diversity is measured by INCON (Xiong et al., 2023a). Specifically, suppose there are n LLMs $L = \{ l _ { 1 } , \cdots , l _ { n } \}$ , and a dataset with m samples $X = \{ x _ { 1 } , \cdots , x _ { m } \}$ . We define $p _ { j } ^ { i }$ as the prediction of $l _ { i }$ on $x _ { j }$ . Then the INCON of L on $X$

![](images/8a565a2b82367c319e563200d2b63f5a11d6a33259d76608b7cd6447fbdee778.jpg)

![](images/ca9a076ece84101e0396ee3396491245eb387b842e802a12449821afe5747698.jpg)

![](images/9698332b21e4b45765c9aa60700164750401c402be259b1b3f049cb63d1dbe1c.jpg)  
(a) GSM8K

![](images/b7513a617af51ad3e9461aaa1a7a98c0f9c289dd40974722c6dc886465796352.jpg)  
(b) Penguins  
Figure 5: First row: Distribution of verbalized confidence on GSM8K and Penguins. Most samples fall into the 80% to 100% range. To better illustrate the major confidence distribution, we set the minimal confidence threshold at 50%, as very few confidences fall below. Second row: Reliability diagram on GSM8K and Penguins. The accuracy within each bin is much lower than its corresponding confidence, showing significant overconfidence.

can be defined as:

$$
\operatorname { I N C O N } = \sum _ { k = 1 } ^ { m } { \frac { \Phi ( p _ { k } ^ { 1 } , \cdot \cdot \cdot , p _ { k } ^ { n } ) } { m } } ,\tag{1}
$$

Φ is a sign function, it will be assigned a value of 1 if there are any two variables in Φ that are not equal, otherwise, Φ takes a value of 0.

The collaboration results are presented in Table 5. We have the following conclusions: (1) More powerful models provide more effective feedback. The 0301 version of gpt-3.5-turbo contributes to a 2.4% accuracy improvement in the 0613 version, while the more advanced claude-instant-1.2 leads to a significant 7.6% increase. (2) LLMs with smaller capability gap can collaborate better. By comparing the first two rows, despite similar levels of diversity, a capability gap increase from 2.8 to 10.0 corresponds to a decrease in performance enhancement for the stronger model, from a 2.4% to just a 0.6% improvement. (3) LLMs with higher diversity can collaborate better. With a similar capability gap, the collaboration between gpt-3.5-turbo-0301 and its 0613 version, which have considerable diversity, results in mutual improvement. In contrast, two claude models, with substantially lower diversity, show that the stronger model does not benefit from the collaboration.

Impact of agent roles. Our default experiments do not include any system messages (i.e. role specification). Here we explore diverse role prompts for agent initialization. The roles are automatically generated by SPP (Wang et al., 2023c) and detailed in Appendix D. Experiment results in Appendix D highlight the cruciality of diverse role prompt design in multi-agent collaboration.

## 4.6 Case study

In this section, we present the complete peer review collaboration process to a math question in GSM8K (Cobbe et al., 2021). As shown in Appendix E, the procedure begins with two incorrect initial answers. Through a series of dynamic, human-like discussions and critiques among the agents (for example, Agent B explicitly addresses Agent A’s misunderstanding of the question and the mistake in the ratio step), all three agents eventually converge on the same correct solution.

## 5 Conclusion

In this work, we let a single model think outside the box by engaging multiple models to collaborate on complex reasoning. We introduce a multi-agent collaboration strategy that emulates the academic peer review process, following an iterative cycle of creation, review, and revision. Extensive experiments show that our approach delivers superior accuracy across all ten datasets and three tasks compared to existing methods. Further analysis shows the effectiveness of confidence integration and demonstrates the superiority of feedback exchange over mere solution sharing.

## Limitations

Despite the effectiveness of multi-agent methods, it is essential to consider the associated costs, particularly in terms of token consumption. The balance between effectiveness and efficiency emerges as a critical area for exploration. In addition, the underlying factors for LLM collaboration are more than just capability and answer diversity. The factors also include role and tool specification of agents. Further research may focus on identifying which types of agents can collaborate more effectively together, thereby providing deeper insights into the optimization of multi-agent systems in practical applications.

## References

Rohan Anil, Andrew M. Dai, Orhan Firat, Melvin Johnson, Dmitry Lepikhin, Alexandre Passos, Siamak Shakeri, Emanuel Taropa, Paige Bailey, Zhifeng Chen, Eric Chu, Jonathan H. Clark, Laurent El Shafey, Yanping Huang, Kathy Meier-Hellstern, Gaurav Mishra, Erica Moreira, Mark Omernick, Kevin Robinson, Sebastian Ruder, Yi Tay, Kefan Xiao, Yuanzhong Xu, Yujing Zhang, Gustavo Hernandez Abrego, Junwhan Ahn, Jacob Austin, Paul Barham, Jan Botha, James Bradbury, Siddhartha Brahma, Kevin Brooks, Michele Catasta, Yong Cheng, Colin Cherry, Christopher A. Choquette-Choo, Aakanksha Chowdhery, Clément Crepy, Shachi Dave, Mostafa Dehghani, Sunipa Dev, Jacob Devlin, Mark Díaz, Nan Du, Ethan Dyer, Vlad Feinberg, Fangxiaoyu Feng, Vlad Fienber, Markus Freitag, Xavier Garcia, Sebastian Gehrmann, Lucas Gonzalez, Guy Gur-Ari, Steven Hand, Hadi Hashemi, Le Hou, Joshua Howland, Andrea Hu, Jeffrey Hui, Jeremy Hurwitz, Michael Isard, Abe Ittycheriah, Matthew Jagielski, Wenhao Jia, Kathleen Kenealy, Maxim Krikun, Sneha Kudugunta, Chang Lan, Katherine Lee, Benjamin Lee, Eric Li, Music Li, Wei Li, YaGuang Li,

Jian Li, Hyeontaek Lim, Hanzhao Lin, Zhongtao Liu, Frederick Liu, Marcello Maggioni, Aroma Mahendru, Joshua Maynez, Vedant Misra, Maysam Moussalem, Zachary Nado, John Nham, Eric Ni, Andrew Nystrom, Alicia Parrish, Marie Pellat, Martin Polacek, Alex Polozov, Reiner Pope, Siyuan Qiao, Emily Reif, Bryan Richter, Parker Riley, Alex Castro Ros, Aurko Roy, Brennan Saeta, Rajkumar Samuel, Renee Shelby, Ambrose Slone, Daniel Smilkov, David R. So, Daniel Sohn, Simon Tokumine, Dasha Valter, Vijay Vasudevan, Kiran Vodrahalli, Xuezhi Wang, Pidong Wang, Zirui Wang, Tao Wang, John Wieting, Yuhuai Wu, Kelvin Xu, Yunhan Xu, Linting Xue, Pengcheng Yin, Jiahui Yu, Qiao Zhang, Steven Zheng, Ce Zheng, Weikang Zhou, Denny Zhou, Slav Petrov, and Yonghui Wu. 2023. Palm 2 technical report.

Sébastien Bubeck, Varun Chandrasekaran, Ronen Eldan, Johannes Gehrke, Eric Horvitz, Ece Kamar, Peter Lee, Yin Tat Lee, Yuanzhi Li, Scott Lundberg, Harsha Nori, Hamid Palangi, Marco Tulio Ribeiro, and Yi Zhang. 2023. Sparks of artificial general intelligence: Early experiments with gpt-4.

Chi-Min Chan, Weize Chen, Yusheng Su, Jianxuan Yu, Wei Xue, Shanghang Zhang, Jie Fu, and Zhiyuan Liu. 2023. Chateval: Towards better llm-based evaluators through multi-agent debate.

Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick, and Oyvind Tafjord. 2018. Think you have solved question answering? try arc, the ai2 reasoning challenge.

Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, Christopher Hesse, and John Schulman. 2021. Training verifiers to solve math word problems.

Yilun Du, Shuang Li, Antonio Torralba, Joshua B. Tenenbaum, and Igor Mordatch. 2023. Improving factuality and reasoning in language models through multiagent debate.

Yao Fu, Litu Ou, Mingyu Chen, Yuhao Wan, Hao Peng, and Tushar Khot. 2023. Chain-of-thought hub: A continuous effort to measure large language models’ reasoning performance.

Mor Geva, Daniel Khashabi, Elad Segal, Tushar Khot, Dan Roth, and Jonathan Berant. 2021. Did aristotle use a laptop? a question answering benchmark with implicit reasoning strategies. Transactions of the Association for Computational Linguistics, 9:346– 361.

Mohammad Javad Hosseini, Hannaneh Hajishirzi, Oren Etzioni, and Nate Kushman. 2014. Learning to solve arithmetic word problems with verb categorization. In Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP), pages 523–533, Doha, Qatar. Association for Computational Linguistics.

Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, and Denny Zhou. 2023. Large language models cannot self-correct reasoning yet.

Geunwoo Kim, Pierre Baldi, and Stephen McAleer. 2023. Language models can solve computer tasks.

Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yutaka Matsuo, and Yusuke Iwasawa. 2022. Large language models are zero-shot reasoners. In Advances in Neural Information Processing Systems.

Rik Koncel-Kedziorski, Hannaneh Hajishirzi, Ashish Sabharwal, Oren Etzioni, and Siena Dumas Ang. 2015. Parsing algebraic word problems into equations. Transactions of the Association for Computational Linguistics, 3:585–597.

Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem. 2023a. Camel: Communicative agents for "mind" exploration of large language model society.

Ruosen Li, Teerth Patel, and Xinya Du. 2023b. Prd: Peer rank and discussion improve large language model based evaluations.

Tian Liang, Zhiwei He, Wenxiang Jiao, Xing Wang, Yan Wang, Rui Wang, Yujiu Yang, Zhaopeng Tu, and Shuming Shi. 2023. Encouraging divergent thinking in large language models through multi-agent debate.

Wang Ling, Dani Yogatama, Chris Dyer, and Phil Blunsom. 2017. Program induction by rationale generation: Learning to solve and explain algebraic word problems. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 158–167, Vancouver, Canada. Association for Computational Linguistics.

Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, and Peter Clark. 2023. Self-refine: Iterative refinement with self-feedback.

M. Minsky. 1988. Society Of Mind. Touchstone book. Simon & Schuster.

OpenAI. 2023. Gpt-4 technical report.

Liangming Pan, Michael Saxon, Wenda Xu, Deepak Nathani, Xinyi Wang, and William Yang Wang. 2023. Automatically correcting large language models: Surveying the landscape of diverse self-correction strategies.

Arkil Patel, Satwik Bhattamishra, and Navin Goyal. 2021. Are NLP models really able to solve simple math word problems? In Proceedings of the 2021 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, pages 2080–2094, Online. Association for Computational Linguistics.

Chen Qian, Xin Cong, Wei Liu, Cheng Yang, Weize Chen, Yusheng Su, Yufan Dang, Jiahao Li, Juyuan Xu, Dahai Li, Zhiyuan Liu, and Maosong Sun. 2023. Communicative agents for software development.

Subhro Roy and Dan Roth. 2015. Solving general arithmetic word problems. In Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing, pages 1743–1752, Lisbon, Portugal. Association for Computational Linguistics.

Noah Shinn, Federico Cassano, Edward Berman, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. 2023. Reflexion: Language agents with verbal reinforcement learning.

Qiushi Sun, Zhangyue Yin, Xiang Li, Zhiyong Wu, Xipeng Qiu, and Lingpeng Kong. 2023. Corex: Pushing the boundaries of complex reasoning through multi-model collaboration.

Mirac Suzgun, Nathan Scales, Nathanael Schärli, Sebastian Gehrmann, Yi Tay, Hyung Won Chung, Aakanksha Chowdhery, Quoc Le, Ed Chi, Denny Zhou, and Jason Wei. 2023. Challenging BIG-bench tasks and whether chain-of-thought can solve them. In Findings of the Association for Computational Linguistics: ACL 2023, pages 13003–13051, Toronto, Canada. Association for Computational Linguistics.

Hugo Touvron, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, Soumya Batra, Prajjwal Bhargava, Shruti Bhosale, Dan Bikel, Lukas Blecher, Cristian Canton Ferrer, Moya Chen, Guillem Cucurull, David Esiobu, Jude Fernandes, Jeremy Fu, Wenyin Fu, Brian Fuller, Cynthia Gao, Vedanuj Goswami, Naman Goyal, Anthony Hartshorn, Saghar Hosseini, Rui Hou, Hakan Inan, Marcin Kardas, Viktor Kerkez, Madian Khabsa, Isabel Kloumann, Artem Korenev, Punit Singh Koura, Marie-Anne Lachaux, Thibaut Lavril, Jenya Lee, Diana Liskovich, Yinghai Lu, Yuning Mao, Xavier Martinet, Todor Mihaylov, Pushkar Mishra, Igor Molybog, Yixin Nie, Andrew Poulton, Jeremy Reizenstein, Rashi Rungta, Kalyan Saladi, Alan Schelten, Ruan Silva, Eric Michael Smith, Ranjan Subramanian, Xiaoqing Ellen Tan, Binh Tang, Ross Taylor, Adina Williams, Jian Xiang Kuan, Puxin Xu, Zheng Yan, Iliyan Zarov, Yuchen Zhang, Angela Fan, Melanie Kambadur, Sharan Narang, Aurelien Rodriguez, Robert Stojnic, Sergey Edunov, and Thomas Scialom. 2023. Llama 2: Open foundation and finetuned chat models.

Lei Wang, Wanyu Xu, Yihuai Lan, Zhiqiang Hu, Yunshi Lan, Roy Ka-Wei Lee, and Ee-Peng Lim. 2023a. Plan-and-solve prompting: Improving zeroshot chain-of-thought reasoning by large language models. In Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 2609–2634, Toronto, Canada. Association for Computational Linguistics.

Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc V Le, Ed H. Chi, Sharan Narang, Aakanksha Chowdhery,

and Denny Zhou. 2023b. Self-consistency improves chain of thought reasoning in language models. In The Eleventh International Conference on Learning Representations.

Zhenhailong Wang, Shaoguang Mao, Wenshan Wu, Tao Ge, Furu Wei, and Heng Ji. 2023c. Unleashing cognitive synergy in large language models: A task-solving agent through multi-persona self-collaboration.

Jason Wei, Yi Tay, Rishi Bommasani, Colin Raffel, Barret Zoph, Sebastian Borgeaud, Dani Yogatama, Maarten Bosma, Denny Zhou, Donald Metzler, Ed H. Chi, Tatsunori Hashimoto, Oriol Vinyals, Percy Liang, Jeff Dean, and William Fedus. 2022a. Emergent abilities of large language models. Transactions on Machine Learning Research. Survey Certification.

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, brian ichter, Fei Xia, Ed Chi, Quoc V Le, and Denny Zhou. 2022b. Chain-of-thought prompting elicits reasoning in large language models. In Advances in Neural Information Processing Systems, volume 35, pages 24824–24837. Curran Associates, Inc.

Zhiheng Xi, Wenxiang Chen, Xin Guo, Wei He, Yiwen Ding, Boyang Hong, Ming Zhang, Junzhe Wang, Senjie Jin, Enyu Zhou, Rui Zheng, Xiaoran Fan, Xiao Wang, Limao Xiong, Yuhao Zhou, Weiran Wang, Changhao Jiang, Yicheng Zou, Xiangyang Liu, Zhangyue Yin, Shihan Dou, Rongxiang Weng, Wensen Cheng, Qi Zhang, Wenjuan Qin, Yongyan Zheng, Xipeng Qiu, Xuanjing Huang, and Tao Gui. 2023. The rise and potential of large language model based agents: A survey.

Kai Xiong, Xiao Ding, Yixin Cao, Ting Liu, and Bing Qin. 2023a. Examining inter-consistency of large language models collaboration: An in-depth analysis via debate. In Findings of the Association for Computational Linguistics: EMNLP 2023, pages 7572–7590, Singapore. Association for Computational Linguistics.

Miao Xiong, Zhiyuan Hu, Xinyang Lu, Yifei Li, Jie Fu, Junxian He, and Bryan Hooi. 2023b. Can llms express their uncertainty? an empirical evaluation of confidence elicitation in llms.

Jintian Zhang, Xin Xu, and Shumin Deng. 2023. Exploring collaboration mechanisms for llm agents: A social psychology view.

Denny Zhou, Nathanael Schärli, Le Hou, Jason Wei, Nathan Scales, Xuezhi Wang, Dale Schuurmans, Claire Cui, Olivier Bousquet, Quoc V Le, and Ed H. Chi. 2023. Least-to-most prompting enables complex reasoning in large language models. In The Eleventh International Conference on Learning Representations.

## A Implementation Details

We use the gpt-3.5-turbo-0613 OpenAI API for all experiments, with all parameters in default setting. We fix the agent number as 3 and the round number of review cycle as 1. We also apply gpt-3.5-turbo-16k-0613 to explore scenarios with a greater number of agents and additional review rounds in Section 4.5. Specifically, we utilize the 16k version for experiments when the total count of agents is set to 5. We also use the 16k version for an increased number of review cycles. The review is conducted over four rounds, with accuracy being calculated after each round, so the result at the first round in Figure 4 may differ from the reported result in Table 2.

Our implementation of the self-correct prompt draws from Huang et al. (2023). For the implementation of multi-agent debate (Du et al., 2023), we utilize the official Github repository1. This implementation adheres to the default configuration of three agents and two debate rounds.

For evaluation metric, we follow Kojima et al. (2022) and report the accuracy of all methods across datasets. Due to the rate limits and a restricted budget, our experiments use a maximum of 500 samples, randomly selected from each dataset.

## B Example of Confidence Ablation

Here we present an example of confidence ablation in Table 6. The initial solution of Agent A is wrong. In the absence of confidence scores, the final answer is misled by ineffective feedback and remains unchanged. In contrast, the integration of confidence score enables the model to focus more on solutions with higher confidence levels rather than on less reliable feedback, eventually guiding the model towards the correct answer.

## C Answer Change Comparison

We compare the revised answers with the initial answers, and summarize the results of changes in answers after self-correction and our method. Figure 6 show the answer changes on the Penguins dataset.

## D Impact of Diverse Role Prompts

We conduct experiments on GSM8K and SVAMP. The following five roles are automatically generated through SPP (Wang et al., 2023c):

1The code for Du et al. (2023) is at https://github.com/ composable-models/llm\_multiagent\_debate

<table><tr><td rowspan="2">Example</td><td colspan="2">Q: If there are 10 eggs in a basket, and there are twice as many eggs in a second basket, how many eggs are in both baskets put together?</td></tr><tr><td colspan="2"> $\mathbf { A } \colon 1 0 + 1 0 ^ { \ast } 2 = 3 0$ </td></tr><tr><td>Stage 1: Create</td><td colspan="2">Let&#x27;s call the number of eggs in the first basket x. We know that  $\mathrm { x } + 2 \mathrm { x } = 1 0 ,$  since the total number of eggs in both baskets is given as 10. x = 10/3. Since we need a whole number of eggs, we can round this value down to the nearest whole number, which is 3. Therefore, there are x = 3 eggs in the first basket and  $2 \mathrm { x } = 2 ( 3 ) = 6 ~ \mathrm { e g g s }$  in the second basket. Hence, there are 9 eggs in both baskets put together.</td></tr><tr><td rowspan="3">Stage 2: Review</td><td>Receives a correct solution from Agent B.</td><td>I would rate my confidence in the feedback given a 10. Overall,</td></tr><tr><td>Overall, the agent&#x27;s reasoning and steps are accurate and correct.</td><td>the agent&#x27;s reasoning and steps are accurate and correct.</td></tr><tr><td>Receives another correct solution from Agent C.</td><td></td></tr><tr><td rowspan="2">Stage 3: Revise</td><td>The agent&#x27;s reasoning and steps are accurate and correct. Receives two wrong feedback from Agent B and Agent C: The agent&#x27;s reasoning process is correct, and each step is logical and ac-</td><td>I would rate my confidence in the feedback given a 10. The agent&#x27;s reasoning and steps are accurate and correct. Receives two wrong feedback from Agent B and Agent C: The agent&#x27;s reasoning process is correct, and each step is logical and accurate. My confidence in this feedback is 9; The agent&#x27;s</td></tr><tr><td>curate; The agent&#x27;s reasoning was mostly correct except for the rounding of the value of x.  $\mathrm { x } + 2 \mathrm { x } = 1 0 . \mathrm { x } = 3 .$  The answer is  $3 + 3 * 2 =$  9 eggs in both baskets put together.</td><td>reasoning was mostly correct except for the rounding of the value of x. I would rate my confidence in this feedback as 7 out of 10.  $1 0 + 1 0 \ast 2 = 3 0 .$  The correct answer is 30 eggs in both baskets put together.</td></tr></table>

Table 6: The responses of Agent A without confidence (left) and with confidence (right). The correct answer and feedback are in green, and the wrong ones are in red. The confidence score assists Agent A towards the correct answer. For ease of read, only the key points of the responses are displayed.

AI Assistant. You are an advanced AI capable of performing complex calculations, logical reasoning, and providing efficient solutions to mathematical problems.

Math Teacher. You are an experienced math teacher with a deep understanding of mathematical concepts, methods, and pedagogy. You can offer insights into problem-solving strategies and educational approaches to mathematics.

Mathematical Scientist. You are a scientist who specializes in advanced mathematical theories and research. You can contribute deep theoretical knowledge and expertise in cutting-edge mathematical areas, such as topology, abstract algebra, or number theory.

Engineer. You are a professional engineer with practical experience in applying mathematical concepts to solve real-world problems. You can offer a practical viewpoint on how mathematics is used in designing, analyzing, and improving systems and structures.

Computer Scientist. You are an expert in computer science, well-versed in algorithms, computational theory, and programming. You can assist in solving problems that involve algorithmic thinking, computational complexity, or numerical methods.

We study whether it is necessary to design diverse role prompts for multi-agent collaboration. Table 7 shows the experiment results. In the single role setting, all agents are AI assistants. In the diverse role setting, for every question, agent roles are randomly selected from the above 5 roles. The results illustrate that our method with the same role prompt underperforms that with diverse role prompt, highlighting the cruciality of diverse role specification in multi-agent collaboration.

<table><tr><td></td><td>GSM8K</td><td>SVAMP</td></tr><tr><td>Single Agent</td><td>75.33</td><td>77.27</td></tr><tr><td>Multi Agent (single role)</td><td>81.80</td><td>84.80</td></tr><tr><td>Multi Agent (diverse role)</td><td>82.80</td><td>85.40</td></tr></table>

Table 7: Effects of diverse role specification on GSM8K and SVAMP.

## E Case Study

The process unfolds across three stages, each illustrated in separate tables: Table 8 illustrates the first “creation” stage. Table 9 and Table 10 both show the second “review” stage. Finally, the “revision” stage is detailed in Table 11.

<table><tr><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="2">Q: Elise has been selling her Dad's collection of 250 books for three years. Each book sells at 20$, and shesold twice as many books in the first year as she has sold in the current year. There are currently 50 unsoldbooks, and her sales number this year is 45. What's the total amount of money she earned in the second year?(later denoted as Question)</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1">Example</td><td colspan="1" rowspan="4">A: If her sales in the current year are 45, she sold $4 5 ^ { * } 2 = * 4 5 ^ { * } 2 { = } 9 0 { > } 9 0$ books in the first year. The totalnumber of books sold in the first and current year is $9 0 + 4 5 = { \scriptscriptstyle 4 9 0 + 4 5 = 1 3 5 } { \scriptscriptstyle 3 5 1 3 5 }$  The total number ofbooks sold in the second year is 250 of the original number of books - 135 sold books - 50 unsold books = $\ll 2 5 0  – 1 3 5 – 5 0 { = } 6 5 { \gg } 6 5$ books. If each book sells at 20$, then she earned $2 0 ^ { * } 6 5 = \mathbb { \ S } \mathrm { \times } 2 0 ^ { \ast } 6 5 \mathrm { = } 1 3 0 0 \mathrm { \gg } 1 3 0 0$ in thesecond year #### 1300</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="2">Q: Can you solve the following math problem? {Question} Explain your reasoning. Your final answershould be a single numerical number, in the form \boxed{answer}, at the end of your response.</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="10">A: Let's break down the information given: Elise sold twice as many books in the first year as she has sold inthe current year. If she sold 45 books this year, then she sold $4 5 / 2 = 2 2 . 5$ books in the first year. However,since we cannot have half a book, we'll assume that she actually sold 23 books in the first year. There arecurrently 50 unsold books, which means that she has sold a total of $2 5 0 - 5 0 = 2 0 0$ books in the past threeyears. If she sold 23 books in the first year and 45 books this year, then she sold a total of $2 3 + 4 5 = 6 8$ booksin the past two years. To calculate the number of books she sold in the second year, we subtract the numberof books sold in the first year and this year from the total number of books sold in the past two years: 68 - 23 - $4 5 = 6 8 - 6 8 = 0 .$ Therefore, Elise did not sell any books in the second year. Since each book sells for $20,she did not earn any money in the second year. Thus, the total amount of money she earned in the secondyear is \boxed{0}. (later denoted as Answer A)</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1">Agent A</td></tr><tr><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="1">y</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="2">Q: Can you solve the following math problem? {Question} Explain your reasoning. Your final answershould be a single numerical number, in the form \boxed{answer}, at the end of your response.</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="9">A: Let's start by finding out how many books Elise sold in the first year. We are given that she sold twice asmany books in the first year as she has sold this year. Since she has sold 45 books this year, she sold $2 ^ { * } 4 5 =$ 90 books in the first year. In the first year, she sold a total of 90 books $* { \mathfrak { S } } 2 0 = { \mathfrak { S } } { \mathfrak { e } } 9 0 { \dot { * } } 2 0 { = } 1 8 0 0 { \gg } 1 8 0 0$ Nowlet's find out how many books Elise sold in the current year. We are given that she sold 45 books this yearand there are currently 50 unsold books. Therefore, in the current year, she had sold a total of 45 books + 50unsold books = 95 books. Since we know Elise sold a total of 250 books over three years, and we alreadycalculated the number of books sold in the first and current years, we can find out the number of books shesold in the second year. The total number of books sold in the second year is 250 books - 90 books - 95 books= 65 books. We know that each book sells for $20, so in the second year, Elise earned a total of 65 books * $\$ 20=8 * 65 ^ { * } 20 = 1300 * 1300$  Therefore, Elise earned a total of $1300 in the second year. Our final answer is\boxed{1300}. (later denoted as Answer B)</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1">Agent B</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td><td colspan="1" rowspan="2">Q: Can you solve the following math problem? {Question} Explain your reasoning. Your final answershould be a single numerical number, in the form \boxed{answer}, at the end of your response.</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="3" rowspan="4">A: Let's set up an equation to represent the information given. Let's call the number of books Elise sold inthe current $\mathrm { y e a r ~ } " \mathrm { x } " .$ According to the problem, she sold twice as many books in the first year as she has soldin the current year, so she sold 2x books in the first year. In the three years, Elise sold a total of 250 books,and since she sold x books in the current year and 2x books in the first year, she sold $2 5 0 - ( \mathrm { x } + 2 \mathrm { x } ) = 2 5 0 - 3 \mathrm { x }$ books in the second year. We are given that there are currently 50 unsold books, which means that the totalAgent C  number of books sold is $2 5 0 - 5 0 = 2 0 0 .$ Since the total number of books sold in the second year is equalto $2 0 0 - \left( \mathrm { x } + 2 \mathrm { x } \right)$ , we can set up the equation: $2 0 0 - 3 \mathrm { x } = 4 5$ Simplifying this equation, we get: $- 3 x = - 1 5 5 .$ Dividing by -3 on both sides, we find: $\mathbf { \bar { x } } = 1 5 5 / 3$ Therefore, Elise sold 155/3 books in the current year. Now,to find the total amount of money she earned in the second year, we need to multiply the number of bookssold in the second year by the price per book. The price per book is $20, and the number of books sold in thesecond year is $2 0 0 { \overset { \cdot } { \circ } } \left( \mathbf { x } + 2 \mathbf { x } \right) = 2 0 0 { \overset { \cdot } { \circ } } 3 \mathbf { x } = 2 0 0 - 3 ( \mathbf { \hat { 1 } } 5 5 / 3 ) = 2 0 0 - 1 5 5 = 4 5$ books. So, Elise earned a total of $4 5 * \ S 2 \bar { 0 } = \ S { \ll } 4 5 ^ { * } 2 0 { = } 9 0 0 { > } 9 0 0$ in the second year. Therefore, Elise earned a total of $900 in the second year.Answer: \boxed{900}. (later denoted as Answer C)</td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="2" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="4">Agent A</td><td colspan="4" rowspan="1">Q: Here is a solution from another agent: {Answer B} Please examine this agent's reasoning process step bystep and offer feedback on its reasoning. You can rate your confidence in your feedback on a scale from 1-10,where 10 indicates the highest level of confidence.</td></tr><tr><td colspan="4" rowspan="1">A: I would rate my confidence in this agent's reasoning process as a 9. The agent's solution is correct, andthey have provided a clear and logical breakdown of the problem. They correctly calculated that Elise sold90 books in the first year, based on the information given, and found that she sold a total of 95 books inthe current year. Subtracting this from the total number of books sold over the three years, they correctlyfound that Elise sold 65 books in the second year. Finally, they correctly multiplied this number by theprice per book to find that Elise earned $1300 in the second year. Overall, the agent's reasoning process iswell-explained and logical. (later denoted as Feedback $\mathsf { A } \to \mathsf { B } )$ </td></tr><tr><td colspan="4" rowspan="1">Q: Here is a solution from another agent: {Answer C} Please examine this agent's reasoning process step bystep and offer feedback on its reasoning. You can rate your confidence in your feedback on a scale from 1-10,where 10 indicates the highest level of confidence.</td></tr><tr><td colspan="4" rowspan="2">A: I would rate my confidence in this agent's reasoning process as a 7. The agent correctly set up the equationto represent the information given, relating the number of books sold in the current year to the number ofbooks sold in the first and second years. They correctly determined that the total number of books sold is 200,based on the information given about unsold books. However, the agent made a mistake in their calculationof the number of books sold in the second year. They incorrectly substituted the value of x into the equationand found that Elise sold 45 books in the second year. This is inconsistent with the information provided,which states that Elise sold 45 books in the current year, not the second year. Therefore, the calculation of thetotal amount of money earned in the second year, $900, is incorrect. Overall, the reasoning process is mostlycorrect, but there is a mistake in the calculation of the number of books sold in the second year. (later denotedas Feedback $\mathsf { A } \to \mathsf { C } )$ </td></tr><tr><td colspan="4" rowspan="1"></td></tr><tr><td colspan="1" rowspan="2"></td><td colspan="4" rowspan="2">Q: Here is a solution from another agent: {Answer A} Please examine this agent's reasoning process step bystep and offer feedback on its reasoning. You can rate your confidence in your feedback on a scale from 1-10,where 10 indicates the highest level of confidence.</td></tr><tr><td colspan="3" rowspan="1">ctor</td></tr><tr><td colspan="5" rowspan="2">Agent BA: I rate my confidence in my feedback as a 10. Feedback: The reasoning process provided by the otheragent is correct. Let's go through the steps of their solution: The agent sets up an equation to represent theinformation given, with $" \mathbf { X } "$ representing the number of books Elise sold in the current year. They correctlyrdetermine that Elise sold twice as many books in the first year as she has sold in the current year, so thenumber of books sold in the first year is 2x. The agent then uses the total number of books sold in the threeyears (250) and subtracts the number of books sold in the current year and the first year to find the number ofbooks sold in the second year, which is correctly represented as $2 5 0 - ( \mathrm { x } + 2 \mathrm { x } )$ . The total number of bookssold is given as 200 (250 - 50), and the agent correctly sets up the equation $2 0 0 - 3 \mathbf { x } = 4 5 $ to represent thenumber of books sold in the second year, with 45 being the number of books sold in the current year. Theagent solves the equation correctly, finding $\mathbf { \boldsymbol { x } } = 1 5 5 / 3$ as the number of books sold in the current year. Finally,the agent multiplies the number of books sold in the second year by the price per book ($20) to find the totalamount of money earned in the second year, which is correctly calculated as $4 { \dot { 5 } } * \ S 2 0 = \ S 9 0 0 .$ Therefore, theother agent's reasoning process is correct and provides a valid solution to the math problem. (later denoted asFeedback B → C)</td></tr><tr><td colspan="3" rowspan="1">O. Hrisy</td></tr></table>

Table 8: Stage 1: Create. Each agent independently constructs its own solution. The first row “Example” shows a question and its gold answer in GSM8K (Cobbe et al., 2021). The initial responses of Agent A and Agent C are wrong, and only Agent B is correct. The wrong answers and the critical wrong steps are in red, and the correct answer is in green.

Table 9: Stage 2 of Agent A and B: Review. Each agent provides reviews on the solutions of others. Agent A accurately assesses the answers of others and correctly identifies the primary error in Agent C’s solution. Conversely, while Agent B successfully points out the error of Agent A, it fails to pinpoint the error of Agent C. Incorrect feedback is in red, and the correct feedback and the accurately identified errors are in green.

![](images/288e38c74705e9cabad0fad08064b2b1b18220bdab62d394cbf660b377438b08.jpg)  
(a) Self-correct

![](images/9d8d3269817f8bf3175cfdd787be8a5d6dcbb1248aa32b2aaa17ff88a8887cf9.jpg)  
Figure 6: Comparison of the changes in answers on Penguins after self-correction and our collaboration method. No change: The answer remains unchanged; Correct→Incorrect: A correct answer is changed to an incorrect one; Incorrect→Correct: An incorrect answer is revised to a correct one; Incorrect→Incorrect: An incorrect answer is altered but remains incorrect.

<table><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="2">Q: Here is a solution from another agent: {Answer A} Please examine this agent's reasoning process step bystep and offer feedback on its reasoning. You can rate your confidence in your feedback on a scale from 1-10,where 10 indicates the highest level of confidence.</td></tr><tr><td colspan="1" rowspan="2"></td></tr><tr><td colspan="1" rowspan="4">A: The reasoning of the second agent is incorrect. Here's a breakdown of the errors: The assumption thatElise sold 23 books in the first year is incorrect. The problem states that she sold twice as many books in thefirst year as she has sold in the current year. Since she sold 45 books this year, it means she sold 45 * 2 = 90books in the first year. The calculation of the total number of books sold in the past two years is incorrect. Itshould be 90 (number of books sold in the first year) + 45 (number of books sold this year) = 135, not 68.The conclusion that Elise did not sell any books in the second year is incorrect. The problem does not provideexplicit information about the number of books sold in the second year, so we cannot assume it to be zero.As a result, the calculation of the money earned in the second year as $0 is also incorrect. Confidence infeedback: 10/10. (later denoted as Feedback C → A)</td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1">Agent C</td><td colspan="1" rowspan="3">Q: Here is a solution from another agent: {Answer B} Please examine this agent's reasoning process step bystep and offer feedback on its reasoning. You can rate your confidence in your feedback on a scale from 1-10,where 10 indicates the highest level of confidence.</td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="3">A: The reasoning of the third agent is correct. Here's a breakdown of their solution: They correctly calculatethat Elise sold 90 books in the first year, as she sold twice as many books as she did in the current year (45).They then correctly calculate the earnings from the first year by multiplying the number of books sold (90)</td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="1">number of books sold (90)</td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="4">by the price per book ($20), giving a total of $1800. They determine that Elise sold a total of 95 books inthe current year (45 books sold + 50 unsold books). They correctly calculate the number of books sold inthe second year by subtracting the number of books sold in the first and current years (250 books - 90 books- 95 books = 65 books). They calculate the earnings from the second year by multiplying the number of</td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td colspan="1" rowspan="1"></td><td colspan="1" rowspan="2">books sold in the second year (65) by the price per book ($20), giving a total of $1300. The agent's reasoningprocess is sound, and they correctly follow through the steps to arrive at the correct answer. Confidence infeedback: 10/10. (later denoted as Feedback C → B)</td></tr><tr><td colspan="1" rowspan="1"></td></tr><tr><td rowspan="2">Agent A</td><td colspan="2">Q: Here are the feedbacks for your solution from the above two agents: One agent feedback: {Feedback B → A} One agent feedback: {Feedback  ${ \mathsf { C } }  { \mathsf { A } }  \mathsf { \} }$  Using other agents' solutions and feedbacks as additional information, can you provide your answer to the math problem? The original math problem is {Question} Your final answer should be a single numerical number, in the form \boxed{answer}, at the end of your response.</td></tr><tr><td colspan="2">A: Based on the corrected information from the feedback received, let's analyze the problem again: Elise sold twice as many books in the first year as she has sold in the current year. Since she sold 45 books this year, the number of books sold in the first year is  $2 * 4 5 = 9 0$  books. The total number of books sold in the past two years is 90 (number of books sold in the first year) + 45 (number of books sold this year) = 135 books. The total number of books sold in the three years is 250 (total number of books) - 50 (unsold books) = 200 books. Therefore, the number of books sold in the second year is 200 (total number of books sold in two years) - 135 (number of books sold in the past two  $\mathrm { y e a r s } ) = 6 5$  books. Since each book sells for $20, the total amount of money Elise earned in the second year is 65 books  $\ast \mathfrak { S } 2 0 = \mathfrak { S } 1 3 0 0$  Therefore, the total amount of money Elise earned in the second year is \boxed{1300}.</td></tr><tr><td rowspan="2">Agent B</td><td colspan="2">Q: Here are the feedbacks for your solution from the above two agents: One agent feedback: {Feedback A → B} One agent feedback: {Feedback  $C \  \ \mathsf { B } \}$  Using other agents' solutions and feedbacks as additional information, can you provide your answer to the math problem? The original math problem is {Question} Your final answer should be a single numerical number, in the form \boxed{answer}, at the end of your</td></tr><tr><td colspan="2">response. A: Based on the correct reasoning and solutions provided by the other agents, the total amount of money Elise earned in the second year is $1300. Therefore, the answer is \boxed{1300}.</td></tr><tr><td></td><td colspan="2">Q: Here are the feedbacks for your solution from the above two agents: One agent feedback: {Feedback A → C} One agent feedback: {Feedback  $\textsf { B } \to \textsf { C } \}$  Using other agents' solutions and feedbacks as additional</td></tr><tr><td rowspan="2">Agent C</td><td colspan="2">information, can you provide your answer to the math problem? The original math problem is {Question} Your final answer should be a single numerical number, in the form \boxed{answer}, at the end of your response.</td></tr><tr><td colspan="2">A: Based on the correct reasoning provided, the total amount of money Elise earned in the second year is $1300. Therefore, the final answer is \boxed{ 1300}.</td></tr></table>

Table 10: Stage 2 of Agent C: Review. Agent C accurately assesses the answers of others and correctly identifies the primary error in Agent A’s solution. The correct feedback and the accurately identified errors are in green.

Table 11: Stage 3: Revise. Upon receiving peer reviews, agents revise their initial solutions. All agents arrive at the correct answer.