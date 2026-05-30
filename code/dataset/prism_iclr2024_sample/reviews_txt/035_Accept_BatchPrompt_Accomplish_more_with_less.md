# BatchPrompt: Accomplish more with less

OpenReview ID: Agyicd577r
Decision: Accept

## Abstract
The ever-increasing token limits of large language models (LLMs) have enabled long context as input. Many LLMs are trained and fine-tuned to perform zero/few-shot inference using instruction-based prompts. Prompts typically include a detailed task instruction, several examples, and a single data point for inference. This baseline is referred to as “SinglePrompt” in this paper. In terms of token count, when the data input is small compared to instructions and examples, this results in lower token utilization, compared with encoder-based models like fine-tuned BERT. This cost inefficiency, affecting inference speed and compute budget, counteracts many of the benefits that LLMs offer. This paper aims to alleviate this problem by batching multiple data points in each prompt, a strategy we refer to as “BatchPrompt”. We improve token utilization by increasing the “density” of data points, however, this cannot be done naively. Simple batching can degrade performance, especially as batch size increases, and data points can yield different answers depending on their position within a prompt. To address the quality issue while retaining high token utilization, we introduce Batch Permutation and Ensembling (BPE) for BatchPrompt – a simple majority vote over repeated permutations of data, that recovers label quality at the cost of more token usage. To counterbalance this cost, we further propose Self-reflection-guided EArly Stopping (SEAS), which can terminate the voting process early for data points that the LLM handles confidently. Our comprehensive experimental evaluation demonstrates that BPE + SEAS can boost the performance of BatchPrompt by a striking margin on a range of popular NLP tasks, including question answering (Boolq), textual entailment (RTE), and duplicate questions identification (QQP). This performance is even competitive with/higher than single-data prompting (SinglePrompt), while using far fewer LLM calls and input tokens. At batch size 32, our BatchPrompt + BPE + SEAS uses 15.7% the number of LLM calls, and achieves: Boolq accuracy 90.6% → 90.9% with 27.4% tokens, QQP accuracy 87.2% → 88.4% with 18.6% tokens, RTE accuracy 91.5% → 91.1% with 30.8% tokens. We hope our simple yet effective approach will shed light on the future research of large language models. Code: github.com/microsoft/BatchPrompt

## Reviews

### Review 1
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper proposes an efficient prompting technique, BatchPrompt, which batches the input samples into a single prompt to improve the token utilization. While simply batching samples leads to a significant performance drop, this paper introduces Batch Permutation and Ensembling (BPE) and Self-reflection-guided Early Stopping (SEAS) to maintain the generation quality. BPE permutes the data order in each batch and uses majority voting to get the final prediction. SEAS allows early stopping of voting when LLM is confident about the sample. Experiments on some language understanding tasks show BPE+SEAS boosts BatchPrompt performance to be competitive with single-data prompting while using far fewer tokens and API calls.

#### Strengths
- The idea of BatchPrompt is simple and practical. Using ensemble and early stopping techniques BPE and SEAS to improve performance is novel to me.
- The paper is clearly written and easy to follow.
- The work focuses on the important problem of improving the prompting efficiency of LLM inference.

#### Weaknesses
- The proposed method adds some hyperparameters like batch size and voting rounds for configuration. More analysis could be provided on computational efficiency tradeoffs and how to determine the good hyperparameters
- The experiments are conducted on language understanding tasks. It would be helpful to evaluate the method on more diverse tasks, e.g. reasoning, knowledge-intensive QA, and creative writing.

#### Questions
- How to determine good hyperparameters like batch size and voting rounds for BatchPrompt? More analysis could be provided on computational efficiency tradeoffs.
- It seems that gpt-3.5-turbo suffers from performance degradation when using BatchPrompt, while gpt-4 does not. Is this caused by the model scale? I believe it is helpful to add an analysis of BatchPrompt on the LLaMA series with different model sizes.
- It would be helpful evaluate the method on more diversed tasks, e.g. reasoning, knowledge-intensive, creative writing tasks. Does the type or difficulty of the instruction affect the performance of BatchPrompt?

### Review 2
Rating: 8: accept, good paper
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The paper proposes a method for batching prompts.  Larger batch size generally improve throughput, but degrade performance.  This paper introduced some suggestions (voting rounds and SEAS) to reduce the performance degradation.

#### Strengths
The paper advocates the use of batching for prompting, and may be successful in setting a new trend in that direction.

#### Weaknesses
I worry about running so many experiments.  The plots in Figure 3 suggest that there are patterns to the results, but even so, if we run lots and lots of experiments and report the best values, the best value could be the result of randomness.

On the other hand, to make the case for trends, we may need to run even more experiments over more benchmarks, models, batch sizes and so on.

It would be nice to fit some kind of smooth regression to the results to help with interpretation.  Can you say how performance depends on batch size, voting rounds and model?  An ANOVA would help address concerns above with running so many experiments.

#### Questions
Can you say more clearly up front that large batches improve throughput, but would degrade performance.  To address performance, you introduce voting rounds and SEAS.  This should also be stated clearly in the conclusions.

