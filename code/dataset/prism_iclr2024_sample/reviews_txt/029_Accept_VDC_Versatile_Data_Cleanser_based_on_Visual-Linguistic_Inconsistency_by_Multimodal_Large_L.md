# VDC: Versatile Data Cleanser based on Visual-Linguistic Inconsistency by Multimodal Large Language Models

OpenReview ID: ygxTuVz9eU
Decision: Accept

## Abstract
The role of data in building AI systems has recently been emphasized by the emerging concept of data-centric AI. Unfortunately, in the real-world, datasets may contain dirty samples, such as poisoned samples from backdoor attack, noisy labels in crowdsourcing, and even hybrids of them. The presence of such dirty samples makes the DNNs vunerable and unreliable.
Hence, it is critical to detect dirty samples to improve the quality and realiability of dataset. 
Existing detectors only focus on detecting poisoned samples or noisy labels, that are often prone to weak generalization when dealing with dirty samples from other fields.
In this paper, we find a commonality of various dirty samples is visual-linguistic inconsistency between images and associated labels. 
To capture the semantic inconsistency between modalities, we propose versatile data cleanser (VDC) leveraging the surpassing capabilities of multimodal large language models (MLLM) in cross-modal alignment and reasoning.
It consists of three consecutive modules: the visual question generation module to generate insightful questions about the image; the visual question answering module to acquire the semantics of the visual content by answering the questions with MLLM; followed by the visual answer evaluation module to evaluate the inconsistency.
Extensive experiments demonstrate its superior performance and generalization to various categories and types of dirty samples.
The code is available at [https://github.com/zihao-ai/vdc](https://github.com/zihao-ai/vdc).

## Reviews

### Review 1
Rating: 6: marginally above the acceptance threshold
Confidence: 5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.

#### Summary
The paper proposes a general "label" cleaning/filtering approach and aims to detect three types of errors: "poisoned samples", "noisy samples", and "hybrid dirty samples". The paper takes advantage of the exceptional capability of multimodal large language model (MLLM) and casts the error detection problem into a three-step scoring pipeline. The pipeline consists of 1) visual question generation, 2) visual question answering, and 3) visual answer evaluation. The main argument is that, unlike prior arts, the proposed approach can detect all three types of label errors and achieves better performance in common benchmarks, including ImageNet-100 and CIFAR-10.

#### Strengths
- The proposed method leverages the recent trend of MLLM to the label error detection literature
- The proposed method is training-free

#### Weaknesses
- The empirical comparison is not fair.
    - The propose approach is using instruct-BLIP (larger network trained on larger dataset), while the baseline is usually using less-expressive network trained on smaller datasets, e.g., CL is using ResNet-18 and trained on CIFAR dataset.
- The claim that the proposed method mitigates all three types of label noises is too strong.
    - The proposed approach is general, but so do other baselines. For example, SimiFeat-V leverages the feature similarity to detect noisy labels, which is also applicable to the scenario of “poisoned samples” as long as the feature extractor is trained on a poison-free dataset.

#### Questions
1. The name of “visual question generation” is confusing. From my understanding to the paper, there is no visual signal in this stage. Can the author confirm this?
2. What are the accuracy of each question?
    - Figure 2 shows the TRR of the general and label-specific questions. I am curious of what specific question is challenging for the instruct-BLIP. Is there any specific question that is always challenging to the instructBLIP and, therefore, removing those questions actually help the overall performance
3. Given that the method leverages a ensemble of the MLLM responses, instead of taking the average accuracy as score as in Eq. 4, does the author think that using techniques like label aggregation further improves the overall performances?
4. To make a fair comparison with other baselines, I suggest the authors could compare baselines with MLLM as well. For example, CL usually trains their classifier with leave-one-out or cross validation, which limits the size of the train dataset. However, one can also uses off-the-shelf classifier and apply CL on it.
5. Do the authors consider the data-leakage problem? Does the train dataset used to train the instruct-BLIP accidentally include the images in ImageNet or CIFAR? If so, how do accurately validate the performances?
6. Do the authors observe any accumulated error in the three-step pipeline? For example, the label-specific question include some noisy questions, which leads to poisoned answers in the second stage.

