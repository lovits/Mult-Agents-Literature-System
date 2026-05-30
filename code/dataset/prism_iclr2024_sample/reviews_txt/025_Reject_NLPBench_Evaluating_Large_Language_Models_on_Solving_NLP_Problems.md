# NLPBench: Evaluating Large Language Models on Solving NLP Problems

OpenReview ID: fpYIlzOpIA
Decision: Reject

## Abstract
Recent developments in large language models (LLMs) have shown promise in enhancing the capabilities of natural language processing (NLP). Despite these successes, there remains a dearth of research dedicated to the NLP problem-solving abilities of LLMs. To fill the gap in this area, we present a unique benchmarking dataset, NLPBench, comprising 378 college-level NLP questions spanning various NLP topics sourced from Yale University's prior final exams. NLPBench includes questions with context, in which multiple sub-questions share the same public information, and diverse question types, including multiple choice, short answer, and math. Our evaluation, centered on LLMs such as GPT-3.5/4, PaLM-2, and LLAMA-2, incorporates advanced prompting strategies like the chain-of-thought (CoT) and tree-of-thought (ToT). Our study reveals that the effectiveness of the advanced prompting strategies can be inconsistent, occasionally damaging LLM performance, especially in smaller models like the LLAMA-2 (13b). Furthermore, our manual assessment illuminated specific shortcomings in LLMs' scientific problem-solving skills, with weaknesses in logical decomposition and reasoning notably affecting results.

## Reviews

### Review 1
Rating: 5: marginally below the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
The authors develop a new benchmark dataset (NLPBench) to evaluate the large language models for solving NLP problems. NLPBench comprises 378 college-level NLP questions (with and without context) spanning various NLP topics sourced from some University's prior final exams. NLPBench was evaluated on different LLMs such as GPT-4, PaLM-2, and LLAMA-2 using advanced prompting strategies including chain-of-thought (CoT) and tree-of-thought (ToT) and different decoding strategies such as self-consistency. The results show that NLPBench illuminates specific shortcomings in LLMs’ scientific problem-solving skills, with weaknesses in logical decomposition and reasoning notably affecting performance.

#### Strengths
1. Introduces a new dataset that challenges the current state-of-the-art prompting strategies and which is useful in evaluating the performance of LLMs.

2. The paper is well-written and easy to follow.

3. The authors carried out extensive experiments and evaluations that included recent prompting approaches and LLMs.

#### Weaknesses
In general, NLPBench is useful, but I think there are some clarities on how it was collected that are missing:

1. How did you get access to the final exams included in the dataset?  How do you ensure that these exams were not already online and that some recent models like GPT-4 have already included them in their training dataset? It was not clear from the paper how you checked that.  You mentioned that you curate questions that are not readily accessible online and couldn’t be easily extracted or transformed into text, but how do you measure that specific content cannot be easily extracted or transformed into text? what reliable techniques did you use to do that? 

2. In what years these final exams were given? This information might help in the development of future related datasets. 

3. In the data selection process, you mentioned that you selected 400 questions out of 1000 total questions, what were the criteria? Was it a random selection?

4. The dataset size looks small, why in Table 6, was not there any comparison for the NLPBench size to other benchmarks?

5. The very closely related benchmark (SciBench) also includes math problems, did you check if NLPBench's math-related problems are not also in SciBench? I did not see this evaluation in the paper.

6. How many expert human annotators were involved in the dataset processing?

**Minor:**
Some typos: 
- Page 3 in the paragraph that describes the complex structure: multi-tern -> multi-tern
- Page 4: zero-shot and few-shot(FS+ToT, FS+ToT) -> (ZS+ToT, FS+ToT)

#### Questions
- How many universities were included in the data collection?
- For other questions, please check the weakness section.

### Review 2
Rating: 5: marginally below the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
The authors propose a new LLM benchmarking dataset consisting of 378 questions collected from Universities’ NLP final exams with short-answers,  multiple-choice questions, math questions with step-by-step solutions. Some questions come with a context information. Different LLMs (GPT-3.5/4, PaLM-2, and LLAMA-2) are benchmarked on the dataset with different prompting strategies with a combination of zero-shot, few-shot and chain of thought (CoT) and tree of thought (ToT). The experimental results show that prompting strategies such as can reduce performance, in particular for small size models. The evaluation shows LLM limitations in reasoning, logical decomposition.

#### Strengths
- This work aim to expand the scope of LLM benchmarking and address new perspectives by contributing new datasets and benchmarking scenarios
- The evaluation includes both close and open models. It is important to understand the gap between these model types

#### Weaknesses
- The size of the dataset is relatively small and might limit the conclusion drawn from the results.
- The gap filled by the proposed by introducing NLPBench (Table 6) is rather narrow and needs stronger justification. It covers a broader context than the claimed main focus of NLP-related topics such as Math. 
- The analysis conclusion are mostly known, such as small LLMs have inconsistent results with advanced prompting. LLM limitation on problem-solving tasks.

#### Questions
- How open questions have been evaluated ? The paper mentions only human annotation of errors.
- Under Inaccessibility, details are missing. How did you make sure that the questions are not part of other datasets ? What are risks of contamination by LLM training data  ?
- I expected that the top-3 models is including PalM but in 4.2, Llama-2 was taken instead. Is there a justification for this choice ?

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
This paper presents a benchmark dataset for NLP-related questions for LLMs to answer. The collected dataset, NLPBench, consists of 378 college-level NLP questions and various LLMs are tested on this benchmark. In addition, this paper also compares different prompting strategies, but finds out that the results are not consistent with the "advancement" of the technique.

#### Strengths
* Interesting angle and scope for LLM evaluation
* Experiments of the effectiveness of different prompting strategies under this task

#### Weaknesses
* The scope of the evaluation is quite limited
* The dataset is small and relatively the evaluation cost is high

#### Questions
* Could this approach be adapted to other areas or domains? Would be nice to discuss about it and also the transfer cost.

## Meta Reviews

### Meta Review 1
This paper presents a dataset of final exam problems and answers in the university classes of natural language processing (NLP). While. this must have taken a lot of work and the resulting dataset is useful, it is not sufficient to warrant a publication at ICLR. For it to have scientific contribution, I would like to see an in-depth discussion about how the NLP problems and answers are different, from an LLM perspective, from the physics and other science questions in the SciBench. Without that discussion, it is just adding another dataset. Granted, benchmark datasets are necessary in advancing the field, but to be a full paper at ICLR, I think more insights about the dataset is needed, so that future researchers can learn from this experience in building more diverse and unique benchmark datasets.

## Decisions

Decision: Reject