The discussion of the results should address the comments above about interpretation.  The ablation studies show that voting rounds are effective.  But it is hard to see the relation between batch size and performance.  It looks like batch size still reduces performance, even with voting rounds and SEAS.  Is that right?

### Review 3
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
For NLP tasks where each data point for inference is not necessarily lengthy, the token count for instructions and few-shot examples in the prompt may be considerably larger than that of the data point, resulting in lower token-resource utilization. This paper try to alleviate the preceding problem by batching multiple data points into a single prompt, a prompting strategy we refer to as “BatchPrompt”. This strategy increases the “density” of data points, which in turn leads to improved token utilization, which shows promising fulture.

#### Strengths
1.	Batchprompt could highly improve token-resource utilization
2.	BPE could effectively It can effectively reduce the error rate caused by the different position in a batch.
3.	SEAS could effectively reduce the amount of unnecessary calculations

#### Weaknesses
1.	It seems that each item in the new batch (with only one prompt) could not be computed parallelly as original. Whether it will increase the time cost? It might be better to add time and flops metrics in the experiments.
2.	I think the “batchprompt” could be used in both training and test phases, right?
3.	In BPE, the weight for confidence is directly 1. What about to generate the weights scores directly by the LLM without whether confident?

#### Questions
Please see the weakness.

### Review 4
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The paper describes a method to improve resource utilization by increasing the 'density' of user query tokens using batching the queries. User queries exhibit lower token utilization compared to the system prompts and/or few shot examples that goes with the query. Authors point out that this is not cost efficient and the 'batchprompt' method requires less LLM calls and better user query token utilization (saving the overall numbers of tokens in a batch which in effect is more cost-efficient). 

Batch prompting makes the LLM generation task n times harder for batch size n since the LLM needs to generate n outputs corresponding the n packed queries. Authors conduct experiments and show that this significantly degrades performance, and the order of the packed queries also significantly impact the performance. 

Authors develop a batch permutation and ensembling method (to utilize voting from repeated permutations) - this slightly increases the token count and increases the LLM calls (still much less compared to single prompt inference) however improves the performance. Further improvement is realized with 'self reflection guided early stopping (SEAS) scheme) where the generator is also asked to provide the confidence of the result and using rules, the system stops the voting procedure early.

Authors have performed experiments on 3 datasets (yes/no question answering, entailment, paraphrase detection) and shown that with a batch size of 32, and using BPE and SEAS. the accuracies on 3 datasets do not degrade (improve slightly).

#### Strengths
- Authors propose a robust method that uses larger batch size, more voting rounds (eg. 5+) and a self-reflection guided early stopping approach.

- The early stopping method also uses a pruning strategy to prune away confident predictions leaving fewer/harder samples for later
rounds. In the process, the harder samples might also become easier to predict, due to smaller effective batch size in later rounds. 

- via experiments, authors show that voting is most successful when the baseline performance is strong (for example, gpt4 vs. gpt3.5)

#### Weaknesses
- Authors chose small number of tasks (only 3 simple tasks (yes/no QnA, paraphrase detection and entailment detection) -> these tasks may be too easy for gpt3.5 and gpt4 systems 

- Results are shown using few experiments (~300 dataset queries each for the 3 datasets); typically a validation on more tasks and more datasets would have helped get a more confident understanding of the approach. 

- this is a nice applied research paper with good results and a principled approach for improving cost efficiency, however there are many variables to unpack (quality and length of tasks, mixing different types of instructions, performance on novel datasets not seen by the LLMs, solving position bias discrepancy via BPE with more experiments and results, role of prompt variations on the results, etc)

#### Questions
- All tasks are very short answer type tasks, using tasks that generate longer answers might be very hard to experiment using the batchprompt approach. Couldn't see a discussion on this topic in the paper. Thoughts?

- it is not clear how this system would be used with all its advantages in a deployment scenario - batching real world prompts with very different instructions might have unpredictable behavior, any thoughts?

## Meta Reviews

### Meta Review 1
This paper proposes a simple yet novel approach to improving the prompting efficiency of LLM inference based on Batch Permutation and Ensembling (BPE), a majority vote approach that improves labelling quality through repeatedly permutating data positions in a batch at the price of more token usage, and Self-reflection-guided EArly Stopping (SEAS) to counterbalance the additional token usage caused by the voting process. In the words of one of the reviewers, the authors present “good results and a principled approach” towards demonstrating the effectiveness of their method. A key weaknesses is the need for more rigorous evaluations on more diverse sets of tasks; however, the authors have presented additional results on other datasets as part of the rebuttal. The authors should ensure that they address all of the reviewers’ comments (and e.g., not only add raw results but thoroughly describe all new results on additional datasets) and run additional experiments as needed (e.g., ANOVA to facilitate interpretation). The authors should also ensure they thoroughly proofread their paper. 

Other comments:
It is not clear what the authors mean by “Data containing sensitive content cannot be used with gpt-3.5” — please clarify in the paper. Also, they might want to consider a different abbreviation for their first method as ‘BPE’ is already used in the literature (Byte-Pair Encoding).

## Decisions

Decision: Accept (poster)