### Review 2
Rating: 6: marginally above the acceptance threshold
Confidence: 4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.

#### Summary
To address common noise data and backdoor attack problems in deep learning, the paper designed a data cleaning tool called VDC using a multimodal large language model. By designing generalized visual question answering questions and label-specific visual question answering questions, VDC can remove dirty and poisoned data from the dataset based on the inconsistency between the semantic of the obtained question results and the semantic of the image itself. The paper compared VDC with backdoor attack methods and noisy learning methods, demonstrating the effectiveness of VDC.

#### Strengths
+ The paper's approach is innovative, using popular multimodal large models to replace manual data cleaning work.
+ The paper unified the treatment of noisy data and poisoned data from backdoor attacks, which is relatively rare in previous research.
+ The paper's extensive experiments demonstrate the effectiveness of VDC in handling dirty data.

#### Weaknesses
+ The overall content of the paper seems to be more about using out-of-distribution methods to filter data, and perhaps this should be reflected in the accuracy of sample selection.
+ While the paper effectively addresses the issue of dirty data using MLLM, it seems to have a bias towards reporting the application of MLLM.

#### Questions
+ How is the threshold for excluding dirty data determined in the paper?
+ Has the author considered the scenario where MLLM itself serves as a detector rather than a data cleaner?
+ The paper's method relies heavily on MLLM, which in essence depends on more data and better labeling. Therefore, it may not be necessary to test models that use more clean data on small datasets, as this may go against the goal of advancing deep learning.

### Review 3
Rating: 6: marginally above the acceptance threshold
Confidence: 3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.

#### Summary
This paper proposes a working pipeline for noisy data detection. Compared with existing works focusing on noisy data or noisy label, this work aims to obtain an integrated framework to handle a comprehensive scenario including various noisy cases. Specifically, it terms it as visual-language inconsistency. Leveraging on several prompt techniques, the proposed framework achieves promising results compared with other baselines.

#### Strengths
1. Noisy or dirty data detection and cleaning is an important research topic. It is becoming even more critical for recent machine learning research since the data scale is always getting larger.
2. The proposed framework wisely utilize the advantage of current large-scale model to benefit the dirty data detection task.
3. Comprehensive empirical results show the framework superiority compared with other baselines.
4. The whole draft is in a good format for readers.

#### Weaknesses
1. I mainly concern about the technical contribution in this draft. The wise combination of prompting and dirty data detection is interesting. However, it still based on the visual-language understanding from large-scale pretrained model. Only based on such powerful tools relatively diminish this paper novelty. In addition, the key point of this paper is proposing an integrated detection pipeline instead of only focusing on sample or label. This point looks like a trivial combination which is incremental compared with previous settings. Is this setting practical and necessary for real-world scenarios?
2. Adding more recent published works for comparison may further help to support the paper contribution. Currently, only one or two baselines are published within past one year.

#### Questions
Please refer to the strengths and weakness for details. Even if I am concerning some points in weakness, I recognize other aspects of this paper mentioned in strengths. Overall, I lean to vote for an acceptance for now and I would like to check other reviewers' comments to discuss and make my final decision.

## Meta Reviews

### Meta Review 1
This paper considers the problem of noisy data detection. To solve this problem, an integrated framework is proposed to handle a comprehensive scenario. The proposed framework leverages several prompt techniques and achieves promising results.

**Strengths**
- The paper studies an important topic in the community.
- It is interesting to utilize the advantage of current large-scale model to benefit the dirty data detection task.
- Comprehensive experiments are provided to demonstrate the effectiveness of the proposed method over previous methods.
- The paper is well-written and easy to follow.

**Weaknesses**

Pre-rebuttal, many concerns are raised, including more fair comparison, clarification of the novelty, more experiments, etc. Most of them have been addressed in the rebuttal. But two concerns still remain.

- Lacks 1) analysis on why the proposed method is better, 2) in what scenario, the proposed method tends to work better, and finally 3) and why MLLM is preferred in this application.

- Make the using of foundations models more clear.

## Decisions

Decision: Accept (poster)
